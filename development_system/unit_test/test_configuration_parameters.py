from development_system.configuration_parameters import ConfigurationParameters


def test_configuration_parameters_is_static():
    # Instantiation should be blocked
    try:
        ConfigurationParameters()  # type: ignore
        assert False, "ConfigurationParameters should not be instantiable"
    except TypeError:
        assert True


def test_load_configuration_calls_validator(monkeypatch):
    calls = {"validate": 0, "read": 0}

    def fake_validate_json(json_file, schema_file):
        calls["validate"] += 1
        # return value is not used
        return True

    def fake_read_config(filepath):
        calls["read"] += 1
        return {"service_flag": False, "min_layers": 1, "max_layers": 1, "step_layers": 1,
                "min_neurons": 1, "max_neurons": 1, "step_neurons": 1,
                "validation_tolerance": 0.1, "test_tolerance": 0.1}

    # Patch the underlying validator methods used by load_configuration
    import development_system.configuration_parameters as cp

    monkeypatch.setattr(cp.JsonHandlerValidator, "validate_json", fake_validate_json)
    monkeypatch.setattr(cp.JsonHandlerValidator, "read_configuration_parameters", fake_read_config)

    ConfigurationParameters.params = {}
    ConfigurationParameters.load_configuration()

    assert calls["validate"] == 1
    assert calls["read"] == 1
    assert ConfigurationParameters.params["service_flag"] is False
