"""
Author: Martina Fabiani
"""
import os


def _get_data_file_absolute_path(relative_path: str) -> str:
    """
    Returns the absolute path of a file from a path relative to this file.
    :param relative_path: the path of a file relative to this module's file
    :return: the absolute path  resolved from the supplied relative path
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# Ingestion system
ING_MAN_CONFIG_FILE_PATH = _get_data_file_absolute_path("Ingestion_Configuration_schema/"
                                                        "IngestionSystemConfiguration.json")

ING_MAN_CONFIG_SCHEMA_FILE_PATH = _get_data_file_absolute_path(
    "Ingestion_Configuration_schema/IngestionSystemConfigurationSchema.json")
RECORD_SCHEMA_FILE_PATH = _get_data_file_absolute_path("record_and_session_schema/recordSchema.json")

# Database Manager
DATABASE_FILE_PATH = _get_data_file_absolute_path("IngestionDB/IngestionSystem.db")
DATABASE_FOLDER_PATH = _get_data_file_absolute_path("IngestionDB")