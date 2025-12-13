"""Configuration loader for the production system."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .json_validation import JsonHandler


class ConfigurationParameters:
    """Load production and networking parameters from JSON assets."""

    def __init__(self) -> None:
        self._package_root = Path(__file__).resolve().parent
        handler = JsonHandler()

        prod_conf_path = self._package_root / "configuration" / "prod_sys_conf.json"
        schema_path = self._package_root / "production_schema" / "configSchema.json"
        prod_sys_conf = handler.read_json_file(prod_conf_path)
        if not prod_sys_conf or handler.validate_json(prod_sys_conf, schema_path) is False:
            raise ValueError("Invalid production system configuration")
        self.parameters: Dict[str, Any] = prod_sys_conf

        global_path = self._package_root / "configuration" / "global_netconf.json"
        net_conf = handler.read_json_file(global_path)
        if not net_conf:
            raise ValueError("Global netconf missing or invalid")
        self.global_netconf: Dict[str, Any] = net_conf

    def start_config(self) -> Dict[str, str]:
        """Payload sent to the messaging system to kick-off production."""
        return {"configuration": "production"}


