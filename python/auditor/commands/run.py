from argparse import _SubParsersAction
import os
import sys
import time
from auditor.llm.adapters import OpenAIGPT3, OpenAIGPT4, OpenAIGPT4Turbo
from auditor.llm.conversation import AuditorConversation, Conversation
from glob import glob

from auditor.llm.plugin.verify import VerifyPlugIn


def setup(subparsers: _SubParsersAction):
    run_subparser = subparsers.add_parser("run")
    run_subparser.add_argument("folder")
    run_subparser.add_argument("--set", action="store_true")
    run_subparser.add_argument("--setset", action="store_true")
    run_subparser.add_argument("--gpt3", action="store_true")
    run_subparser.add_argument("--gpt4", action="store_true")
    run_subparser.add_argument("--normal", action="store_true")
    run_subparser.add_argument("--first", type=int)
    run_subparser.add_argument("--force", action="store_true")
    run_subparser.add_argument(
        "--plugin",
        type=str,
        action="append",
        help="Plugin name, can specify multipel times",
    )
    run_subparser.add_argument("--filter", type=str)


def run_llm_folder(llm_folder: str, adapter, retry_limit=3, force=False, filter=None):
    children = os.listdir(llm_folder)
    for child in children:
        start = None
        retry_cnt = 0
        child_dir = os.path.join(llm_folder, child)
        if filter is not None and child_dir.find(filter) == -1:
            continue
        while True:
            start = time.time()
            try:
                c = AuditorConversation(adapter, child_dir)
                c.run(force)
                break
            except Exception as ex:
                print(ex, file=sys.stderr)
                if str(ex).find("Please reduce the length of the messages") != -1:
                    print("exceed length limit, ignored and continue")
                    break
                if retry_cnt >= retry_limit:
                    print("exceed retry limit, ignored and continue")
                    break

                print("wait 60 seconds and retry", file=sys.stderr)
                retry_cnt += 1
                time.sleep(60)
        if start:
            end = time.time()
            dur = end - start
            print(f"[duration] {dur:.2f} secs")


def command(args):
    folder = args.folder
    adapter = get_adapter(args)
    print("Adapter", type(adapter))
    if not os.path.exists(folder):
        print(f'folder "{folder}" does not exist', file=sys.stderr)
        return
    if args.set:
        run_llm_folder(
            os.path.join(folder, "llm"), adapter, force=args.force, filter=args.filter
        )

    if args.setset:
        cfolders = glob(f"{folder}/*")
        limit = None

        if args.first:
            limit = args.first
        for c in cfolders:
            cset = os.path.join(c, "llm")
            if not os.path.exists(cset):
                print(f"{c}, skip since no llm folder")
                continue
            run_llm_folder(cset, adapter, force=args.force, filter=args.filter)
            if limit is not None:
                limit -= 1
                if limit == 0:
                    print(f"reach the # of folder limit {args.first}, stop")
                    break
    else:
        c = (
            Conversation(adapter, folder)
            if args.normal
            else AuditorConversation(adapter, folder)
        )
        c.run(args.force)

        if args.plugin:
            for plugin in args.plugin:
                if plugin == "verify":
                    plugin = VerifyPlugIn(adapter, folder)
                    plugin.run(args.force)


def get_adapter(args):
    if args.gpt3:
        return OpenAIGPT3()
    elif args.gpt4:
        return OpenAIGPT4()
    else:
        return OpenAIGPT4Turbo()
