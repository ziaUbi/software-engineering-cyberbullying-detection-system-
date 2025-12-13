"""Networking primitives for the cyberbullying production system."""
from __future__ import annotations

import json
import queue
import threading
from typing import Dict, Optional

import requests
from flask import Flask, jsonify, request

from .configuration_parameters import ConfigurationParameters
from .label import Label


class ProductionSystemIO:
    """Manage inbound and outbound HTTP messaging for the production system."""

    def __init__(self, host: str = "0.0.0.0", port: int = 5007) -> None:
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.msg_queue: "queue.Queue[Dict[str, str]]" = queue.Queue()
        
        # Silenzia i log di Flask per pulizia
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        @self.app.route("/send", methods=["POST"])
        def receive_message():
            data = request.json or {}
            sender_ip = request.remote_addr
            sender_port = data.get("port")
            message_content = data.get("payload") or data.get("message")
            message = {"ip": sender_ip, "port": sender_port, "message": message_content}
            self.msg_queue.put(message)
            return jsonify({"status": "received"}), 200

    def start_server(self) -> None:
        """Boot the Flask server on a background thread."""
        print(f"Flask server listening on {self.host}:{self.port}")
        thread = threading.Thread(target=self.app.run, kwargs={"host": self.host, "port": self.port}, daemon=True)
        thread.start()

    def send_configuration(self) -> Optional[Dict[str, str]]:
        """Send the start configuration to the messaging system."""
        configuration = ConfigurationParameters()
        payload = {
            "port": self.port,
            "message": json.dumps(configuration.start_config())
        }
        msg_sys = configuration.global_netconf["Messaging System"]
        url = f"http://{msg_sys['ip']}:{msg_sys['port']}/MessagingSystem"
        try:
            response = requests.post(url, json=payload, timeout=2)  #lower timeout
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as exc:
            print(f"Error sending message: {exc}")
        return None

    # def send_label(self, target_ip: str, target_port: int, label: Label, rule: str) -> Optional[Dict[str, str]]:
    #     """Dispatch labels to downstream services (with TX counters and safe logs)."""
    #     # init counters lazily (no need to change __init__)
    #     if not hasattr(self, "_tx_client_counter"):
    #         self._tx_client_counter = 0
    #     if not hasattr(self, "_tx_eval_counter"):
    #         self._tx_eval_counter = 0

    #     label_json = label.to_json_string()


    #     if rule == "send":
    #         endpoint = "/send"
    #         tag = "EVAL"
    #     elif rule == "client":
    #         endpoint = "/ClientSide"
    #         tag = "CLIENT"
    #     else:
    #         print(f"[TX ERROR] unsupported rule '{rule}'")
    #         return None

    #     url = f"http://{target_ip}:{target_port}{endpoint}"
    #     payload = {"port": self.port, "payload": label_json}

    #     try:
    #         response = requests.post(url, json=payload, timeout=10)

    #         if response.status_code != 200:
    #             print(f"[TX ERROR] {tag} http={response.status_code} to={target_ip}:{target_port}{endpoint} uuid={label.uuid}")
    #             return None

    #         # increment only on success
    #         if tag == "CLIENT":
    #             self._tx_client_counter += 1
    #             n = self._tx_client_counter
    #         else:
    #             self._tx_eval_counter += 1
    #             n = self._tx_eval_counter

    #         print(f"[TX {tag} #{n}] to={target_ip}:{target_port}{endpoint} uuid={label.uuid}")
    #         return response.json()

    #     except requests.RequestException as exc:
    #         print(f"[TX ERROR] {tag} exception to={target_ip}:{target_port}{endpoint} uuid={label.uuid} err={exc}")
    #         return None

    def send_label(self, target_ip: str, target_port: int, label: Label, rule: str) -> Optional[Dict[str, str]]:
        """Dispatch labels to downstream services (with TX counters and safe logs)."""
        # init counters lazily (no need to change __init__)
        if not hasattr(self, "_tx_client_counter"):
            self._tx_client_counter = 0
        if not hasattr(self, "_tx_eval_counter"):
            self._tx_eval_counter = 0

        # --- MODIFICA SSE INIZIO ---
        # Determiniamo endpoint, tag e FORMATO del payload in base alla regola
        if rule == "send":
            endpoint = "/send"
            tag = "EVAL"
            # L'Evaluation System vuole un DIZIONARIO (JSON Object annidato)
            # Assumiamo che la classe Label abbia il metodo to_dictionary() come visto nei file precedenti
            label_content = label.to_dictionary() 
        elif rule == "client":
            endpoint = "/ClientSide"
            tag = "CLIENT"
            # Il Client Side (o il vecchio standard) usa una STRINGA JSON
            label_content = label.to_json_string()
        else:
            print(f"[TX ERROR] unsupported rule '{rule}'")
            return None
        # --- MODIFICA SSE FINE ---

        url = f"http://{target_ip}:{target_port}{endpoint}"
        
        # Qui label_content sarà un dict per 'eval' e una str per 'client'
        payload = {"port": self.port, "message": label_content}

        try:
            # requests.post con parametro 'json=' serializza automaticamente
            # se label_content è un dict, diventa un oggetto JSON nel body.
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code != 200:
                print(f"[TX ERROR] {tag} http={response.status_code} to={target_ip}:{target_port}{endpoint} uuid={label.uuid}")
                return None

            # increment only on success
            if tag == "CLIENT":
                self._tx_client_counter += 1
                n = self._tx_client_counter
            else:
                self._tx_eval_counter += 1
                n = self._tx_eval_counter

            print(f"[TX {tag} #{n}] to={target_ip}:{target_port}{endpoint} uuid={label.uuid}")
            return response.json()

        except requests.RequestException as exc:
            print(f"[TX ERROR] {tag} exception to={target_ip}:{target_port}{endpoint} uuid={label.uuid} err={exc}")
            return None

    # Questa è l'attesa bloccante originale per i messaggi in arrivo
    # def get_last_message(self) -> Optional[Dict[str, str]]:
    #     """Block until a message is available in the queue."""
    #     return self.msg_queue.get(block=True)

    def get_last_message(self) -> Optional[Dict[str, str]]:
        """Block until a message is available in the queue."""
        try:
            # Aggiungiamo timeout=1.0. 
            # In questo modo ogni secondo il blocco si "sveglia".
            return self.msg_queue.get(block=True, timeout=1.0)
        except queue.Empty:
            # Se dopo 1 secondo non è arrivato nulla, restituisce None
            return None

    def send_timestamp(self, timestamp: float, status: str) -> bool:
        """Report production timestamps to the service class."""
        configuration = ConfigurationParameters()
        service_conf = configuration.global_netconf["Service Class"]
        prod_conf = configuration.global_netconf["Production System"]
        url = f"http://{service_conf['ip']}:{service_conf['port']}/Timestamp"
        packet = {
            "port": prod_conf["port"],
            "message": json.dumps({
                "timestamp": timestamp,
                "system": "Cyberbullying Production System",
                "status": status
            })
        }
        try:
            response = requests.post(url, json=packet, timeout=10)
            return response.status_code == 200
        except requests.RequestException as exc:
            print(f"Error sending timestamp: {exc}")
            return False