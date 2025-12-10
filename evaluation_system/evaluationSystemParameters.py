"""
Author: Rossana Antonella Sacco
"""

import json
import jsonschema
import os

class EvaluationSystemParameters:
    """
    This class is used to store and manage the parameters of the Evaluation System.
    """

    # Local parameters paths
    LOCAL_PARAMETERS_PATH = "params/evaluationSystemParam.json"
    LOCAL_PARAMETERS_SCHEMA_PATH = "schema/evaluationSystemParamsSchema.json"
    LOCAL_PARAMETERS = {}

    # Global parameters paths
    GLOBAL_PARAMETERS_PATH = "params/netConf.json"
    GLOBAL_PARAMETERS_SCHEMA_PATH = "schema/netConfSchema.json"
    GLOBAL_PARAMETERS = {}

    # Static class attributes for easy access in Orchestrator
    # They are used to avoid accessing the dictionary every time
    # They are initialized with default values, which can be overridden by the loaded parameters
    min_number_labels = 100
    total_errors = 5
    max_consecutive_errors = 3

    @staticmethod
    def loadParameters(basedir: str = "."):
        """
        Loads the parameters from JSON files and validates them against schemas.
        Also populates static class attributes for easier access.

        :param basedir: The base directory for file lookup.
        """

        try:
            #Load Local Parameters (Thresholds)
            local_path = os.path.join(basedir, EvaluationSystemParameters.LOCAL_PARAMETERS_PATH)
            with open(local_path, "r") as local_params:
                EvaluationSystemParameters.LOCAL_PARAMETERS = json.load(local_params)

                if not EvaluationSystemParameters._validate_json(EvaluationSystemParameters.LOCAL_PARAMETERS, "local", basedir):
                    print("Error: Invalid local parameters.")
                    return

                # Map dictionary values to class attributes for easy access in Orchestrator
                EvaluationSystemParameters.min_number_labels = EvaluationSystemParameters.LOCAL_PARAMETERS.get("min_number_labels")
                EvaluationSystemParameters.total_errors = EvaluationSystemParameters.LOCAL_PARAMETERS.get("total_errors")
                EvaluationSystemParameters.max_consecutive_errors = EvaluationSystemParameters.LOCAL_PARAMETERS.get("max_consecutive_errors")

            #Load Global Parameters (Network Config)
            global_path = os.path.join(basedir, EvaluationSystemParameters.GLOBAL_PARAMETERS_PATH)
            with open(global_path, "r") as global_params:
                EvaluationSystemParameters.GLOBAL_PARAMETERS = json.load(global_params)

                if not EvaluationSystemParameters._validate_json(EvaluationSystemParameters.GLOBAL_PARAMETERS, "global", basedir):
                    print("Error: Invalid global parameters.")
                    return
            
            print("Parameters loaded successfully.")

        except FileNotFoundError as e:
            print(f"Configuration file not found: {e}")
        except Exception as e:
            print(f"Error loading parameters: {e}")

    @staticmethod
    def _validate_json(json_parameters: dict, param_type: str, basedir: str = ".") -> bool:
        """
        Validate JSON parameters read from a file against their schema.
        """

        if param_type == "local":
            schema_path = os.path.join(basedir, EvaluationSystemParameters.LOCAL_PARAMETERS_SCHEMA_PATH)
        elif param_type == "global":
            schema_path = os.path.join(basedir, EvaluationSystemParameters.GLOBAL_PARAMETERS_SCHEMA_PATH)
        else:
            return False

        try:
            with open(schema_path, "r") as schema_file:
                schema = json.load(schema_file)
            
            jsonschema.validate(json_parameters, schema)
            return True
        except FileNotFoundError:
            print(f"Schema file not found: {schema_path}")
            return False
        except jsonschema.ValidationError as e:
            print(f"Schema validation error ({param_type}): {e.message}")
            return False