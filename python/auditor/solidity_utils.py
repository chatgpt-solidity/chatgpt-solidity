import re
from typing import Dict, List, Set, Tuple
from slither.core.declarations import Contract, FunctionContract, SolidityFunction
import string
import random
from slither.core.variables.state_variable import StateVariable


def generate_random_string(length):
    letters = (
        string.ascii_letters + string.digits
    )  # includes both uppercase and lowercase letters, and digits
    result = "".join(random.choice(letters) for _ in range(length))
    return result


def find_all_callees(funcs: Set[FunctionContract]) -> Set[FunctionContract]:
    to_explore: List[FunctionContract] = []
    explored: Set[FunctionContract] = set()

    for f in funcs:
        to_explore.append(f)

    while len(to_explore) != 0:
        f = to_explore.pop(0)
        if f is None or f in explored:
            continue
        explored.add(f)
        if hasattr(f, "is_constructor") and f.is_constructor:
            to_explore.extend(f.contract.constructors)

        if isinstance(f, SolidityFunction):
            continue
        for c in f.all_internal_calls():
            to_explore.append(c)
        for c in f.all_library_calls():
            callee = c[1]
            to_explore.append(callee)

    return explored


def is_function_overrided_by_state_variable(f: FunctionContract):
    for variable in f.contract.state_variables_entry_points:
        if variable.name == f.name:
            return True

    return False


def slithir_funcs_to_text(
    funcs: Set[FunctionContract],
    filelines: List[str],
    with_comment=False,
    lstrip=True,
    with_contract_decl=False,
    with_state_var=False,
    mangle_localvar=False,
    mangle_statevar=False,
) -> str:
    explored_start_lines = set()

    # contract line regions, contract => array of (line/block string, line/block start number)
    # line number is used to sort the order
    contract2lines: Dict[Contract, List[Tuple[str, int]]] = {}

    # mapping from state variable and mangled name
    contract_state_var_replace_map: Dict[StateVariable, str] = {}

    for func in funcs:
        if not hasattr(func, "source_mapping") or not func.source_mapping.lines:
            # require, assert, etc..
            continue
        func_start_line = min(func.source_mapping.lines)
        if func_start_line in explored_start_lines:
            continue
        explored_start_lines.add(func_start_line)

        # make sure func belong to same contract are stick together
        if func.contract_declarer not in contract2lines:
            contract2lines[func.contract_declarer] = []

        lines: List = contract2lines[func.contract_declarer]

        func_begin_at_index = len(lines)
        # extract function body
        func_body_end = max(func.source_mapping.lines)

        func_lines: List[str] = []
        replace_map = {}
        if mangle_localvar:
            for v in func.local_variables:
                replace_map[v.name] = generate_random_string(random.randint(4, 10))
            for v in func.parameters:
                replace_map[v.name] = generate_random_string(random.randint(4, 10))

        for line_id in range(func_start_line, func_body_end + 1):
            line = filelines[line_id - 1]
            if lstrip:
                line = line.lstrip()
            if line.strip().startswith(("*", "/*", "//")) and not with_comment:
                continue

            if mangle_localvar:
                for key, value in replace_map.items():
                    line = re.sub(f"\\b{key}\\b", value, line)
                    # line = re.sub(f"`{key}`", '`'+value+'`', line)
            func_lines.append((line, line_id - 1))

        if mangle_statevar:
            state_vars = set(func.state_variables_read) | set(
                func.state_variables_written
            )
            for v in state_vars:
                if v not in contract_state_var_replace_map:
                    contract_state_var_replace_map[v] = generate_random_string(
                        random.randint(4, 10)
                    )

            replaced_lines = []
            for line, row in func_lines:
                for v in state_vars:
                    line = re.sub(
                        f"\\b{v.name}\\b", contract_state_var_replace_map[v], line
                    )
                replaced_lines.append((line, row))

            func_lines = replaced_lines

        lines.extend(func_lines)

        # extract function's comment if any
        if with_comment:
            if func.source_mapping.lines:
                curr = func_start_line - 2
                while curr >= 0:
                    curr_line = filelines[curr]
                    if curr_line == "\n" or curr_line.strip().startswith(
                        ("*", "/*", "//")
                    ):
                        curr -= 1
                        if lstrip:
                            curr_line = curr_line.lstrip()

                        for key, value in replace_map.items():
                            curr_line = re.sub(f"\\b{key}\\b", value, curr_line)
                        lines.append((curr_line, curr))
                    else:
                        break

        # add contract decl and state variable if any
        if with_state_var and not with_contract_decl:
            with_contract_decl = True

        if with_state_var:
            state_vars = set(func.state_variables_read) | set(
                func.state_variables_written
            )
            for v in state_vars:
                start_line = min(v.source_mapping.lines)
                if start_line in explored_start_lines:
                    continue
                explored_start_lines.add(start_line)

                # handle state variable decleration here
                if v.contract not in contract2lines:
                    contract2lines[v.contract] = []
                target_region = contract2lines[v.contract]

                for idx in v.source_mapping.lines:
                    # target_region.insert(0, filelines[idx - 1])
                    target_region.append((filelines[idx - 1], idx - 1))

                if with_comment:
                    if v.source_mapping.lines:
                        curr = start_line - 2
                        while curr >= 0:
                            curr_line = filelines[curr]
                            if curr_line == "\n" or curr_line.strip().startswith(
                                ("*", "/*", "//")
                            ):
                                curr -= 1
                                if lstrip:
                                    curr_line = curr_line.lstrip()
                                # since we put state variable at the beginning
                                # the comment with it should also at the beginning
                                target_region.append((curr_line, curr))
                            else:
                                break

    text = ""
    for c, strs in contract2lines.items():
        # put the start of contract decleration if flag is on
        if with_contract_decl:
            start_line_idx = min(c.source_mapping.lines)
            decl_start_lines = []
            line_idx = start_line_idx
            while line_idx <= len(filelines):
                line = filelines[line_idx - 1]
                decl_start_lines.append(line)
                line_idx += 1
                if line.rstrip().endswith("{"):
                    break
            text += "".join(decl_start_lines)
        sorted_tuples = sorted(strs, key=lambda t: t[1])
        sorted_lines = map(lambda t: t[0], sorted_tuples)
        text += "".join(sorted_lines)

        # put the end of contract decleration to the end if flag is on
        if with_contract_decl:
            end = max(c.source_mapping.lines)
            if end - 1 >= len(filelines):
                text += filelines[len(filelines) - 1]
            else:
                text += filelines[end - 1]
        text += "\n"

    return text


def get_contract_names(c: Contract) -> Set[str]:
    """A contract can inherit many other contracts,
    get_contract_names returns a list of names
    for all of them including itself.

    Args:
        c (Contract): Target contract

    Returns:
        Set[str]: list of contract names
    """

    names = set()
    explore = [c]
    explored = set()
    while len(explore) != 0:
        curr = explore.pop()
        if curr in explored:
            continue
        explored.add(curr)
        names.add(curr.name.lower())
        for toexlore in curr.inheritance:
            explore.append(toexlore)
            names.add(toexlore.name.lower())
    return names


def get_public_state_var_sigs(c: Contract) -> Set[str]:
    """get a list of public state variables

    Args:
        c (Contract): _description_

    Returns:
        Set[str]: List of state variable as signature
    """
    signatures = set()
    explore = [c]
    explored = set()
    while len(explore) != 0:
        curr = explore.pop()
        if curr in explored:
            continue
        explored.add(curr)

        for toexlore in curr.inheritance:
            explore.append(toexlore)

        for cv in curr.state_variables:
            print(cv, cv.visibility, cv.full_name, curr.name)
            if cv.visibility == "public":
                signatures.add(cv.signature_str)
    return signatures


def get_erc_number(c: Contract) -> str:
    names = get_contract_names(c)
    for name in names:
        idx = name.find("erc")
        if idx != -1:
            return name[idx + 3 :]
    return None


def get_erc_numbers(c: Contract) -> List[str]:
    ercs = set()
    names = get_contract_names(c)
    for name in names:
        idx = name.find("erc")
        if idx != -1:
            ercs.add(name[idx + 3 :])
    return list(ercs)


def get_functions_to_check(c: Contract) -> List[FunctionContract]:
    functions = []

    for f in c.functions:
        if f.is_constructor and not f.is_declared_by(c):
            # print(f.name, "skip because of other contract's constructor")
            continue
        if not f.is_implemented:
            # print(f.name, "skip because of interface (no implementation)")
            continue
        if f.visibility != "public" and f.visibility != "external":
            # print(f.name, "skip because of not public or not external")
            continue
        functions.append(f)

    return functions
