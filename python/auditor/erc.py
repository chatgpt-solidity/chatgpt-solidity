

from typing import Dict


class ERC:
    def __init__(self, erc_dict: Dict) -> None:
        self._erc_dict = erc_dict
    
    def functions(self):
        for obj in self._erc_dict.get("functions", []):
            yield (obj["name"], obj["arg_types"], \
                   obj.get("return_type", None))
    
    def events(self):
        for obj in self._erc_dict.get("events", []):
            yield (obj["name"], obj["params"])
    
    def function_rules(self):
        for fname, typed_rule_obj in self._erc_dict.get("functionRule", {}).items():
            for rule_type, rules in typed_rule_obj.items():
                for rule in rules:
                    yield (fname, rule_type, rule)

    def event_rules(self):
        for ename, typed_rule_obj in self._erc_dict.get("eventRule", {}).items():
            for condition in typed_rule_obj.get("conditions", []):
                yield (ename, condition)

    def global_rules(self):
        typed_rule_obj = self._erc_dict.get("globalRule", None)
        if not typed_rule_obj:
            return
        for rule_type, rules in typed_rule_obj.items():
            for rule in rules:
                    yield (rule_type, rule)


