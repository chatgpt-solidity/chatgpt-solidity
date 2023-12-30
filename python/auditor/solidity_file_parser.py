import re
import sys
from typing import Dict, List
from slither.slither import Slither
from slither.core.compilation_unit import SlitherCompilationUnit
from slither.core.declarations import Contract, FunctionContract, SolidityFunction
import subprocess

from python.auditor.fs import read_text_file
from python.auditor.solidity_utils import get_erc_numbers


def load_contract(contract_file, contract_name) -> Contract:
    slither = Slither(contract_file)
    cu = slither.compilation_units[0]
    auto_get_contract(cu)
    c = cu.get_contract_from_name(contract_name)[0]
    return c


def auto_get_contract(cu: SlitherCompilationUnit):
    derived_contracts = cu.contracts_derived
    for c in derived_contracts:
        print(c.name)
        for i in c.inheritance:
            print("inherit", i.name)
    print("auto_get_contract", derived_contracts, len(derived_contracts))


def get_all_pragma_solidity_versions(text: str) -> List[str]:
    prefix = "pragma solidity "
    return [
        line[len(prefix) : -1]
        for line in text.splitlines()
        if line.startswith("pragma solidity")
    ]


def get_minmatch_solidity_version(text: str) -> str:
    """A solidity file might contains multiple
    "pragma solidity x.x.x". Find the most lowest
    match one and return.

    Args:
        text (str): Solidity source file

    Returns:
        str: lowest solidity version that matched the pragma
        version constraint.
    """
    versions = get_all_pragma_solidity_versions(text)
    # if len(versions) == 1 and versions[0] == "^0.4.13":
    #     return "0.4.17"
    max = (0, 0, 0)
    for ver_str in versions:
        ver_str = ver_str.replace(" ", "")
        if ver_str[0] == "^" or ver_str[0] == "=":
            ver_str = ver_str[1:]
        elif ver_str[1] == "=":
            # match either >= or <=
            ver_str = ver_str[2:]

        [maj, minor, patch] = ver_str.split(".")[:3]
        match = re.search(r"\D", patch)  # Find the first non-number character
        if match:
            patch = patch[: match.start()]
        maj = int(maj)
        if minor == "*":
            minor = 0
        else:
            minor = int(minor)
        if patch == "*":
            patch = 0
        else:
            patch = int(patch)
        ver_tuple = (maj, minor, patch)
        if maj > max[0]:
            max = ver_tuple
        elif maj == max[0]:
            if minor > max[1]:
                max = ver_tuple
            elif minor == max[1]:
                if patch > max[2]:
                    max = ver_tuple

    res = f"{max[0]}.{max[1]}.{max[2]}"
    if max[1] == 4 and max[2] < 17:
        return "0.4.17"
    return res


def ensure_solc_version(text: str) -> str:
    """Make sure solc version is matched with
    the given solidity source file by using
    solc-select

    Args:
        text (str): Solidity source code
    """
    ver = get_minmatch_solidity_version(text)
    # Note: here the best way is to install & use
    # after comparing the solc current version and
    # min-require version from source code.
    # Too lazy to implement it.
    ret = subprocess.run(
        ["solc-select", "install", ver],
        stdout=subprocess.DEVNULL,
    )
    ret.check_returncode()
    ret = subprocess.run(
        ["solc-select", "use", ver],
        stdout=subprocess.DEVNULL,
    )
    ret.check_returncode()
    return ver


class SolFileParser:
    def __init__(
        self,
        contract_path: str,
        auto_solc=True,
        contract_name=None,
        cname2ercs: Dict = None,
    ) -> None:
        self._contract_path = contract_path
        self.solc_version = None
        if auto_solc:
            text = read_text_file(contract_path)
            self.solc_version = ensure_solc_version(text)

        slither = Slither(contract_path)
        cu = slither.compilation_units[0]
        self.contracts_ercs: Dict[Contract, List[str]] = {}
        if not contract_name:
            inherited = {}
            for c in cu.contracts_derived:
                for inh in c.inheritance:
                    inherited[inh] = True
            for c in cu.contracts_derived:
                if c in inherited:
                    print(f"skip {c.name}, this is not final one")
                    continue
                if c.is_library:
                    continue
                if c.is_interface:
                    # print(f"skip interface {c.name}")
                    continue

                if c.name in cname2ercs:
                    ercs = cname2ercs[c.name]
                else:
                    ercs = get_erc_numbers(c)
                if ercs:
                    self.contracts_ercs[c] = ercs
        else:
            selected_contracts = cu.get_contract_from_name(contract_name)
            if len(selected_contracts) == 0:
                raise RuntimeError(
                    f"no contract '{contract_name}' found in file '{contract_path}'"
                )

            if len(selected_contracts) > 1:
                raise RuntimeError(
                    f"multiple contracts '{contract_name}' found in file '{contract_path}'"
                )

            if contract_name in cname2ercs:
                ercs = cname2ercs[contract_name]
            else:
                ercs = get_erc_numbers(selected_contracts[0])
                print("!!! ", ercs)
            if ercs:
                self.contracts_ercs[c] = ercs
            else:
                raise RuntimeError(
                    f"contracts '{contract_name}' does not implement any ERC in file '{contract_path}'"
                )

        # for c, ercs in self.contracts_ercs.items():
        #     print(f"Found: {c.name} with ERCs: {ercs}")

    def no_contracts_with_erc(self) -> bool:
        return len(self.contracts_ercs) == 0
