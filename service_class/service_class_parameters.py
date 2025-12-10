import json
import jsonschema

class ServiceClassParameters:
    """
    This class is used to store the parameters of the Service Class.
    """

    # Local parameters
    LOCAL_PARAMETERS_PATH = "configuration/service_class_parameters.json"
    LOCAL_PARAMETERS_SCHEMA_PATH = "schemas/service_class_parameters_schema.json"
    LOCAL_PARAMETERS = {}

    # Global parameters
    GLOBAL_PARAMETERS_PATH = "configuration/netconf.json"
    GLOBAL_PARAMETERS_SCHEMA_PATH = "schemas/netconf_schema.json"
    GLOBAL_PARAMETERS = {}

    @staticmethod
    def loadParameters(basedir: str = "."):
        """
        This method is used to load the parameters of the Service Class.

        :param basedir: The base directory from which to look for the different parameters files.
        """

        try:
            with open(f"{basedir}/{ServiceClassParameters.LOCAL_PARAMETERS_PATH}", "r") as local_params:
                ServiceClassParameters.LOCAL_PARAMETERS = json.load(local_params)

                if not ServiceClassParameters._validate_json(ServiceClassParameters.LOCAL_PARAMETERS, "local", basedir):
                    print("Invalid local parameters.")

                with open(f"{basedir}/{ServiceClassParameters.GLOBAL_PARAMETERS_PATH}", "r") as global_params:
                    ServiceClassParameters.GLOBAL_PARAMETERS = json.load(global_params)

                    if not ServiceClassParameters._validate_json(ServiceClassParameters.GLOBAL_PARAMETERS, "global", basedir):
                        print("Invalid global parameters.")

        except Exception as e:
            print(f"Error loading parameters: {e}")

    @staticmethod
    def _validate_json(json_parameters: dict, param_type: str, basedir: str = ".") -> bool:
        """
        Validate JSON parameters read from a file.

        :param json_parameters: The JSON parameters to validate.
        :param param_type: The type of parameters to validate (local or global).
        :param basedir: The base directory from which to look for the different parameters files.
        :return: True if the JSON parameters are valid, False otherwise.
        """

        if param_type == "local":
            schema_path = f"{basedir}/{ServiceClassParameters.LOCAL_PARAMETERS_SCHEMA_PATH}"
        elif param_type == "global":
            schema_path = f"{basedir}/{ServiceClassParameters.GLOBAL_PARAMETERS_SCHEMA_PATH}"
        else:
            return False
        
        with open(schema_path, "r") as schema_file:
            schema = json.load(schema_file)

        try:
            jsonschema.validate(json_parameters, schema)
            return True
        except jsonschema.ValidationError as e:
            if param_type == "local":
                print(f"Invalid JSON local parameters: {e}")
            elif param_type == "global":
                print(f"Invalid JSON global parameters: {e}")
            return False