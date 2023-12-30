from auditor.fs import read_text_file, read_yaml_file
import os

from python.auditor.llm.flow import read_llm_flow_from_file

ERCS_DIR = os.path.join(os.path.dirname(__file__), "../rules")
FLOWS_DIR = os.path.join(os.path.dirname(__file__), "../flows")
FULL_ERCS_DIR = os.path.join(os.path.dirname(__file__), "../erc")

ERCS = {
    "20": read_yaml_file(os.path.join(ERCS_DIR, "erc20.yaml")),
    "721": read_yaml_file(os.path.join(ERCS_DIR, "erc721.yaml")),
    "1155": read_yaml_file(os.path.join(ERCS_DIR, "erc1155.yaml")),
}

FULL_ERCS = {"20": read_text_file(os.path.join(FULL_ERCS_DIR, "20"))}

NOCM_TEMPLATES = {
    "check": read_llm_flow_from_file(os.path.join(FLOWS_DIR, "nocm", "check.yaml")),
    "event": read_llm_flow_from_file(os.path.join(FLOWS_DIR, "nocm", "event.yaml")),
}

NOOS_TEMPLATES = {
    "event-cond": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "noos", "event-cond.yaml")
    ),
    "event": read_llm_flow_from_file(os.path.join(FLOWS_DIR, "noos", "event.yaml")),
    "throw": read_llm_flow_from_file(os.path.join(FLOWS_DIR, "noos", "throw.yaml")),
    "throw-unless": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "noos", "throw-unless.yaml")
    ),
}

SPECIALIZED_TEMPLATES = {
    "check": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "check.yaml")
    ),
    "check-cond": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "check-cond.yaml")
    ),
    "throw": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "throw.yaml")
    ),
    "throw-not": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "throw-not.yaml")
    ),
    "throw-unless": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "throw-unless.yaml")
    ),
    "event": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "event.yaml")
    ),
    "event-cond": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "event-cond.yaml")
    ),
    "event-assign": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "event-assign.yaml")
    ),
    "event-assign-cond": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "event-assign-cond.yaml")
    ),
    "return": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "return.yaml")
    ),
    "call": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "call.yaml")
    ),
    "call-cond": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "call-cond.yaml")
    ),
    "assign": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "assign.yaml")
    ),
    "signature": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "signature.yaml")
    ),
    "esignature": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "specialized", "esignature.yaml")
    ),
}

UNIVERSAL_TEMPLATE = read_llm_flow_from_file(
    os.path.join(FLOWS_DIR, "universal", "flow.yaml")
)

UNIVERSAL_COND_TEMPLATE = read_llm_flow_from_file(
    os.path.join(FLOWS_DIR, "universal", "flow-cond.yaml")
)

FULLERC_TEMPLATES = {
    "function": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "fullerc", "function.yaml")
    ),
    "interface": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "fullerc", "interface.yaml")
    ),
    "einterface": read_llm_flow_from_file(
        os.path.join(FLOWS_DIR, "fullerc", "einterface.yaml")
    ),
}
