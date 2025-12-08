"""
Module: ingestion_system_parameters
Loads and manages configuration parameters for the ingestion system.

Author: Francesco Taverna

"""
import sys

from ingestion_system import ING_MAN_CONFIG_FILE_PATH, ING_MAN_CONFIG_SCHEMA_FILE_PATH
from ingestion_system.json_handler import JsonHandler


class Parameters:
    """
    Loads and stores configuration parameters for the ingestion system.
    """

    def __init__(self):
        """
        Load from a configuration file.
        """
        handler = JsonHandler()
        # validate schema of configuration json
        self.configuration = handler.read_json_file(ING_MAN_CONFIG_FILE_PATH)# trasforming Json to a Python dictionary
        is_valid = handler.validate_json(self.configuration, ING_MAN_CONFIG_SCHEMA_FILE_PATH)
        if is_valid is False:
            sys.exit(0)  # exit if not correct