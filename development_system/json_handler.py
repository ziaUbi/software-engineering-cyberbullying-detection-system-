import json
from typing import Any

from jsonschema import validate, ValidationError, SchemaError


class JsonValidatorReaderAndWriter:
    """
        A class to validate, read and save file json
    """

    @staticmethod
    def validate_json(json_file: str, schema_file: str) -> bool:
        """
        Validate a JSON file against a JSON schema.

        :param json_file: Path to the JSON file to validate.
        :param schema_file: Path to the JSON schema file.
        :return: True if the JSON is valid.
        :raises ValueError: If the JSON is not valid.
        """
        try:
            # Load JSON data
            with open(json_file, 'r') as Jf:
                json_data = json.load(Jf)

            # Load JSON schema
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
    def read_configuration_parameters(filepath):
        """
        Read a json file that contains the parameters.

        Returns:
            file_content: content of json file.

        """
        params = {}
        try:
            with open(filepath, "r") as f:
                file_content = json.load(f)

            layers = file_content.get('layers', {})
            neurons = file_content.get('neurons', {})
            tolerance = file_content.get('tolerance', {})

            params["min_layers"] = layers.get('min_layers')
            params["max_layers"] = layers.get('max_layers')
            params["step_layers"] = layers.get('step_layers')
            params["min_neurons"] = neurons.get('min_neurons')
            params["max_neurons"] = neurons.get('max_neurons')
            params["step_neurons"] = neurons.get('step_neurons')
            params["overfitting_tolerance"] = tolerance.get('overfitting_tolerance')
            params["generalization_tolerance"] = tolerance.get('generalization_tolerance')
            params["service_flag"] = file_content.get('service_flag')

            return params

        except Exception as ex:
            print("Error to read file at path " + filepath + str(ex))
            return None

    @staticmethod
    def read_json_file(filepath):
        """
            Read a generic json file.

            Returns:
                file_content: content of json file.

        """
        try:
            with open(filepath, "r") as f:
                file_content = json.load(f)
            return file_content

        except Exception as e:
            print("Error to read file at path " + filepath + ": " + str(e))
            return None

    @staticmethod
    def write_json_file(data, filepath):
        """
            Args:
                data: data to write into json file
                filepath: path where json file will be saved.

            Returns:
                bool: True if the file is written successfully, False otherwise.
        """

        try:
            with open(filepath, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                return True
        except Exception as e:
            print("Error to save file at path " + filepath + ": " + str(e))
            return False

    def get_system_address(self , json_filepath: str, system_name: str) -> Any | None:
        """
        Reads the IP address and port of a specified system from a JSON file.

        Args:
            json_filepath (str): Path to the JSON file containing system configurations.
            system_name (str): Name of the system whose address is to be fetched.

        Returns:
            dict: A dictionary containing the IP address and port of the specified system.
                  Example: {"ip": "192.168.149.66", "port": 8001}
            None: If the system name is not found or an error occurs.
        """
        try:
            # Load the JSON file
            systems_data = self.read_json_file(json_filepath)

            # Fetch the system configuration
            system_info = systems_data.get(system_name)
            if system_info:
                return system_info
            else:
                print(f"System '{system_name}' not found in the configuration file.")
                return None

        except FileNotFoundError:
            print(f"Error: File '{json_filepath}' not found.")
            return None
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON file.")
            return None

    @staticmethod
    def string_to_dict(string: str) -> dict:
        """
        Converts a JSON-formatted string back to a dictionary.

        Args:
            string (str): The JSON string to convert.

        Returns:
            dict: The dictionary representation of the string.
        """
        try:
            return json.loads(string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Unable to parse string into dictionary: {e}")

    @staticmethod
    def dict_to_string(dictionary: dict) -> str:
        """
        Converts a dictionary to a JSON-formatted string.

        Args:
            dictionary (dict): The dictionary to convert.

        Returns:
            str: A JSON-formatted string representation of the dictionary.
        """
        try:
            return json.dumps(dictionary, indent=4)
        except TypeError as e:
            raise ValueError(f"Unable to convert dictionary to string: {e}")