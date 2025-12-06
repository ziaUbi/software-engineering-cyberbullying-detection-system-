"""
Author: Martina Fabiani
"""
import json
import logging

import jsonschema

class JsonHandler:
    """
        A class to read and save file json
    """

    def read_json_file(self, filepath):
        """
        Read a json file.

        Returns:
            filecontent: content of json file.
        """

        try:
            with open(filepath, "r") as f:
                filecontent = json.load(f)
            return filecontent

        except Exception as e:
            print("Error to read file at path " + filepath + ": " + e)
            return None

    # validate Json sent as a python dictionary
    def validate_json(self, json_data: dict, schema_path: str) -> bool:
        """
            Validate a json object against a json schema in a file.
            :param json_data: json object
            :param schema_path: path to the json schema relative to the data folder
            :return: True if json object is valid, False otherwise
            """
        with open(schema_path, "r", encoding="UTF-8") as file:
            json_schema = json.load(file)
        try:
            jsonschema.validate(instance=json_data, schema=json_schema)
        except jsonschema.exceptions.ValidationError as ex:
            logging.error(ex)
            return False
        return True