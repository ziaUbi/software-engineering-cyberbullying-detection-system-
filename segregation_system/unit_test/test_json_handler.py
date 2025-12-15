import json
import pytest
from segregation_system.segregation_json_handler import SegregationSystemJsonHandler

def test_read_write_field_roundtrip(tmp_path):
    """Tests reading and writing a specific field in a JSON file."""
    p = tmp_path / "test_state.json"
    p.write_text(json.dumps({"service_flag": False, "status": "-"}), encoding="utf-8")
    path_str = str(p)

    val = SegregationSystemJsonHandler.read_field_from_json(path_str, "service_flag")
    assert val is False

    success = SegregationSystemJsonHandler.write_field_to_json(path_str, "status", "OK")
    assert success is True
    
    new_val = SegregationSystemJsonHandler.read_field_from_json(path_str, "status")
    assert new_val == "OK"

def test_string_dict_conversion():
    original_dict = {"ip": "127.0.0.1", "port": 8080}
    
    # Dict -> String
    s = SegregationSystemJsonHandler.dict_to_string(original_dict)
    assert isinstance(s, str)
    
    # String -> Dict
    recovered_dict = SegregationSystemJsonHandler.string_to_dict(s)
    assert recovered_dict == original_dict

    with pytest.raises(ValueError):
        SegregationSystemJsonHandler.string_to_dict("invalid json string")

def test_validate_json_schema(project_root):
    schema_path = project_root / "segregation_system" / "schemas" / "prepared_session_schema.json"
    input_path = project_root / "segregation_system" / "inputs" / "prepared_session.json"
    
    with open(input_path, "r", encoding="utf-8") as f:
        valid_data = json.load(f)
        
    assert SegregationSystemJsonHandler.validate_json(valid_data, str(schema_path)) is True

    # Creates an invalid data by removing a required field
    invalid_data = valid_data.copy()
    del invalid_data["uuid"]
    
    assert SegregationSystemJsonHandler.validate_json(invalid_data, str(schema_path)) is False
