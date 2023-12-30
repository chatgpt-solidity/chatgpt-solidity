#!/usr/bin/env python3

import argparse
import importlib
import os
from glob import glob
import openai

openai.api_key = ""


def main():
    parser = argparse.ArgumentParser("auditor")
    subparsers = parser.add_subparsers(dest="command")

    command_files = glob("python/auditor/commands/*.py")
    command_callbacks = {}

    for file_path in command_files:
        command = os.path.splitext(os.path.basename(file_path))[0]
        import_path = os.path.splitext(file_path)[0].replace("/", ".")
        # Import the "command" function from the file
        module = importlib.import_module(import_path)
        setup_func = getattr(module, "setup")
        setup_func(subparsers)
        command_callbacks[command] = getattr(module, "command")

    args = parser.parse_args()
    command = args.command
    if not command:
        parser.print_help()
        return
    command_callbacks[command](args)


if __name__ == "__main__":
    main()
