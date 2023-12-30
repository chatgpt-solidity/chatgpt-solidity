

from hashlib import sha256
import os
from auditor.prompt import PromptsGenerator
from python.auditor.erc import ERC
from python.auditor.fs import read_text_file
from python.auditor.llm.conversation import Conversation
from python.auditor.prompt.utils import fill_template, get_event_interface, get_function_signature
from python.auditor.rules_config import UNIVERSAL_COND_TEMPLATE, UNIVERSAL_TEMPLATE
from python.auditor.sol_file_folder import get_function_name, get_function_text_by_name


class UniversalPromptsGenerator(PromptsGenerator):
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
                if erc not in self.erc_rules:
                    print(
                        f"[info] Do not support ERC{erc} yet, skip generate prompts for it."
                    )
                    continue

                erc_rule_obj = self.erc_rules[erc]
                self.generate_universal_prompts(llm_folder, cmeta, erc_rule_obj)

    def generate_universal_prompts(self, llm_folder, cmeta, erc_rule_obj):
        erc_obj = ERC(erc_rule_obj)

        idx = 0
        # iterate function rules
        for fname, rtype, rule_obj in erc_obj.function_rules():
            rule = ""
            if rtype == "throw":
                rule += "throw "
                if "if" in rule_obj:
                    rule += rule_obj["if"]
                elif "unless" in rule_obj:
                    rule += rule_obj["unless"]
                else:
                    raise Exception(f"malformed rule in funcion {fname}'s {rtype}")
            elif rtype == "event":
                rule += "emit Event " + rule_obj
            elif rtype == "return":
                rule += rule_obj
            elif rtype == "other":
                rule += rule_obj
            
            texts = get_function_text_by_name(fname, cmeta)
            for sig, code in texts:
                init_question = fill_template(
                    UNIVERSAL_TEMPLATE.flows[0]["template"],
                    code=code,
                    rule=rule
                )

                conversation_dir = os.path.join(llm_folder, f"{idx}")
                os.makedirs(conversation_dir, exist_ok=True)

                c = Conversation(None, conversation_dir)
                c.add_user_prompt(init_question, 0)

                self.llm_children_hashes[conversation_dir] = sha256(
                    init_question.encode()
                ).hexdigest()

                idx += 1
            
        interfaces = list(cmeta["func2file"].keys())
        state_var_sigs = cmeta["state_var_sigs"] if "state_var_sigs" in cmeta else []
        interfaces.extend(state_var_sigs)
        interfaces_str = "\n".join(interfaces)

        # iterate interface rules
        for fname, fargs, fret in erc_obj.functions():
            farg_types = [arg["type"] for arg in fargs]
            rule = get_function_signature(fname, farg_types, fret)
            code=interfaces_str
            init_question = fill_template(
                UNIVERSAL_TEMPLATE.flows[0]["template"],
                code=code,
                rule=rule
            )

            conversation_dir = os.path.join(llm_folder, f"{idx}")
            os.makedirs(conversation_dir, exist_ok=True)

            c = Conversation(None, conversation_dir)
            c.add_user_prompt(init_question, 0)

            self.llm_children_hashes[conversation_dir] = sha256(
                init_question.encode()
            ).hexdigest()

            idx += 1

        # iterate event rules
        contract_events = cmeta.get("events", [])
        einterfaces = "\n".join([get_event_interface(ce["name"], ce["params"]) for ce in contract_events])
        for ename, eargs in erc_obj.events():
            einterface = get_event_interface(ename, eargs)
            conversation_dir = os.path.join(llm_folder, f"{idx}")
            os.makedirs(conversation_dir, exist_ok=True)
            c = Conversation(None, conversation_dir)

            init_question = fill_template(
                UNIVERSAL_TEMPLATE.flows[0]["template"],
                code=einterfaces,
                rule=einterface
            )
            c.add_user_prompt(init_question, 0)
            idx += 1

        for ename, condition in erc_obj.event_rules():
            for fsig, fp in cmeta["func2file"].items():
                # pure and view functions are not allowed to emit
                attrs = cmeta["func2attrs"][fsig]
                if attrs["is_view"] or attrs["is_pure"]:
                    continue

                code = read_text_file(fp).strip("\n")
                rule = "emit Event " + ename
                conversation_dir = os.path.join(llm_folder, f"{idx}")
                os.makedirs(conversation_dir, exist_ok=True)
                c = Conversation(None, conversation_dir)

                cond_match = fill_template(
                    UNIVERSAL_COND_TEMPLATE.flows[0]["template"],
                    code=code,
                    condition=condition
                )
                ask = fill_template(
                    UNIVERSAL_COND_TEMPLATE.flows[1]["template"],
                    rule=rule
                )
                c.add_user_prompt(cond_match, 0)
                c.add_user_prompt(ask, 1)
                idx += 1
        for rtype, rule_obj in erc_obj.global_rules():
            rule = ""
            condition = ""
            if rtype == "throw":
                rule += "throw "
                if "if" in rule_obj:
                    rule += rule_obj["if"]
                elif "unless" in rule_obj:
                    rule += rule_obj["unless"]
                else:
                    raise Exception(f"malformed rule in funcion {fname}'s {rtype}")
            elif rtype == "event":
                rule += "emit Event " + rule_obj
            elif rtype == "return":
                rule += rule_obj
            elif rtype == "other":
                rule += rule_obj
            elif rtype == "check":
                if "rule" in rule_obj:
                    rule = rule_obj["rule"]
                    condition = rule_obj["if"]
            

            for fsig, fp in cmeta["func2file"].items():
                code = read_text_file(fp)

                conversation_dir = os.path.join(llm_folder, f"{idx}")
                os.makedirs(conversation_dir, exist_ok=True)
                c = Conversation(None, conversation_dir)

                cond_match = fill_template(
                    UNIVERSAL_COND_TEMPLATE.flows[0]["template"],
                    code=code,
                    condition=condition
                )
                ask = fill_template(
                    UNIVERSAL_COND_TEMPLATE.flows[1]["template"],
                    rule=rule
                )
                c.add_user_prompt(cond_match, 0)
                c.add_user_prompt(ask, 1)
                idx += 1

            