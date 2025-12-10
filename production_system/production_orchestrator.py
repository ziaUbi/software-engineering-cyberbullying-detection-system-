"""Orchestrator for the cyberbullying detection production system."""
from __future__ import annotations

import json
import time
from pathlib import Path

from .classification import Classification
from .configuration_parameters import ConfigurationParameters
from .deployment import Deployment
from .json_validation import JsonHandler
from .production_system_communication import ProductionSystemIO


class ProductionOrchestrator:
    """Coordinate deployment and inference cycles for social content moderation."""

    def __init__(self, service: bool, unit_test: bool) -> None:
        self._service = service
        self._unit_test = unit_test

        self._configuration = ConfigurationParameters()
        self._evaluation_phase = self._configuration.parameters["evaluation_phase"]
        
        # Manteniamo la chiave "Production System" per compatibilità col tuo JSON attuale
        prod_binding = self._configuration.global_netconf["Production System"]
        self._prod_sys_io = ProductionSystemIO(prod_binding["ip"], prod_binding["port"])
        
        self._session_counter = 0
        self._deployed = False
        self._handler = JsonHandler()
        # Assicurati che la cartella si chiami 'production_schema' come nel tuo file system attuale
        self._schema_path = Path(__file__).resolve().parent / "production_schema" / "PreparedSessionSchema.json"

    def production(self) -> None:
        """Start the orchestrator loop."""
        print("Cyberbullying production process started")
        self._prod_sys_io.start_server()
        while True:
            message = self._prod_sys_io.get_last_message()
            if not message:
                continue

            if self._service:
                self._prod_sys_io.send_timestamp(time.time(), "start")

            sender_ip = message["ip"]
            if sender_ip == self._configuration.global_netconf["Development System"]["ip"]:
                self._handle_deployment(message["message"])
                if self._unit_test:
                    return
                continue

            if sender_ip == self._configuration.global_netconf["Preparation System"]["ip"]:
                self._handle_classification(message["message"])
                if self._unit_test:
                    return
                continue

            print(f"Unknown sender {sender_ip}; ignoring message")
            if self._unit_test:
                return

    def _handle_deployment(self, classifier_payload: str) -> None:
        print("Classifier payload received")
        deployment = Deployment()
        if deployment.deploy(classifier_payload) is False:
            print("Error while deploying cyberbullying classifier")
            return

        self._deployed = True
        print("Classifier deployed successfully")
        self._prod_sys_io.send_configuration()
        if self._service:
            self._prod_sys_io.send_timestamp(time.time(), "end")

    def _handle_classification(self, prepared_session_raw: str) -> None:
        try:
            prepared_session = json.loads(prepared_session_raw)
        except json.JSONDecodeError:
            print("Invalid JSON received")
            return

        if self._handler.validate_json(prepared_session, self._schema_path) is False:
            print("Prepared session rejected: schema validation failed")
            return

        classification = Classification()
        label = classification.classify(prepared_session, self._deployed)
        if label is None:
            print("Classification skipped: classifier not yet deployed")
            return

        print("Moderation label generated")
        # 1. Invio OBBLIGATORIO al Client Side
        self._send_label_to_target("Service Class", label, "client")

        # 2. Invio OPZIONALE all'Evaluation System
        if self._evaluation_phase:
            self._send_label_to_target("Evaluation System", label, "send")
            
        # -----------------------------------

        self._session_counter += 1

        if self._service:
            self._prod_sys_io.send_timestamp(time.time(), "end")

        self._rotate_evaluation_phase()
        

    def _send_label_to_target(self, target_key: str, label, rule: str) -> None:
        try:
            target = self._configuration.global_netconf[target_key]
            self._prod_sys_io.send_label(target["ip"], target["port"], label, rule)
        except KeyError:
            print(f"Target {target_key} not configured properly")

    def _rotate_evaluation_phase(self) -> None:
        if self._evaluation_phase and self._session_counter == self._configuration.parameters["max_session_evaluation"]:
            self._session_counter = 0
            self._evaluation_phase = False
            return

        if not self._evaluation_phase and self._session_counter == self._configuration.parameters["max_session_production"]:
            self._session_counter = 0
            self._evaluation_phase = False


if __name__ == "__main__":
    orchestrator = ProductionOrchestrator(service=True, unit_test=False)
    orchestrator.production()