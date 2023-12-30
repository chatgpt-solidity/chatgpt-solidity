from hashlib import sha256
import os
from typing import Dict, List
from python.auditor.erc import ERC
from python.auditor.fs import read_text_file, write_text_file
from python.auditor.llm.conversation import Conversation
from python.auditor.prompt import PromptsGenerator
from python.auditor.prompt.utils import (
    fill_template,
    get_event_interface,
    get_event_interface_with_pname,
    get_function_signature,
)
from python.auditor.rules_config import NOCM_TEMPLATES, SPECIALIZED_TEMPLATES
from python.auditor.sol_file_folder import (
    ContractMetadata,
    get_function_name,
    get_function_text_by_name,
)


class SpecializedNoCMPromptsGenerator(PromptsGenerator):
    def generate(self):
        self.backup_hashes()

        llm_folder = os.path.join(self.cf.folder_path, "llm")
        metadata = self.cf.metadata

        # check contracts in the solidity file one by one
        for cmeta in metadata.get_contracts():
            # check which ERC this contract
            # (could have a situation that the contract has all the
            # signatures of some ERCs but does not explicitly says that)
            ercs = cmeta["ercs"]

            # a contract can have multiple ERCs
            # so let's generate the prompts for them
            for erc in ercs:
                # if we don't support this ERC, continue
                if erc not in self.erc_rules:
                    print(
                        f"[info] Do not support ERC{erc} yet, skip generate prompts for it."
                    )
                    continue

                erc_rule = self.erc_rules[erc]

                # generate signature & return rules
                # Here, if a function is missing, it can be directly reported without LLM

                # FIXME: this is different but correct way to iterate the rules
                # all above implementation should be refactored
                erc_obj = ERC(erc_rule)

                self.gen_prompts_for_signature_rule(erc_obj, llm_folder, cmeta)

                if "globalRule" in erc_rule:
                    self.gen_prompts_for_global_rule(
                        erc_rule.get("globalRule", {}), llm_folder, cmeta
                    )

                if "functionRule" in erc_rule:
                    self.gen_prompts_for_function_rule(
                        erc_rule["functionRule"].items(), llm_folder, cmeta
                    )
                if "eventRule" in erc_rule:
                    self.gen_promtps_for_conditional_event_rule(
                        erc_rule["eventRule"].items(),
                        llm_folder,
                        cmeta,
                        erc_rule["events"],
                    )

        self.dump_hashes(self.cf.folder_path)

    def gen_prompts_for_global_rule(
        self, typed_rule_obj, llm_folder, cmeta: ContractMetadata
    ):
        for rtype, rules in typed_rule_obj.items():
            if rtype != "check":
                # TODO
                continue
            for ridx, rule in enumerate(rules):
                for fsig, fp in cmeta["func2file"].items():
                    code = read_text_file(fp)
                    fname = get_function_name(fsig)

                    if isinstance(rule, str):
                        init_question = fill_template(
                            SPECIALIZED_TEMPLATES["check"].flows[0]["template"],
                            rule=rule,
                            code=code.strip("\n"),
                            function=fname,
                        )

                        conversation_dir = os.path.join(
                            llm_folder, f"{fname}_gcheck_{ridx}"
                        )
                        os.makedirs(conversation_dir, exist_ok=True)

                        init_question_filepath = os.path.join(
                            conversation_dir, "p0.txt"
                        )
                        write_text_file(
                            init_question_filepath,
                            init_question,
                        )

                        self.llm_children_hashes[conversation_dir] = sha256(
                            init_question.encode()
                        ).hexdigest()
                    else:
                        # with condition
                        cond = rule["if"]
                        r = rule["rule"]
                        init_question = fill_template(
                            NOCM_TEMPLATES["check"].flows[0]["template"],
                            code=code.strip("\n"),
                            function=fname,
                            rule=r + " if " + cond,
                        )

                        conversation_dir = os.path.join(
                            llm_folder, f"{fname}_gcheckcond_{ridx}"
                        )
                        os.makedirs(conversation_dir, exist_ok=True)

                        init_question_filepath = os.path.join(
                            conversation_dir, "p0.txt"
                        )
                        write_text_file(
                            init_question_filepath,
                            init_question,
                        )

                        self.llm_children_hashes[conversation_dir] = sha256(
                            (init_question).encode()
                        ).hexdigest()

    def gen_prompts_for_signature_rule(self, erc: ERC, llm_folder, cmeta: Dict):
        interfaces: List[str] = list(cmeta["func2file"].keys())
        state_var_sigs = cmeta["state_var_sigs"] if "state_var_sigs" in cmeta else []
        interfaces.extend(state_var_sigs)
        interfaces_str = "\n".join(interfaces)
        idx = 0
        for fname, fparams, fret in erc.functions():
            arg_types = [p["type"] for p in fparams]
            # cadidates = get_function_text_by_name(fname, cmeta)
            fsig = get_function_signature(fname, arg_types, fret)

            # if not cadidates:
            #     if func_obj.get("optional", False):
            #         # check auto generated getters
            #         for auto_sig in state_var_sigs:
            #             if auto_sig.find()
            #         continue
            #     else:
            #         print(
            #             f"[Violation] missing required functon {fname}."
            #         )

            init_question = fill_template(
                SPECIALIZED_TEMPLATES["signature"].flows[0]["template"],
                interface=fsig,
                interfaces=interfaces_str,
            )

            conversation_dir = os.path.join(llm_folder, f"interfaces_{idx}")
            os.makedirs(conversation_dir, exist_ok=True)

            c = Conversation(None, conversation_dir)
            c.add_user_prompt(init_question, 0)

            self.llm_children_hashes[conversation_dir] = sha256(
                init_question.encode()
            ).hexdigest()

            idx += 1

        contract_events = cmeta.get("events", [])
        einterfaces = "\n".join(
            [get_event_interface(ce["name"], ce["params"]) for ce in contract_events]
        )

        idx = 0
        for ename, eparams in erc.events():
            einterface = get_event_interface(ename, eparams)
            conversation_dir = os.path.join(llm_folder, f"einterfaces_{idx}")
            os.makedirs(conversation_dir, exist_ok=True)
            c = Conversation(None, conversation_dir)

            init_question = fill_template(
                SPECIALIZED_TEMPLATES["esignature"].flows[0]["template"],
                interface=einterface,
                interfaces=einterfaces,
            )
            c.add_user_prompt(init_question, 0)
            idx += 1

    def gen_promtps_for_conditional_event_rule(
        self, erule_items, llm_folder, cmeta: ContractMetadata, events: List[Dict]
    ):
        for ename, rules_obj in erule_items:
            cond_idx = 0

            for cond in rules_obj.get("conditions", []):
                e_cond = None
                e_or = []

                if isinstance(cond, str):
                    e_cond = cond
                else:
                    e_cond = cond["if"]
                    e_or = cond["orEvents"]

                ask_event = "Emit " + ename
                for e in e_or:
                    ask_event += f" or {e}"

                ask_event += " if "
                ask_event += e_cond

                # generate for every public/external functions
                for fsig, fp in cmeta["func2file"].items():
                    # pure and view functions are not allowed to emit
                    attrs = cmeta["func2attrs"][fsig]
                    if attrs["is_view"] or attrs["is_pure"]:
                        continue

                    code = read_text_file(fp).strip("\n")
                    fname = get_function_name(fsig)
                    template_obj = SPECIALIZED_TEMPLATES["event-cond"]
                    example = ""
                    # find if any examples need to be injected
                    examples = template_obj.examples
                    for e in examples:
                        if "matcher" not in e:
                            continue
                        if e_cond.find(e["matcher"]) != -1:
                            example += e["example"]
                            example += "\n"

                    if "solc_version" in cmeta and cmeta["solc_version"]:
                        progma = "pragma solidity " + cmeta["solc_version"] + ";\n"
                        code = progma + code

                    init_question = fill_template(
                        NOCM_TEMPLATES["event"].flows[0]["template"],
                        code=code,
                        function=fname,
                        rule=ask_event,
                        example=example,
                    )

                    conv_dir_prefix = fname + "#" + str(fsig.count(","))
                    conversation_dir = self.get_conversation_dir(
                        llm_folder,
                        conv_dir_prefix,
                        "condevent_" + ename,
                        cond_idx,
                        cmeta["name"],
                    )
                    os.makedirs(conversation_dir, exist_ok=True)

                    init_question_filepath = os.path.join(conversation_dir, "p0.txt")
                    write_text_file(
                        init_question_filepath,
                        init_question,
                    )

                    self.llm_children_hashes[conversation_dir] = sha256(
                        (init_question).encode()
                    ).hexdigest()

                cond_idx += 1

            if "assign" in rules_obj:
                for param_idx, param_rule in enumerate(rules_obj["assign"]):
                    # parameter rule assumes the event emission
                    # so we should check whether the function has such event emission before generating the prompts
                    # it can be done by simply search whether emit XXXX( is existed
                    # generate for every public/external functions
                    for fsig, fp in cmeta["func2file"].items():
                        # pure and view functions are not allowed to emit
                        attrs = cmeta["func2attrs"][fsig]
                        if attrs["is_view"] or attrs["is_pure"]:
                            continue

                        code = read_text_file(fp).strip("\n")

                        # if the code does not has event emission, do not generate the prompts
                        if code.find(f"emit {ename}") == -1:
                            print(f"skip since function does not emit {ename}")
                            continue
                        fname = get_function_name(fsig)

                        # since the rule is related to the specific parameters, interface of the event should be appended
                        event_dict = next(filter(lambda e: e["name"] == ename, events))
                        event_interface = get_event_interface_with_pname(
                            ename, event_dict["name"], event_dict["params"]
                        )

                        if isinstance(param_rule, dict):
                            # param_rule is dict with key if and else
                            cond = param_rule["if"]
                            rule = param_rule["then"]
                            rule += "\n"
                            rule += event_interface
                            template_obj = SPECIALIZED_TEMPLATES["event-assign-cond"]
                            init_question = fill_template(
                                template_obj.flows[0]["template"],
                                code=code,
                                function=fname,
                                condition=cond,
                            )
                            ask_question = fill_template(
                                template_obj.flows[1]["template"],
                                event=ename,
                                rule=rule,
                            )

                            conv_dir_prefix = fname + "#" + str(fsig.count(","))
                            conversation_dir = self.get_conversation_dir(
                                llm_folder,
                                conv_dir_prefix,
                                "eparamcond_" + ename,
                                str(cond_idx) + "_" + str(param_idx),
                                cmeta["name"],
                            )
                            os.makedirs(conversation_dir, exist_ok=True)

                            init_question_filepath = os.path.join(
                                conversation_dir, "p0.txt"
                            )
                            ask_question_filepath = os.path.join(
                                conversation_dir, "p1.txt"
                            )
                            write_text_file(
                                init_question_filepath,
                                init_question,
                            )
                            write_text_file(
                                ask_question_filepath,
                                ask_question,
                            )

                            self.llm_children_hashes[conversation_dir] = sha256(
                                (init_question + ask_question).encode()
                            ).hexdigest()
                        else:
                            # param_rule is simply a string
                            rule = param_rule
                            rule += "\n"
                            rule += event_interface
                            template_obj = SPECIALIZED_TEMPLATES["event-assign"]
                            init_question = fill_template(
                                template_obj.flows[0]["template"],
                                {
                                    "code": code,
                                    "function": fname,
                                    "event": ename,
                                    "rule": rule,
                                },
                            )

                            conv_dir_prefix = fname + "#" + str(fsig.count(","))
                            conversation_dir = self.get_conversation_dir(
                                llm_folder,
                                conv_dir_prefix,
                                "eparam_" + ename,
                                str(cond_idx) + "_" + str(param_idx),
                                cmeta["name"],
                            )
                            os.makedirs(conversation_dir, exist_ok=True)

                            init_question_filepath = os.path.join(
                                conversation_dir, "p0.txt"
                            )
                            write_text_file(
                                init_question_filepath,
                                init_question,
                            )
                            self.llm_children_hashes[conversation_dir] = sha256(
                                init_question.encode()
                            ).hexdigest()

    def gen_prompts_for_function_rule(self, frule_items, llm_folder, cmeta):
        progma = None
        if "solc_version" in cmeta and cmeta["solc_version"]:
            progma = "pragma solidity " + cmeta["solc_version"] + ";\n"

        for fname, rules_obj in frule_items:
            for category, rules in rules_obj.items():
                if category == "event":
                    events = rules.keys()
                    for event_idx, event in enumerate(events):
                        texts = get_function_text_by_name(fname, cmeta)
                        for sig, code in texts:
                            init_question = fill_template(
                                SPECIALIZED_TEMPLATES[category].flows[0]["template"],
                                code=progma + code.strip("\n")
                                if progma
                                else code.strip("\n"),
                                function=fname,
                                event=event,
                            )

                            conv_dir_prefix = None
                            if len(texts) > 1:
                                conv_dir_prefix = fname + "#" + str(sig.count(","))
                            else:
                                conv_dir_prefix = fname
                            conversation_dir = self.get_conversation_dir(
                                llm_folder,
                                conv_dir_prefix,
                                category,
                                event_idx,
                                cmeta["name"],
                            )
                            os.makedirs(conversation_dir, exist_ok=True)

                            init_question_filepath = os.path.join(
                                conversation_dir, "p0.txt"
                            )
                            write_text_file(
                                init_question_filepath,
                                init_question,
                            )

                            self.llm_children_hashes[conversation_dir] = sha256(
                                init_question.encode()
                            ).hexdigest()
                elif category == "throw":
                    for throw_idx, throw_obj in enumerate(rules):
                        texts = get_function_text_by_name(fname, cmeta)
                        for sig, code in texts:
                            code = code.strip("\n")
                            if "if" in throw_obj:
                                init_question = fill_template(
                                    SPECIALIZED_TEMPLATES["throw"].flows[0]["template"],
                                    code=code,
                                    function=fname,
                                    condition=throw_obj["if"],
                                )
                            elif "unless" in throw_obj:
                                cond = throw_obj["unless"]
                                template_obj = SPECIALIZED_TEMPLATES["throw-unless"]
                                example = ""
                                # find if any examples need to be injected
                                examples = template_obj.examples
                                for e in examples:
                                    if "matcher" not in e:
                                        continue
                                    if cond.find(e["matcher"]) != -1:
                                        example += e["example"]
                                        example += "\n"

                                init_question = fill_template(
                                    SPECIALIZED_TEMPLATES["throw-unless"].flows[0][
                                        "template"
                                    ],
                                    code=code,
                                    function=fname,
                                    condition=cond,
                                    example=example,
                                )
                            else:
                                raise Exception(f"invalid rule found: {throw_obj}")

                            conv_dir_prefix = None
                            if len(texts) > 1:
                                conv_dir_prefix = fname + "#" + str(sig.count(","))
                            else:
                                conv_dir_prefix = fname
                            conversation_dir = self.get_conversation_dir(
                                llm_folder,
                                conv_dir_prefix,
                                "throw",
                                throw_idx,
                                cmeta["name"],
                            )
                            os.makedirs(conversation_dir, exist_ok=True)

                            init_question_filepath = os.path.join(
                                conversation_dir, "p0.txt"
                            )
                            write_text_file(
                                init_question_filepath,
                                init_question,
                            )

                            self.llm_children_hashes[conversation_dir] = sha256(
                                init_question.encode()
                            ).hexdigest()
                elif category == "call":
                    hooks = rules.keys()
                    for hook in hooks:
                        hook_conditions = rules[hook]
                        for rule_idx, cond_obj in enumerate(hook_conditions):
                            texts = get_function_text_by_name(fname, cmeta)
                            for sig, code in texts:
                                init_question = fill_template(
                                    SPECIALIZED_TEMPLATES["call-cond"].flows[0][
                                        "template"
                                    ],
                                    {
                                        "code": code.strip("\n"),
                                        "condition": cond_obj["if"],
                                        "function": fname,
                                    },
                                )

                                conv_dir_prefix = None
                                if len(texts) > 1:
                                    conv_dir_prefix = fname + "#" + str(sig.count(","))
                                else:
                                    conv_dir_prefix = fname
                                conversation_dir = self.get_conversation_dir(
                                    llm_folder,
                                    conv_dir_prefix,
                                    category,
                                    rule_idx,
                                    cmeta["name"],
                                )
                                os.makedirs(conversation_dir, exist_ok=True)

                                init_question_filepath = os.path.join(
                                    conversation_dir, "p0.txt"
                                )
                                write_text_file(
                                    init_question_filepath,
                                    init_question,
                                )

                                ask_question = fill_template(
                                    SPECIALIZED_TEMPLATES["call-cond"].flows[1][
                                        "template"
                                    ],
                                    {"hook": hook},
                                )
                                ask_question_filepath = os.path.join(
                                    conversation_dir, "p1.txt"
                                )
                                write_text_file(
                                    ask_question_filepath,
                                    ask_question,
                                )

                                self.llm_children_hashes[conversation_dir] = sha256(
                                    (init_question + ask_question).encode()
                                ).hexdigest()

                else:
                    for rule_idx, rule in enumerate(rules):
                        texts = get_function_text_by_name(fname, cmeta)
                        for sig, code in texts:
                            # if category == "check" or category == "general":
                            init_question = fill_template(
                                SPECIALIZED_TEMPLATES[category].flows[0]["template"],
                                code=code.strip("\n"),
                                rule=rule,
                                function=fname,
                            )

                            conv_dir_prefix = None
                            if len(texts) > 1:
                                conv_dir_prefix = fname + "#" + str(sig.count(","))
                            else:
                                conv_dir_prefix = fname
                            conversation_dir = self.get_conversation_dir(
                                llm_folder,
                                conv_dir_prefix,
                                category,
                                rule_idx,
                                cmeta["name"],
                            )
                            os.makedirs(conversation_dir, exist_ok=True)

                            init_question_filepath = os.path.join(
                                conversation_dir, "p0.txt"
                            )
                            write_text_file(
                                init_question_filepath,
                                init_question,
                            )

                            self.llm_children_hashes[conversation_dir] = sha256(
                                init_question.encode()
                            ).hexdigest()
