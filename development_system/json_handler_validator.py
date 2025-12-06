import json
from typing import Any

from jsonschema import validate, ValidationError, SchemaError


class JsonHandlerValidator:
    """
        Static class to validate and handle JSON files.
    """
    def __new__(cls, *args, **kwargs):
        if cls is JsonHandlerValidator:
            raise TypeError(f"'{cls.__name__}' cannot be instantiated")
        return object.__new__(cls, *args, **kwargs)


    @staticmethod
    def validate_json(json_file: str, schema_file: str) -> bool:
        """
        Validate a JSON file against a JSON schema.

        :param json_file: Path to the JSON file to validate
        :param schema_file: Path to the JSON schema
        :returns Boolean: True if json_file is valid
        :raises ValueError: Raised if json_file is not valid
        """
        try:
            # Load JSON data and schema
            with open(json_file, 'r') as Jf:
                json_data = json.load(Jf)

            with open(schema_file, 'r') as Sf:
                json_schema = json.load(Sf)

            # Validate JSON against schema
            validate(instance=json_data, schema=json_schema)

            return True
            
        except ValidationError as e:
            raise ValueError(f"JSON validation failed: {e.message}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e.msg}")
        except FileNotFoundError as e:
            raise ValueError(f"File not found: {e.filename}")


    @staticmethod
    def read_json_file(filepath):
        """
            Read a generic json file

            :param filepath: path of json file
            :returns file_content: content of json file

        """
        try:
            with open(filepath, "r") as f:
                file_content = json.load(f)
            return file_content

        except Exception as e:
            print("Error to read file at path " + filepath + ": " + str(e))
            return None
        

    @staticmethod
    def read_configuration_parameters(filepath):
        """
        Read a json containing configuration parameters.

        :param filepath: path of json file
        :returns file_content: content of json file

        """
        params = {}
        try:
            file_content = JsonHandlerValidator.read_json_file(filepath)

            layers = file_content.get('layers')
            neurons = file_content.get('neurons')
            tolerance = file_content.get('tolerance')

            params["min_layers"] = layers.get('min_layers')
            params["max_layers"] = layers.get('max_layers')
            params["step_layers"] = layers.get('step_layers')
            params["min_neurons"] = neurons.get('min_neurons')
            params["max_neurons"] = neurons.get('max_neurons')
            params["step_neurons"] = neurons.get('step_neurons')
            params["validation_tolerance"] = tolerance.get('validation_tolerance')
            params["test_tolerance"] = tolerance.get('test_tolerance')
            params["service_flag"] = file_content.get('service_flag')

            return params

        except Exception as ex:
            print("Error to read config file at path " + filepath + str(ex))
            return None


    @staticmethod
    def get_system_ip_address(filepath: str, system_name: str) -> Any | None:
        """
        Reads the IP address and port of a specified system from a JSON file.

        :param json_filepath: Path to the JSON file containing system configurations
        :param system_name: Name of the system whose address is to be fetched

        :returns dict: A dictionary containing the IP address and port of the specified system.
                        Example: {"ip": "192.168.149.66", "port": 8001}
        :returns None: If the system name is not found or an error occurs.
        """
        try:
            # Load the JSON file
            systems_data = JsonHandlerValidator.read_json_file(filepath)

            # Fetch the system configuration
            system_info = systems_data.get(system_name)
            if system_info:
                return system_info
            else:
                print(f"System '{system_name}' not found in the configuration file.")
                return None

        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found.")
            return None
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON file.")
            return None


    @staticmethod
    def write_json_file(data, filepath):
        """
            :param data: data to write into json file
            :param filepath: path where json file will be saved

            :returns Boolean: True if the file is written successfully, False otherwise
        """
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                return True
        except Exception as e:
            print("Error to save file at path " + filepath + ": " + str(e))
            return False
        
        
    @staticmethod
    def string_to_dict(string: str) -> dict:
        """
        Converts a JSON-formatted string back to a dictionary.

        :param string: The JSON string to convert.

        :returns dict: The dictionary representation of the string.
        """
        try:
            return json.loads(string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Unable to parse string into dictionary: {e}")


    @staticmethod
    def dict_to_string(dictionary: dict) -> str:
        """
        Converts a dictionary to a JSON-formatted string.

        :param dictionary (dict): The dictionary to convert.

        :returns str: A JSON-formatted string representation of the dictionary.
        """
        try:
            return json.dumps(dictionary, indent=4)
        except TypeError as e:
            raise ValueError(f"Unable to convert dictionary to string: {e}")