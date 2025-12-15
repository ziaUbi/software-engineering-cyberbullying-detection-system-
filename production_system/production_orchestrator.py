"""Orchestrator for the cyberbullying detection production system."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


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

        # Counters for logging purposes
        self._rx_counter = 0


        self._configuration = ConfigurationParameters()

        # Phase manager
        self._phase_manager = ClassificationPhaseManager(
            evaluation_phase=bool(self._configuration.parameters["evaluation_phase"]),
            prod_threshold=int(self._configuration.parameters["max_session_production"]),
            eval_threshold=int(self._configuration.parameters["max_session_evaluation"]),
        )

        prod_binding = self._configuration.global_netconf["Production System"]
        self._prod_sys_io = ProductionSystemIO(prod_binding["ip"], prod_binding["port"])

        # check if the classifier is already deployed
        model_path = Path(__file__).resolve().parent / "model" / "cyberbullying_classifier.sav"
        self._deployed = model_path.exists()

        self._handler = JsonHandler()
        self._schema_path = Path(__file__).resolve().parent / "production_schema" / "PreparedSessionSchema.json"

    def production(self) -> None:
        """Start the orchestrator loop."""
        print("Cyberbullying production process started")
        self._prod_sys_io.start_server()
        while True:
            message = self._prod_sys_io.get_last_message()
            if not message:
                continue

            sender_ip = message.get("ip")
            sender_port = message.get("port")
            content = message.get("message")

            # set correct size based on content type
            if isinstance(content, str):
                size = len(content)
            elif isinstance(content, dict):
                size = len(json.dumps(content))
            else:
                size = 0

            if sender_ip == self._configuration.global_netconf["Development System"]["ip"] and sender_port == self._configuration.global_netconf["Development System"]["port"]:
                msg_type = "classifier"
            elif sender_ip == self._configuration.global_netconf["Preparation System"]["ip"] and sender_port == self._configuration.global_netconf["Preparation System"]["port"]:
                msg_type = "prepared_session"
            else:
                msg_type = "unknown"

            self._rx_counter += 1
            print(f"[RX] #{self._rx_counter} from={sender_ip}:{sender_port} type={msg_type} size={size}")


            #   Timestamp
            if self._service:
                self._prod_sys_io.send_timestamp(time.time(), "start")

            # sender_ip = message["ip"]
            if sender_ip == self._configuration.global_netconf["Development System"]["ip"] and sender_port == self._configuration.global_netconf["Development System"]["port"]:
                self._handle_deployment(message["message"])
                if self._unit_test:
                    return
                continue

            if sender_ip == self._configuration.global_netconf["Preparation System"]["ip"] and sender_port == self._configuration.global_netconf["Preparation System"]["port"]:
                self._handle_classification(message["message"])
                if self._unit_test:
                    return
                continue

            print(f"Unknown sender {sender_ip}; ignoring message")
            if self._unit_test:
                return

    def _handle_deployment(self, classifier_payload: str | None) -> None:
        if not classifier_payload or not isinstance(classifier_payload, str):
            return

        deployment = Deployment()
        if not deployment.deploy(classifier_payload):
            return

        # Update internal state
        self._deployed = True

        # Notify other systems (messaging / service)
        self._prod_sys_io.send_configuration()

        if self._service:
            self._prod_sys_io.send_timestamp(time.time(), "end")


    def _handle_classification(self, prepared_session_raw: Any) -> None:
        # 1. Input normalization (dict or JSON string)
        if isinstance(prepared_session_raw, dict):
            prepared_session = prepared_session_raw
        else:
            try:
                prepared_session = json.loads(prepared_session_raw)
            except (json.JSONDecodeError, TypeError):
                print("Invalid prepared session received (not valid JSON)")
                return

        # 2. Schema validation
        if not self._handler.validate_json(prepared_session, self._schema_path):
            print("Prepared session rejected: schema validation failed")
            return

        # 3. Classification
        classification = Classification()
        label = classification.classify(prepared_session, self._deployed)

        if label is None:
            # model not yet available
            return

        # 4. Mandatory sending to Client Side
        self._send_label_to_target("Service Class", label, rule="client")

        # 5. Optional sending to Evaluation System
        if self._phase_manager.evaluation_phase:
            self._send_label_to_target("Evaluation System", label, rule="send")

        # 6. Timestamp (best effort)
        if self._service:
            try:
                self._prod_sys_io.send_timestamp(time.time(), "Session Classified")
            except Exception:
                pass  

        # 7. Phase update
        switched = self._phase_manager.on_session_completed()
        if switched:
            print(f"[PHASE] switched to {self._phase_manager.current_phase}")


    def _send_label_to_target(self, target_key: str, label, rule: str) -> None:
        try:
            target = self._configuration.global_netconf[target_key]
            self._prod_sys_io.send_label(
                target["ip"],
                target["port"],
                label,
                rule
            )
        except KeyError:
            print(f"[ERROR] Target '{target_key}' not configured properly")



if __name__ == "__main__":
    orchestrator = ProductionOrchestrator(service=True, unit_test=False)
    orchestrator.production()
