from typing import Dict, List





def fill_template(template: str, **kwargs):
    for key, value in kwargs.items():
        template = template.replace(f"<{key}>", value)

    return template




def get_event_interface_with_pname(event_name: str, event_params: List) -> str:

    # Constructing the interface string
    interface_string = f"event {event_name}("
    param_strings = [f"{param['type']}{' indexed' if param.get('indexed') else ''} {param['name']}" for param in event_params]
    interface_string += ", ".join(param_strings) + ");"

    return interface_string

def get_event_interface(event_name: str, event_params: List) -> str:

    # Constructing the interface string
    interface_string = f"event {event_name}("
    param_strings = [f"{param['type']}{' indexed' if param.get('indexed') else ''}" for param in event_params]
    interface_string += ", ".join(param_strings) + ");"

    return interface_string


def get_function_signature(fname:str, farg_types, fret):
    return (
                f"{fname}({','.join(farg_types)}) returns({fret})"
                if fret
                else f"{fname}({','.join(farg_types)}) returns()"
            )