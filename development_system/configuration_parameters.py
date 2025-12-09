import os
from development_system.json_handler_validator import JsonHandlerValidator


class ConfigurationParameters:
    """Static class for configuration parameters of the development system"""
    def __new__(cls, *args, **kwargs):
        if cls is ConfigurationParameters:
            raise TypeError(f"'{cls.__name__}' cannot be instantiated")
        return object.__new__(cls, *args, **kwargs)
    
    params = {}

    @staticmethod
    def load_configuration():
        """Load configuration parameters from a JSON file."""
        THIS_DIR = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(THIS_DIR, "configuration", "dev_parameters.json")
        JsonHandlerValidator.validate_json(filepath, os.path.join(THIS_DIR, "schemas", "dev_parameters_schema.json"))
        ConfigurationParameters.params = JsonHandlerValidator.read_configuration_parameters(filepath)