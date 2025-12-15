import json
import logging
from typing import Any, Optional

import jsonschema

class SegregationSystemJsonHandler:
    @staticmethod
    def read_json_file(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)

        except Exception as e:
            print("Error to read file at path " + filepath + ": " + e)
            return None

    @staticmethod
    def write_json_file(data, filepath):
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                return True
        except Exception as e:
            print("Error to save file at path " + filepath + ": " + e)
            return False

    @staticmethod
    def write_field_to_json(file_path: str, field_name: str, value):
        try:
            data = SegregationSystemJsonHandler.read_json_file(file_path)
            data[field_name] = value
            return SegregationSystemJsonHandler.write_json_file(data, file_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return False
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {file_path}")
            return False

    @staticmethod
    def read_field_from_json(file_path: str, field_name: str):
        return SegregationSystemJsonHandler.read_json_file(file_path).get(field_name, None)

    @staticmethod
    def get_system_address(json_filepath: str, system_name: str) -> Optional[Any]:
        try:
            systems_data = SegregationSystemJsonHandler.read_json_file(json_filepath)
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
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    @staticmethod
    def validate_json(json_data: dict, schema_path: str) -> bool:
        with open(schema_path, "r", encoding="UTF-8") as file:
            json_schema = json.load(file)
        try:
            jsonschema.validate(instance=json_data, schema=json_schema)
        except jsonschema.exceptions.ValidationError as ex:
            logging.error(ex)
            return False
        return True

    @staticmethod
    def validate_json_from_path(json_path: str, schema_path: str) -> bool:
        with open(json_path, "r", encoding="UTF-8") as file:
            json_data = json.load(file)
        return SegregationSystemJsonHandler.validate_json(json_data, schema_path)

    @staticmethod
    def string_to_dict(string: str) -> dict:
        try:
            return json.loads(string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Unable to parse string into dictionary: {e}")

    @staticmethod
    def dict_to_string(dictionary: dict) -> str:
        try:
            return json.dumps(dictionary, indent=4)
        except TypeError as e:
            raise ValueError(f"Unable to convert dictionary to string: {e}")