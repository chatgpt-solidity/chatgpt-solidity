from auditor.llm.plugin import PlugIn
from auditor.llm.conversation import Conversation
from auditor.llm.adapters import LLMAdapter
from python.auditor.fs import read_text_file


class VerifyPlugIn(PlugIn):
    def __init__(self, auditor: LLMAdapter, conversation_folder: str) -> None:
        super().__init__("verify", auditor, conversation_folder)

    def verify_result(self):
        c = Conversation(None, self.conversation_folder)
        plugin_conv = Conversation(None, self.get_plugin_conversation_folder())
        reply = read_text_file(c.get_reply_files()[-1])
        verified_reply = read_text_file(plugin_conv.get_reply_files()[-1])
        if (reply.find("YES") != -1 and verified_reply.find("YES") != -1) or (
            reply.find("NO") != -1 and verified_reply.find("NO") != -1
        ):
            print("Verified: Passed")
        else:
            print("Verified: Failed")

    def run(self, force=False):
        c = Conversation(None, self.conversation_folder)
        messages = c.get_messages()
        if messages[-1]["role"] != "assistant":
            raise Exception(
                f"expect last message should be a reply from LLM in folder '{self.conversation_folder}' "
            )
        if force:
            self.clean_plugin_conversation_folder()
        self.create_plugin_conversation_folder()
        plugin_conv = Conversation(self.auditor, self.get_plugin_conversation_folder())

        if len(plugin_conv.get_prompt_files()) > 0 and not force:
            # already generated the prompt
            pass
        else:
            conclude_prompt = (
                'Does the explanation apologize or not? Reply in "YES" or "NO".'
            )
            # if messages[-1]["content"].find("\n") > 1:
            #     # if there is multiple newline, highly possible LLM already explain the reason in the reply
            #     plugin_conv.add_user_prompt(conclude_prompt)
            # else:
            plugin_conv.add_user_prompt(
                'Explain the reason step by step and conclude the final answer in "YES" or "NO".'
            )
            # plugin_conv.add_user_prompt(conclude_prompt)

        plugin_conv.run(force, extra_messages=messages)
        confirm = read_text_file(plugin_conv.get_reply_files()[0]).find("YES") != -1
        if not confirm:
            print("Reject the original")
        else:
            print("Insist with the original answer")


def generate_conclude_prompt(c: Conversation):
    """Generate the conclusion, which is "Conclude" + <last question>

    Args:
        c (Conversation): Conversation that is going to be generate the conclusion for.
    """
    prompt = read_text_file(c.get_prompt_files()[-1])

    for line in prompt.splitlines()[:2]:
        if line.find("?") != -1:
            last_question = line
            last_question = last_question[:1].lower() + last_question[1:]

            return last_question

    raise Exception(f"cannot find last question in {c.folder}")
