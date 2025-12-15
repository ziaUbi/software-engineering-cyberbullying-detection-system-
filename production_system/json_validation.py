"""Utilities for managing JSON payloads in the cyberbullying detection system."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

import jsonschema


class JsonHandler:
    """Read, persist, and validate JSON payloads."""

    def read_json_file(self, filepath: str | Path) -> Dict[str, Any] | None:
        """Read a JSON file from *filepath* and return its content."""
        file_path = Path(filepath)
        try:
            with file_path.open("r", encoding="utf-8") as json_file:
                return json.load(json_file)
        except Exception as exc: 
            logging.error("Error reading JSON file %s: %s", file_path, exc)
            return None

    def write_json_file(self, data: Dict[str, Any], filepath: str | Path) -> bool:
        """Persist *data* into *filepath*.

        Returns *True* if the write succeeds, otherwise *False*.
        """
        file_path = Path(filepath)
        try:
            with file_path.open("w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            return True
        except Exception as exc:
            logging.error("Error saving JSON file %s: %s", file_path, exc)
            return False

    def validate_json(self, json_data: Dict[str, Any], schema_path: str | Path) -> bool:
        """Validate *json_data* against the schema in *schema_path*."""
        schema_file = Path(schema_path)
        with schema_file.open("r", encoding="utf-8") as file:
            json_schema = json.load(file)
        try:
            jsonschema.validate(instance=json_data, schema=json_schema)
        except jsonschema.exceptions.ValidationError as exc:
            logging.error(exc)
            return False
        return True
