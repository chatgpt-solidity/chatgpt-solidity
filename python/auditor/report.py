import json
from python.auditor.sol_file_folder import ContractFolder
from auditor.fs import write_text_file


class Report:
    def __init__(self, cf: ContractFolder) -> None:
        self.cf = cf
        self.items = []

    def add_item(self, fn: str, rule_category: str, rule: str, violate: bool):
        self.items.append(
            {
                "function": fn,
                "rule_type": rule_category,
                "rule": rule,
                "violate": violate,
            }
        )

    def dump(self, filepath: str):
        text = json.dumps(self.items)
        write_text_file(filepath, text)
