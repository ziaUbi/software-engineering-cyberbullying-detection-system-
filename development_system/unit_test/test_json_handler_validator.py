import json
from pathlib import Path

import pytest

from development_system.json_handler_validator import JsonHandlerValidator


def test_dict_to_string_and_back_roundtrip():
    d = {"a": 1, "b": [1, 2, 3], "c": {"x": "y"}}
    s = JsonHandlerValidator.dict_to_string(d)
    assert isinstance(s, str)
    out = JsonHandlerValidator.string_to_dict(s)
    assert out == d


def test_string_to_dict_raises_on_invalid_json():
    with pytest.raises(ValueError):
        JsonHandlerValidator.string_to_dict("{not valid json}")


def test_validate_json_missing_file_raises(tmp_path: Path):
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps({"type": "object"}))

    with pytest.raises(ValueError) as e:
        JsonHandlerValidator.validate_json(str(tmp_path / "missing.json"), str(schema))

    assert "File not found" in str(e.value)


def test_read_configuration_parameters_happy_path(tmp_path: Path):
    # Minimal config file matching what read_configuration_parameters expects
    config = {
        "layers": {"min_layers": 1, "max_layers": 3, "step_layers": 1},
        "neurons": {"min_neurons": 4, "max_neurons": 8, "step_neurons": 2},
        "tolerance": {"validation_tolerance": 0.2, "test_tolerance": 0.1},
        "service_flag": False,
    }
    fp = tmp_path / "dev_parameters.json"
    fp.write_text(json.dumps(config))

    params = JsonHandlerValidator.read_configuration_parameters(str(fp))

    assert params["min_layers"] == 1
    assert params["max_layers"] == 3
    assert params["step_layers"] == 1
    assert params["min_neurons"] == 4
    assert params["max_neurons"] == 8
    assert params["step_neurons"] == 2
    assert params["validation_tolerance"] == 0.2
    assert params["test_tolerance"] == 0.1
    assert params["service_flag"] is False
