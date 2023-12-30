from argparse import _SubParsersAction
import sys
from typing import Dict, List
from python.auditor.prompt.fullerc import FullERCPromptsGenerator
from python.auditor.prompt.specializedfullcode import (
    SpecializedFullCodePromptsGenerator,
)
from python.auditor.prompt.specializednocm import SpecializedNoCMPromptsGenerator
from python.auditor.prompt.specializednooneshot import (
    SpecializedNoOneShotPromptsGenerator,
)
from python.auditor.rules_config import ERCS

from python.auditor.sol_file_folder import (
    init_sol_file_folder,
    init_sol_file_folder_for_dataset,
)
from python.auditor.prompt import PromptsGenerator
from python.auditor.prompt.specialized import SpecializedPromptsGenerator
from python.auditor.prompt.universal import UniversalPromptsGenerator
from python.auditor.sol_file_folder import SolFileFolder


def setup(subparsers: _SubParsersAction):
    subparser = subparsers.add_parser("gen")
    subparser.add_argument("--file", type=str)
    subparser.add_argument("--name", type=str)
    subparser.add_argument("--erc", type=str)
    subparser.add_argument("--dataset", type=str)
    subparser.add_argument("output_folder", type=str)
    subparser.add_argument(
        "--cname2ercs",
        action="append",
        type=parse_cname2ercs,
        help="Enter NAME:List_of_numbers",
    )
    subparser.add_argument("--disable", action="append", type=str)
    subparser.add_argument(
        "--gen-mode",
        choices=[
            "universal",
            "specialized",
            "fullerc",
            "specializednocm",
            "specializednooneshot",
            "fullcode",
        ],
        default="specialized",
    )


def generate(cf, disables: List[str], generator_mode):
    generator = get_prompts_generator(generator_mode, cf, ERCS)
    generator.generate()


def parse_cname2ercs(input_str):
    name, numbers = input_str.split(":")
    numbers = numbers.split(",")
    return name, numbers


def get_prompts_generator(
    mode: str, cf: SolFileFolder, erc_rules: Dict
) -> PromptsGenerator:
    if mode == "specialized":
        return SpecializedPromptsGenerator(cf, erc_rules)
    elif mode == "universal":
        return UniversalPromptsGenerator(cf, erc_rules)
    elif mode == "fullerc":
        return FullERCPromptsGenerator(cf, None)
    elif mode == "specializednocm":
        return SpecializedNoCMPromptsGenerator(cf, erc_rules)
    elif mode == "specializednooneshot":
        return SpecializedNoOneShotPromptsGenerator(cf, erc_rules)
    elif mode == "fullcode":
        return SpecializedFullCodePromptsGenerator(cf, erc_rules)


def command(args):
    """Build the prompts that audits the given contrac

    Args:
        args (_type_): _description_
    """
    # contract file path
    file = args.file

    # check only this contract name (optional)
    name = args.name

    # check only for this ERC (optional)
    erc = args.erc

    # output folder
    output_folder = args.output_folder

    generater_mode = args.gen_mode
    dataset = args.dataset

    cname2ercs_dict = {}
    if args.cname2ercs:
        for name, numbers in args.cname2ercs:
            cname2ercs_dict[name] = numbers

    if file:
        cf = init_sol_file_folder(file, output_folder, cname2ercs_dict)
        generate(cf, disables=args.disable, generator_mode=generater_mode)

    elif dataset:
        for cf in init_sol_file_folder_for_dataset(
            dataset, output_folder, cname2ercs_dict
        ):
            try:
                generate(cf, disables=args.disable, generator_mode=generater_mode)
            except Exception as ex:
                raise ex
                print("[error]", cf.folder_path, str(ex), file=sys.stderr)
