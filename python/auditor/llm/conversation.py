from typing import Dict, List
from glob import glob
import os

from auditor.fs import read_text_file, write_text_file
import auditor.str
from python.auditor.llm.adapters import LLMAdapter


class Conversation:
    def __init__(self, adapter: LLMAdapter, folder: str) -> None:
        self.model_temperature = 0
        self.prompt_prefix = "p"
        self.reply_prefix = "r"
        self.prompt_suffix = ".txt"
        self.reply_suffix = ".txt"
        self.folder = folder
        self.llm_adapter = adapter

    def _get_prompts_and_replies(self):
        us = self.get_prompt_files()
        rs = self.get_reply_files()
        return us, rs

    def get_prompt_files(self):
        return glob(
            os.path.join(self.folder, f"{self.prompt_prefix}*{self.prompt_suffix}")
        )

    def get_reply_files(self):
        return glob(
            os.path.join(self.folder, f"{self.reply_prefix}*{self.reply_suffix}")
        )

    def _get_filename_of_prompt_at(self, folder: str, idx: int):
        return os.path.join(folder, f"{self.prompt_prefix}{idx}{self.prompt_suffix}")

    def _get_filename_of_reply_at(self, folder: str, idx: int):
        return os.path.join(folder, f"{self.reply_prefix}{idx}{self.reply_suffix}")

    def print_messages(self, messages: List[Dict]):
        for m in messages:
            self.print_message(m)

    def print_message(self, m):
        content = m["content"]
        role = m["role"]
        summary_content = auditor.str.prefix(content, 128)
        print(f"{role}: {summary_content}")

    def get_messages(self) -> List:
        us, rs = self._get_prompts_and_replies()
        messages = []
        for i in range(len(us)):
            prompt_content = read_text_file(
                self._get_filename_of_prompt_at(self.folder, i)
            )
            messages.append({"role": "user", "content": prompt_content})
            self.print_message(messages[-1])

            # llm already answered
            if i < len(rs):
                reply_filepath = self._get_filename_of_reply_at(self.folder, i)
                reply_content = read_text_file(reply_filepath)
                messages.append({"role": "assistant", "content": reply_content})
        return messages

    def add_user_prompt(self, prompt: str, index = None):
        us, _ = self._get_prompts_and_replies()
        prompt_filepath = os.path.join(
            self.folder, f"{self.prompt_prefix}{index if index is not None else len(us)}{self.prompt_suffix}"
        )
        write_text_file(prompt_filepath, prompt)

    def run(self, force=False, extra_messages=None):
        us, rs = self._get_prompts_and_replies()

        if force:
            for r in rs:
                os.remove(r)
            rs = []
        messages = []
        if extra_messages:
            messages.extend(extra_messages)

        for i in range(len(us)):
            prompt_content = read_text_file(
                self._get_filename_of_prompt_at(self.folder, i)
            )
            messages.append({"role": "user", "content": prompt_content})
            self.print_message(messages[-1])

            # llm already answered
            if i < len(rs):
                reply_filepath = self._get_filename_of_reply_at(self.folder, i)
                reply_content = read_text_file(reply_filepath)
                messages.append({"role": "assistant", "content": reply_content})
                self.print_message(messages[-1])
            else:
                # need to ask llm
                if messages[-1]["role"] == "assistant":
                    raise RuntimeError(
                        f"expect new prompt, but latest is reply[{reply_filepath}]"
                    )

                reply = self.llm_adapter.ask(messages)
                self.print_message({"role": "assistant", "content": reply})
                write_text_file(self._get_filename_of_reply_at(self.folder, i), reply)

        return None


class AuditorConversation(Conversation):
    def run(self, force=False):
        us, rs = self._get_prompts_and_replies()
        if force:
            for r in rs:
                os.remove(r)
            rs = []
        messages = [
            # {
            #     "role": "system",
            #     "content": "Act like a smart contract auditor. You will be provided with a code and an instruction. Follow the instruction to check the code.",
            # }
        ]

        for i in range(len(us)):
            prompt_content = read_text_file(
                self._get_filename_of_prompt_at(self.folder, i)
            )
            messages.append({"role": "user", "content": prompt_content})
            self.print_message(messages[-1])

            # llm already answered
            if i < len(rs):
                reply_filepath = self._get_filename_of_reply_at(self.folder, i)
                reply_content = read_text_file(reply_filepath)
                messages.append({"role": "assistant", "content": reply_content})
                self.print_message(messages[-1])
                if (
                    self.folder.find("condevent") != -1
                    or self.folder.find("gcheckcond_") != -1
                    or self.folder.find("_call_") != -1
                    or self.folder.find("_eparamcond") != -1
                ):
                    if i == 0 and reply_content.find("NO") != -1:
                        print("[info] skip next since condition is NO")
                        break
                
                elif os.path.basename(self.folder).isdigit() and len(us) > 1:
                    if i == 0 and reply_content.find("NO") != -1:
                        print("[info] skip next since condition is NO")
                        break

            else:
                # need to ask llm
                if messages[-1]["role"] == "assistant":
                    raise RuntimeError(
                        f"expect new prompt, but latest is reply[{reply_filepath}]"
                    )
                reply = self.llm_adapter.ask(messages)
                self.print_message({"role": "assistant", "content": reply})
                write_text_file(self._get_filename_of_reply_at(self.folder, i), reply)

                if (
                    self.folder.find("condevent") != -1
                    or self.folder.find("gcheckcond_") != -1
                    or self.folder.find("_call_") != -1
                    or self.folder.find("_eparamcond") != -1
                ):
                    if i == 0 and reply.find("NO") != -1:
                        print("[info] skip next since condition is NO")
                        break
                elif os.path.basename(self.folder).isdigit() and len(us) > 1:
                    if i == 0 and reply.find("NO") != -1:
                        print("[info] skip next since condition is NO")
                        break

        return None
