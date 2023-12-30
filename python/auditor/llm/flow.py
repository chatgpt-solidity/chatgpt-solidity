import yaml


class LLMFlow:
    def __init__(self, type_, flows, examples):
        self.type = type_
        self.flows = flows
        self.examples = examples

    @classmethod
    def from_dict(cls, data):
        return cls(
            type_=data["type"], flows=data["flows"], examples=data.get("examples", [])
        )

    def __repr__(self):
        return (
            f"LLMFlow(type={self.type}, flows={self.flows}, examples={self.examples})"
        )


def read_llm_flow_from_file(file_path) -> LLMFlow:
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    return LLMFlow.from_dict(data)
