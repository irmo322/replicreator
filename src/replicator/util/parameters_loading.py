import cerberus

import yaml
import os
from pathlib import Path


class CustomValidator(cerberus.Validator):
    types_mapping = cerberus.Validator.types_mapping.copy()
    types_mapping["path"] = cerberus.TypeDefinition("path", (Path,), ())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = Path(kwargs["base_path"])

    def _normalize_coerce_join_base_path(self, value):
        return str(self.base_path / value)

    def _normalize_coerce_join_base(self, value):
        return self.base_path / value

    def _normalize_coerce_keep_raw_path(self, value):
        return Path(value)


def validate_parameters(raw_parameters, schema, base_path="."):
    """
    Validate parameters using given cerberus-like schema.
    Contrary to official cerberus schema which assumes that document's root is a dict,
    the given schema MUST define the root type which can be of any kind supported by cerberus.
    :param raw_parameters:
    :param schema:  a cerberus-like schema describing parameters data.
    :param base_path: base path used for normalizing path.
    :return: the validated parameters
    """
    schema_with_root = {'root': schema}
    raw_parameters_with_root = {'root': raw_parameters}
    parameters_validator = CustomValidator(base_path=base_path, schema=schema_with_root, require_all=True)
    if parameters_validator.validate(raw_parameters_with_root):
        validated_parameters = parameters_validator.document["root"]
    else:
        raise RuntimeError(f"Bad parameters: {parameters_validator.errors}")

    return validated_parameters


def load_parameters_yaml(parameters_file_path, schema):
    """
    Load and check parameters from given yaml file.
    Check this for the schema https://docs.python-cerberus.org
    :param parameters_file_path:
    :param schema: a cerberus schema describing parameters data.
    :return: validated parameters
    """
    # Load yaml file and validate it
    with open(parameters_file_path, 'r', encoding="utf8") as f:
        raw_parameters = yaml.load(f.read(), Loader=yaml.SafeLoader)

    try:
        validated_parameters = validate_parameters(
            raw_parameters, schema, base_path=os.path.dirname(parameters_file_path))
    except RuntimeError as e:
        raise RuntimeError(f"Unable to validate parameters from file {parameters_file_path}\n{e}")

    return validated_parameters
