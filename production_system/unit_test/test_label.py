import json
from production_system.label import Label

def test_label_serialization():
    label = Label(uuid="123-abc", label="cyberbullying")
    
    # Test to_dictionary
    d = label.to_dictionary()
    assert d["uuid"] == "123-abc"
    assert d["label"] == "cyberbullying"
    
    # Test to_json_string
    json_str = label.to_json_string()
    loaded = json.loads(json_str)
    assert loaded == d