import json
import logging
import jsonschema

class JsonHandler:
    """
    A class to read and save json files.
    """

    def read_json_file(self, filepath):
        """
        Read a json file.

        Returns:
            filecontent: content of json file or None if error.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                filecontent = json.load(f)
            return filecontent

        except Exception as e:
            print(f"Error reading file at path {filepath}: {e}")
            return None

    def validate_json(self, json_data: dict, schema_path: str) -> bool:
        """
        Validate a json object against a json schema in a file.
        :param json_data: json object
        :param schema_path: path to the json schema
        :return: True if json object is valid, False otherwise
        """
        try:
            with open(schema_path, "r", encoding="UTF-8") as file:
                json_schema = json.load(file)
            
            jsonschema.validate(instance=json_data, schema=json_schema)
            return True

        except FileNotFoundError:
            logging.error(f"Schema file not found at: {schema_path}")
            return False
            
        except json.JSONDecodeError:
            logging.error(f"Schema file at {schema_path} is not valid JSON.")
            return False

        except jsonschema.exceptions.ValidationError as ex:
            logging.error(f"JSON Validation Error: {ex.message}")
            return False
            
        except Exception as e:
            logging.error(f"Unexpected error during validation: {e}")
            return False