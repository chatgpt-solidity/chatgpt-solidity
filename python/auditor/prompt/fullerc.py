from hashlib import sha256
import os
from auditor.prompt import PromptsGenerator
from python.auditor.erc import ERC
from python.auditor.fs import read_text_file
from python.auditor.llm.conversation import Conversation
from python.auditor.prompt.utils import (
    fill_template,
    get_event_interface,
    get_function_signature,
)
from python.auditor.rules_config import (
    FULL_ERCS,
    FULLERC_TEMPLATES,
    UNIVERSAL_COND_TEMPLATE,
    UNIVERSAL_TEMPLATE,
)
from python.auditor.sol_file_folder import get_function_name, get_function_text_by_name


class FullERCPromptsGenerator(PromptsGenerator):
    def generate(self):
        self.backup_hashes()

        # Output folder
        llm_folder = os.path.join(self.cf.folder_path, "llm")

        # Metadata contains the all the information(sliced function, ERCs, etc.) about smart contract(s)
        metadata = self.cf.metadata

        for cmeta in metadata.get_contracts():
            ercs = cmeta["ercs"]

            for erc in ercs:
                # if we don't support this ERC, continue
                if erc not in FULL_ERCS:
                    print(
                        f"[info] Do not support ERC{erc} yet, skip generate prompts for it."
                    )
                    continue

                erc_text = FULL_ERCS[erc]
                idx = 0
                # Each function + Full ERC
                for fsig, fp in cmeta["func2file"].items():
                    code = read_text_file(fp).strip("\n")
                    conversation_dir = os.path.join(llm_folder, f"{idx}")
                    os.makedirs(conversation_dir, exist_ok=True)
                    c = Conversation(None, conversation_dir)
                    fname = get_function_name(fsig)
                    ask = fill_template(
                        FULLERC_TEMPLATES["function"].flows[0]["template"],
                        code=code,
                        erc=erc_text,
                        function=fname,
                    )
                    c.add_user_prompt(ask, 0)
                    idx += 1
                # Whole function interfaces + Full ERC
                interfaces = list(cmeta["func2file"].keys())
                state_var_sigs = (
                    cmeta["state_var_sigs"] if "state_var_sigs" in cmeta else []
                )
                interfaces.extend(state_var_sigs)
                interfaces_str = "\n".join(interfaces)

                conversation_dir = os.path.join(llm_folder, f"{idx}")
                os.makedirs(conversation_dir, exist_ok=True)
                c = Conversation(None, conversation_dir)

                ask = fill_template(
                    FULLERC_TEMPLATES["interface"].flows[0]["template"],
                    code=interfaces_str,
                    erc=erc_text,
                )
                c.add_user_prompt(ask, 0)
                idx += 1

                # Whole event interfaces + Full ERC
                contract_events = cmeta.get("events", [])
                einterfaces = "\n".join(
                    [
                        get_event_interface(ce["name"], ce["params"])
                        for ce in contract_events
                    ]
                )

                conversation_dir = os.path.join(llm_folder, f"{idx}")
                os.makedirs(conversation_dir, exist_ok=True)
                c = Conversation(None, conversation_dir)

                ask = fill_template(
                    FULLERC_TEMPLATES["einterface"].flows[0]["template"],
                    code=einterfaces,
                    erc=erc_text,
                )
                c.add_user_prompt(ask, 0)
                idx += 1
