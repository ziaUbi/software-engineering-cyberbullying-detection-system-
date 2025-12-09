"""
Module: PreparationSystemParameters
Loads and manages configuration parameters for the preparation system.

Author: Martina Fabiani
"""
import sys
import logging

from preparation_system.json_handler import JsonHandler
from preparation_system import PREP_CONFIG_FILE_PATH, PREP_MAN_CONFIG_SCHEMA_FILE_PATH

class PreparationSystemParameters:
    """
    Loads and stores configuration parameters for the preparation system.
    Corresponds to 'PreparationConfiguration' in the UML.
    """

    def __init__(self):
        """
        Load configuration from file, validate it, and map to attributes.
        """
        handler = JsonHandler()
        
        # Read configuration file (Corrected path constant)
        self.configuration = handler.read_json_file(PREP_CONFIG_FILE_PATH)
        
        if self.configuration is None:
            logging.critical("Configuration file not found or unreadable.")
            sys.exit(1) # Exit with error code

        # Validate configuration file schema
        is_valid = handler.validate_json(self.configuration, PREP_MAN_CONFIG_SCHEMA_FILE_PATH)
        
        if not is_valid:
            logging.critical("Configuration file does not match the schema.")
            sys.exit(1) # Exit with error code

        # Map dictionary to class attributes
        try:
            self.development_mode = self.configuration.get("development", False)
            self.min_decibel_gain = self.configuration.get("MinDecibelGain", -100.0)
            self.max_decibel_gain = self.configuration.get("MaxDecibelGain", 0.0)
            self.stopword_list = self.configuration.get("StopwordList", [])
            self.features = self.configuration.get("features", [])
            
            # Parametri di connessione
            self.ip_classification = self.configuration.get("ip_classification")
            self.port_classification = self.configuration.get("port_classification")
            self.ip_segregation = self.configuration.get("ip_segregation")
            self.port_segregation = self.configuration.get("port_segregation")
            self.ip_preparation = self.configuration.get("ip_preparation")
            self.port_preparation = self.configuration.get("port_preparation")
            
        except Exception as e:
            logging.error(f"Error mapping configuration parameters: {e}")
            sys.exit(1)

    def load_config(self):
        """
        Reloads the configuration (UML method).
        """
        self.__init__()