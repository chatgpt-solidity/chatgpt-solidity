import os
import shutil
import sys
from typing import Dict, List, Tuple
from auditor.fs import read_json_file, read_text_file, write_text_file
from auditor.solidity_file_parser import SolFileParser
from auditor.solidity_utils import (
    find_all_callees,
    get_functions_to_check,
    get_public_state_var_sigs,
    is_function_overrided_by_state_variable,
    slithir_funcs_to_text,
)
import json
from glob import glob


class Question:
    def __init__(self, group) -> None:
        self.group = group


class JsonObjectWrapper:
    def __init__(self, data=None) -> None:
        self.data = data if data is not None else {}

    def dump_to_file(self, filepath):
        with open(filepath, "w") as file:
            json.dump(self.data, file, indent=4)

    def load_from_file(self, filepath):
        with open(filepath, "r") as file:
            self.data = json.load(file)


class ContractMetadata(JsonObjectWrapper):
    def __init__(self, data=None) -> None:
        super().__init__(data)

    def set_events(self, events):
        self.data["events"] = events

    def set_func2file(self, func2file):
        self.data["func2file"] = func2file

    def get_func2file(self):
        if not "func2file" in self.data:
            self.data["func2file"] = {}
        return self.data["func2file"]

    def get_func2attrs(self):
        if not "func2attrs" in self.data:
            self.data["func2attrs"] = {}
        return self.data["func2attrs"]

    def get_solc_version(self):
        return self.data["solc_version"]

    def set_func2attrs(self, f2a):
        self.data["func2attrs"] = f2a

    def set_solc_version(self, version):
        self.data["solc_version"] = version

    def set_ercs(self, ercs):
        self.data["ercs"] = ercs

    def set_name(self, name):
        self.data["name"] = name

    def set_state_var_sigs(self, sigs):
        self.data["state_var_sigs"] = sigs


def get_function_text_by_name(fname: str, cm: Dict) -> List[Tuple[str, str]]:
    """Get function(s) sig and content(including all the callees)

    Args:
        fname (str): name of the function
        cm (Dict): contract metadata

    Returns:
        List[Tuple[str, str]]: A list of (sig, content)
    """
    if "func2file" not in cm:
        return []
    results = []
    fprefix = fname + "("
    for name, text in cm["func2file"].items():
        if name.startswith(fprefix):
            results.append((name, read_text_file(text)))
    return results


def enumerate_functions(cm: Dict) -> List[Tuple[str, str]]:
    if "func2file" not in cm:
        return []

    results = []
    for name, path in cm["func2file"].items():
        fname = get_function_name(name)
        results.append((fname, path))
    return results


def get_function_name(sig: str) -> str:
    return sig[: sig.find("(")]


class SolFileFolderMetadata(JsonObjectWrapper):
    def __init__(self, data=None) -> None:
        super().__init__(data)

    def add_contract_metadata(self, cm):
        if "contracts" not in self.data:
            self.data["contracts"] = []

        self.data["contracts"].append(cm.data)

    def set_sol_file(self, sol_filepath):
        self.data["file"] = sol_filepath

    def get_sol_file(self):
        return self.data["file"]

    def get_contracts(self):
        return self.data["contracts"] if "contracts" in self.data else []


class SolFileFolder:
    def __init__(
        self,
        folder_path: str,
        sol_filepath: str,
        metadata: SolFileFolderMetadata = None,
    ) -> None:
        self.folder_path = folder_path
        self.sol_filepath = sol_filepath
        self.metadata = SolFileFolderMetadata() if metadata is None else metadata


def init_sol_file_folder(
    sol_file: str, output_folder: str, cname2ercs_dict
) -> SolFileFolder:
    sol_filename = os.path.basename(sol_file).split(".")[0]
    sol_file_folder = os.path.join(output_folder, sol_filename)
    cf_metadata_file = os.path.join(sol_file_folder, "metadata.json")
    if os.path.exists(cf_metadata_file):
        # print(f"metadata '{cf_metadata_file}' existed, skip")
        return SolFileFolder(
            sol_file_folder,
            sol_file,
            SolFileFolderMetadata(read_json_file(cf_metadata_file)),
        )

    cf = SolFileFolder(sol_file_folder, sol_file)
    os.makedirs(sol_file_folder, exist_ok=True)
    cf.metadata.set_sol_file(sol_file)
    ctext = read_text_file(sol_file)
    ctext_lines = ctext.splitlines(True)

    parser = SolFileParser(sol_file, cname2ercs=cname2ercs_dict)

    # we only need to slice functions for contract implemented for ERC
    for c, ercs in parser.contracts_ercs.items():
        cmeta = ContractMetadata()
        cmeta.set_solc_version(parser.solc_version)
        contract_folder = os.path.join(sol_file_folder, c.name)
        if os.path.exists(contract_folder):
            # remove old contract folder
            shutil.rmtree(contract_folder)
            print(f"[-] {contract_folder}")
        funcs_folder = os.path.join(contract_folder, "f")
        os.makedirs(funcs_folder, exist_ok=True)
        funcs = get_functions_to_check(c)

        # slice each function
        for f in funcs:
            if is_function_overrided_by_state_variable(f):
                # since function is overrided by a state variable
                # and there is no way to get Solidity version of the generated function
                # simply give up
                continue
            to_explore = set()
            to_explore.add(f)
            explored = find_all_callees(to_explore)
            text = slithir_funcs_to_text(explored, ctext_lines, True, False, True, True)
            func_filename = os.path.join(
                funcs_folder,
                f.full_name.replace("(", "_")
                .replace(")", "_")
                .replace(",", "_")
                .removesuffix("_")
                .removesuffix("_"),
            )

            if os.path.exists(func_filename):
                if f.contract_declarer == f.contract:
                    # should override
                    pass
                else:
                    print(
                        f"found overrided function {f.name} at {f.contract_declarer.name}, skip"
                    )
                    continue

            write_text_file(func_filename, text)
            cmeta.get_func2file()[f.signature_str] = func_filename
            cmeta.get_func2attrs()[f.signature_str] = {
                "is_view": f.view,
                "is_pure": f.pure,
            }

        state_var_sigs = get_public_state_var_sigs(c)
        cmeta.set_state_var_sigs(list(state_var_sigs))
        events = []
        for e in c.events:
            events.append(
                {
                    "name": e.name,
                    "params": [
                        {"type": str(p.type), "indexed": p.indexed} for p in e.elems
                    ],
                }
            )

        cmeta.set_ercs(ercs)
        cmeta.set_events(events)
        cmeta.set_name(c.name)
        cf.metadata.add_contract_metadata(cmeta)

    cf.metadata.dump_to_file(cf_metadata_file)
    return cf


def init_sol_file_folder_for_dataset(
    dataset: str, output_folder: str, cname2ercs_dict
) -> List[SolFileFolder]:
    # FIXME: only support single solidity file first, for solidity folder, need to merge first
    sol_files = glob(os.path.join(dataset, "*.sol"))
    num_of_files = len(sol_files)
    print(f"Found {num_of_files} single solidity files")

    # results = []
    for idx, f in enumerate(sol_files):
        try:
            cf = init_sol_file_folder(f, output_folder, cname2ercs_dict)
            print(f"[success] '{f}': {idx+1}/{num_of_files}")

            yield cf
            # results.append(init_sol_file_folder(f, output_folder))
        except Exception as ex:
            print(f"[error] '{f}': {ex}", file=sys.stderr)

    # return results
