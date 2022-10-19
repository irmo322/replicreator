from .util.parameters_loading import load_parameters_yaml

from pathlib import Path
import csv


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
        "file_path": {"type": "path", "coerce": "join_base"}
    }}},

    "version": {"type": "string"},

    "output": {"type": "dict", "schema": {
        "web_app": {"type": "dict", "schema": {
            "file_path": {"type": "path", "coerce": "join_base"}
        }},
        "statistics": {"type": "dict", "schema": {
            "file_path": {"type": "path", "coerce": "join_base"}
        }}
    }}
}}


def process_parameters_file(parameters_file_path):
    parameters = load_parameters_yaml(parameters_file_path, _parameters_schema)
    process_parameters(parameters)


def process_parameters(parameters):
    print(parameters)  # TODO erase it

    check_parameters(parameters)

    all_lines = [load_lines(scene["file_path"]) for scene in parameters["scenes"]]

    check_transcriptions(parameters, all_lines)
    statistics = compute_statistics(parameters, all_lines)
    save_statistics(parameters, statistics)
    generate_web_app(parameters)


def check_parameters(parameters):
    """
    Checks if parameters are consistent and raises exceptions if not.
    :param parameters:
    :return:
    """
    # Checking that labels from characters and stage directions do not conflict with each other.
    char2labels = {"stage directions": parameters["stage_directions"]["labels"]}
    for i, character in enumerate(parameters["characters"]):
        char2labels[f"character {i}"] = character["labels"]
    label2char = {}
    for char, char_labels in char2labels.items():
        for label in char_labels:
            if label in label2char:
                raise RuntimeError(f"label {label} is present twice in {label2char[label]} and {char}.")
            label2char[label] = char


def check_transcriptions(parameters, all_lines):
    """
    Checks transcriptions consistency.
    :param parameters:
    :param all_lines:
    :return:
    """
    # Checking that characters labels in transcriptions are not unknown.
    stage_directions_labels = set(parameters["stage_directions"]["labels"])
    all_character_labels = set.union(*[set(character["labels"]) for character in parameters["characters"]])

    for i, (scene, lines) in enumerate(zip(parameters["scenes"], all_lines)):
        for block in lines:
            if stage_directions_labels.intersection(block["characters"]) and len(block["characters"]) > 1:
                raise RuntimeError(f"Invalid set of characters {block['characters']} in scene {scene}")
            for character in block["characters"]:
                if character not in stage_directions_labels and character not in all_character_labels:
                    raise RuntimeError(f"Unknown character {character} in scene {scene}.")


def compute_statistics(parameters, all_lines):
    stage_directions_labels = set(parameters["stage_directions"]["labels"])
    label2main = {}
    main_character_labels = []
    for character in parameters["characters"]:
        main_label = character["labels"][0]
        main_character_labels.append(main_label)
        for label in character["labels"]:
            label2main[label] = main_label

    statistics = []
    for i, (scene, lines) in enumerate(zip(parameters["scenes"], all_lines)):
        scene_statistics = {char: {"lines": 0, "words": 0, "alphanum_chars": 0} for char in main_character_labels}
        for block in lines:
            for line in block['lines']:
                clean_line = "".join([c if c.isalnum() else " " for c in remove_inline_stage_directions(line)])
                n_words = len(clean_line.split())
                n_alphanum_chars = sum(c.isalnum() for c in clean_line)
                for character in block["characters"]:
                    if character not in stage_directions_labels:
                        char_stats = scene_statistics[label2main[character]]
                        char_stats["lines"] += 1
                        char_stats["words"] += n_words
                        char_stats["alphanum_chars"] += n_alphanum_chars
        statistics.append(scene_statistics)

    return statistics


def save_statistics(parameters, statistics):
    main_character_labels = list(statistics[0].keys())
    with open(parameters["output"]["statistics"]["file_path"], 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["scene name"] +
                        [char + " " + kind
                         for char in main_character_labels
                         for kind in ["lines", "words", "alphanum_chars"]])
        for scene_statistics, scene in zip(statistics, parameters["scenes"]):
            writer.writerow([scene["menu_name"]] +
                            [scene_statistics[char][kind]
                             for char in main_character_labels
                             for kind in ["lines", "words", "alphanum_chars"]])


def generate_web_app(parameters):
    # 4 - générer la web app
    pass  # TODO


def load_lines(transcription_file_path):
    with open(transcription_file_path) as f:
        file_lines = [line.strip() for line in f.readlines()]

    theatrical_lines = []
    new_character = True
    for file_line in file_lines:
        if not file_line:
            new_character = True
        elif file_line[0] != "#":
            if new_character:
                block_characters = [w.strip() for w in file_line.split(",")]
                theatrical_lines.append({"characters": block_characters, "lines": []})
                new_character = False
            else:
                theatrical_lines[-1]["lines"].append(file_line)

    return theatrical_lines


def remove_inline_stage_directions(line):
    clean_line_chunks = []
    while line:
        if line[0] == "(":
            end = line.find(")")
            if end == -1:
                len(line) - 1
            line = line[end + 1:]
        else:
            begin = line.find("(")
            if begin == -1:
                begin = len(line)
            clean_line_chunks.append(line[:begin])
            line = line[begin:]
    return "".join(clean_line_chunks)
