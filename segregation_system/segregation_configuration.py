import json
import os

from segregation_system.segregation_configuration import SegregationSystemJsonHandler

class SegregationSystemConfiguration:
    GLOBAL_PARAMETERS = {}
    LOCAL_PARAMETERS = {}

    @staticmethod
    def load_parameters(base_dir="."):
        # Load global parameters
        GLOBAL_PATH = os.path.join(base_dir, "configuration", "netconf.json")
        try:
            with open(GLOBAL_PATH, "r") as f:
                if SegregationSystemJsonHandler.validate_json_from_path(GLOBAL_PATH, os.path.join(base_dir, "configuration", "netconf_schema.json")):
                    SegregationSystemConfiguration.GLOBAL_PARAMETERS = json.load(f)
        except FileNotFoundError:
            print("[Config] netconf.json not found.")

        # Load local parameters
        LOCAL_PATH = os.path.join(base_dir, "configuration", "segregation_parameters.json")
        try:
            with open(LOCAL_PATH, "r") as f:
                if SegregationSystemJsonHandler.validate_json_from_path(LOCAL_PATH, os.path.join(base_dir, "configuration", "segregation_parameters_schema.json")):
                    SegregationSystemConfiguration.LOCAL_PARAMETERS = json.load(f)
        except FileNotFoundError:
            print("[Config] segregation_parameters.json not found. Using defaults.")