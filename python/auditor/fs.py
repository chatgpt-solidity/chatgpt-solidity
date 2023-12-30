from typing import Dict
import json
import yaml


def read_json_file(jsonfp) -> Dict:
    with open(jsonfp, "r") as f:
        obj = json.load(f)
    return obj


def write_json_file(fp, obj):
    with open(fp, "w") as f:
        json.dump(obj, f, indent=4)


def read_yaml_file(fp) -> Dict:
    with open(fp, "r") as f:
        obj = yaml.unsafe_load(f)
    return obj


def read_text_file(textfp) -> str:
    with open(textfp, "r") as f:
        return f.read()


def write_text_file(fp: str, text: str):
    with open(fp, "w") as f:
        f.write(text)

    print(f"[+] {fp}")
