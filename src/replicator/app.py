from .util.parameters_loading import load_parameters_yaml

from pathlib import Path


_RES_FOLDER_PATH = Path(__file__).parent / "../../res"

_parameters_schema = {"type": "dict", "schema": {
    "stage_directions": {"type": "dict", "schema": {
        "labels": {"type": "list", "schema": {'type': 'string'}}
    }},

    "characters": {"type": "list", "schema": {'type': 'dict', 'schema': {
        "labels": {"type": "list", "schema": {'type': 'string'}}
    }}},

    "scenes": {"type": "list", "schema": {'type': 'dict', 'schema': {
        "menu_name": {"type": "string"},
        "file_path": {"type": "string"}
    }}},

    "output": {"type": "dict", "schema": {
        "web_app": {"type": "dict", "schema": {
            "file_path": {"type": "string"}
        }},
        "statistics": {"type": "dict", "schema": {
            "file_path": {"type": "string"}
        }}
    }}
}}


def process_parameters_file(parameters_file_path):
    parameters = load_parameters_yaml(parameters_file_path, _parameters_schema)
    process_parameters(parameters)


def process_parameters(parameters):
    print(parameters)


