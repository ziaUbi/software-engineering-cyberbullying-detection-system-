import json
from pathlib import Path

import pytest

from segregation_system.segregation_json_handler import SegregationSystemJsonHandler


def test_read_write_field_roundtrip(tmp_path: Path):
    p = tmp_path / "state.json"
    p.write_text(json.dumps({"a": 1, "b": "-"}), encoding="utf-8")

    assert SegregationSystemJsonHandler.read_field_from_json(str(p), "a") == 1
    assert SegregationSystemJsonHandler.write_field_to_json(str(p), "b", "OK") is True
    assert SegregationSystemJsonHandler.read_field_from_json(str(p), "b") == "OK"


def test_string_dict_conversion():
    d = {"x": 1, "y": ["a", "b"]}
    s = SegregationSystemJsonHandler.dict_to_string(d)
    assert isinstance(s, str)
    assert SegregationSystemJsonHandler.string_to_dict(s) == d

    with pytest.raises(ValueError):
        SegregationSystemJsonHandler.string_to_dict("not json")


def test_validate_json_against_schema(project_root: Path):
    schema_path = project_root / "segregation_system" / "schemas" / "prepared_session_schema.json"
    valid = json.loads((project_root / "segregation_system" / "inputs" / "prepared_session.json").read_text(encoding="utf-8"))
    assert SegregationSystemJsonHandler.validate_json(valid, str(schema_path)) is True

    invalid = dict(valid)
    invalid.pop("uuid")
    assert SegregationSystemJsonHandler.validate_json(invalid, str(schema_path)) is False
