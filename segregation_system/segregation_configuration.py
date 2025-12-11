import json
import os

from segregation_system.segregation_json_handler import SegregationSystemJsonHandler

class SegregationSystemConfiguration:
    GLOBAL_PARAMETERS = {}
    LOCAL_PARAMETERS = {}

    @staticmethod
    def load_parameters(base_dir="segregation_system"):
        # Load global parameters
        GLOBAL_PATH = base_dir + "/configuration/netconf.json"
        GLOBAL_SCHEMA_PATH = base_dir + "/schemas/netconf_schema.json"
        try:
            with open(GLOBAL_PATH, "r") as f:
                if SegregationSystemJsonHandler.validate_json_from_path(GLOBAL_PATH, GLOBAL_SCHEMA_PATH):
                    SegregationSystemConfiguration.GLOBAL_PARAMETERS = json.load(f)
        except FileNotFoundError:
            print("[Config] netconf.json not found.")

        # Load local parameters
        LOCAL_PATH = base_dir + "/configuration/segregation_parameters.json"
        LOCAL_SCHEMA_PATH = base_dir + "/schemas/segregation_parameter_schema.json"
        try:
            with open(LOCAL_PATH, "r") as f:
                if SegregationSystemJsonHandler.validate_json_from_path(LOCAL_PATH, LOCAL_SCHEMA_PATH):
                    SegregationSystemConfiguration.LOCAL_PARAMETERS = json.load(f)
        except FileNotFoundError:
            print("[Config] segregation_parameters.json not found.")