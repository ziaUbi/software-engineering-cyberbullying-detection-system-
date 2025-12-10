import json
import os

from segregation_system.segregation_configuration import SegregationSystemJsonHandler

class SegregationSystemConfiguration:
    GLOBAL_PARAMETERS = {}
    LOCAL_PARAMETERS = {}

    @staticmethod
    def configure_parameters(base_dir="."):
        # Carica configurazione globale di rete
        try:
            with open(os.path.join(base_dir, "configuration", "netconf.json"), "r") as f:
                SegregationSystemConfiguration.GLOBAL_PARAMETERS = json.load(f)
        except FileNotFoundError:
            print("[Config] netconf.json not found.")

        try:
            with open(os.path.join(base_dir, "configuration", "segregation_parameters.json"), "r") as f:
                SegregationSystemConfiguration.LOCAL_PARAMETERS = json.load(f)
        except FileNotFoundError:
            print("[Config] segregation_parameters.json not found. Using defaults.")
            # Default fallback
            SegregationSystemConfiguration.LOCAL_PARAMETERS = {
                "min_sessions_for_processing": 2000,
                "balancing_report_threshold": 0.05,
                "minimum_coverage_report_threshold": 100,
                "number_of_record_of_session": 4,
                "training_set_percentage": 0.70,
                "validation_set_percentage": 0.20,
                "test_set_percentage": 0.10
            }





class SegregationSystemConfiguration:
    # Local parameters
    LOCAL_PARAMETERS_PATH = "conf/segregation_system_configuration.json"
    LOCAL_PARAMETERS_SCHEMA_PATH = "conf/segregationSystemConfigurationSchema.json"
    LOCAL_PARAMETERS = {} # A Dict object.

    # Global parameters
    GLOBAL_PARAMETERS_PATH = "conf/global_netconf.json"
    GLOBAL_PARAMETERS_SCHEMA_PATH = "conf/global_netconf_schema.json"
    GLOBAL_PARAMETERS = {} # A Dict object.

    @staticmethod
    def configure_parameters(local_file_path = LOCAL_PARAMETERS_PATH , global_file_path = GLOBAL_PARAMETERS_PATH) -> None:
        """
        Initializes the `SegregationSystemConfiguration` instance with configuration values from a JSON file.

        Args:
            file_path (str): The path to the JSON configuration file. Defaults to "conf/segregation_system_configuration.json".

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            KeyError: If any required key is missing in the JSON file.
            ValueError: If any value type is incorrect.
        """

        if SegregationSystemConfiguration.validate_json():
            # Extract and assign values to instance variables
            try:
                SegregationSystemConfiguration.LOCAL_PARAMETERS = SegregationSystemJsonHandler.read_json_file(local_file_path)
                SegregationSystemConfiguration.GLOBAL_PARAMETERS = SegregationSystemJsonHandler.read_json_file(global_file_path)
            except KeyError as e:
                raise KeyError(f"Missing required configuration key: {e}")
            except ValueError:
                raise ValueError("One or more values in the configuration file are of the wrong type.")
        else:
            print("Configuration files are not valid.")

    @staticmethod
    def validate_json() -> bool:
        """
        Validate JSON parameters read from a file.

        :param json_parameters: The JSON parameters to validate.
        :param param_type: The type of the parameters (local or global).
        :param basedir: The base directory from which to look for the different parameters files.
        :return: True if the JSON parameters are valid, False otherwise.
        """
        resp1 = SegregationSystemJsonHandler.validate_json_from_path(SegregationSystemConfiguration.LOCAL_PARAMETERS_PATH , SegregationSystemConfiguration.LOCAL_PARAMETERS_SCHEMA_PATH)
        resp2 = SegregationSystemJsonHandler.validate_json_from_path(SegregationSystemConfiguration.GLOBAL_PARAMETERS_PATH , SegregationSystemConfiguration.GLOBAL_PARAMETERS_SCHEMA_PATH)
        return resp1 and resp2