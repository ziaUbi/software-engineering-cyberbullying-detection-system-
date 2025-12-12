"""Orchestrator for the cyberbullying detection production system."""
from __future__ import annotations

import json
import time
from pathlib import Path

from .classification import Classification
from .production_phase_manager import ClassificationPhaseManager
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

        # Phase manager (spostiamo qui la logica che prima era in _rotate_evaluation_phase)
        self._phase_manager = ClassificationPhaseManager(
            evaluation_phase=bool(self._configuration.parameters["evaluation_phase"]),
            prod_threshold=int(self._configuration.parameters["max_session_production"]),
            eval_threshold=int(self._configuration.parameters["max_session_evaluation"]),
        )

        # Manteniamo la chiave "Production System" per compatibilità col tuo JSON attuale
        prod_binding = self._configuration.global_netconf["Production System"]
        self._prod_sys_io = ProductionSystemIO(prod_binding["ip"], prod_binding["port"])

        # self._deployed = False
        self._deployed = True  # Per testare senza deployment !!!!!!!!!!!!!
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

            print(f"\n[DEBUG] Messaggio Arrivato: {message}\n")

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

        # 2. Invio OPZIONALE all'Evaluation System (deciso dal Phase Manager)
        if self._phase_manager.evaluation_phase:
            self._send_label_to_target("Evaluation System", label, "send")

        if self._service:
            self._prod_sys_io.send_timestamp(time.time(), "end")

        switched = self._phase_manager.on_session_completed()
        if switched:
            print(f"[DEBUG] Phase switched -> {self._phase_manager.current_phase}")

    def _send_label_to_target(self, target_key: str, label, rule: str) -> None:
        try:
            target = self._configuration.global_netconf[target_key]
            self._prod_sys_io.send_label(target["ip"], target["port"], label, rule)
        except KeyError:
            print(f"Target {target_key} not configured properly")


if __name__ == "__main__":
    orchestrator = ProductionOrchestrator(service=True, unit_test=False)
    orchestrator.production()
