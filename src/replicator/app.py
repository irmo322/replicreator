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
    print(parameters)  # TODO erase it

    check_parameters(parameters)
    check_transcriptions(parameters)
    generate_statistics(parameters)
    generate_web_app(parameters)


def check_parameters(parameters):
    """
    Checks if parameters are consistent and raises exceptions if not.
    :param parameters:
    :return:
    """
    # Checking that labels from characters and stage directions do not conflict with each other.
    char2labels = {}
    char2labels["stage directions"] = parameters["stage_directions"]["labels"]
    for i, character in enumerate(parameters["characters"]):
        char2labels[f"character {i}"] = character["labels"]
    label2char = {}
    for char, char_labels in char2labels.items():
        for label in char_labels:
            if label in label2char:
                raise RuntimeError(f"label {label} is present twice in {label2char[label]} and {char}.")
            label2char[label] = char


def check_transcriptions(parameters):
    # 2 - vérifier la cohérence des transcriptions, notamment vis-à-vis des paramètres
    pass  # TODO


def generate_statistics(parameters):
    # 3 - générer les statistiques
    pass  # TODO


def generate_web_app(parameters):
    # 4 - générer la web app
    pass  # TODO
