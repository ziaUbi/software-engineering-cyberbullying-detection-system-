import threading
import requests
import json
from flask import Flask, request, jsonify
from queue import Queue, Empty
from typing import Optional, Dict, Any, Tuple
import dataclasses
from dataclasses import asdict

from preparation_system.json_handler import JsonHandler 
from preparation_system import RAW_SESSION_SCHEMA_PATH


class PreparationSessionChannel:
    """
    Communication channel for the Preparation System.
    
    Responsibilities:
    1. Receive RawSessions from the Ingestion System (via Flask server).
    2. Buffer received sessions in a thread-safe Queue.
    3. Send PreparedSessions to the Classification or Segregation System.
    """

    def __init__(self, host: str = '0.0.0.0', port: int = 5001):
        """
        Initialize the Flask server and the message queue.

        :param host: Host IP address to bind the server.
        :param port: Port number to listen on.
        """
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        
        # Thread-safe queue to store incoming RawSessions
        self._input_queue = Queue()

        # Define the route to receive messages (RawSessions)
        @self.app.route('/send', methods=['POST'])
        def _receive_internal():
            """
            Internal Flask route to handle incoming HTTP POST requests.
            Expected format: {"type": "raw_session", "payload": {...}, ...}
            """
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 415
            
            data = request.json
            sender_ip = request.remote_addr
            
            # Extract the actual data payload
            msg_type = data.get('type')
            payload = data.get('payload') # This should be the RawSession dict

            if not payload:
                return jsonify({"error": "Invalid format, 'payload' missing"}), 400

            # We only care about raw_sessions in this input channel
            if msg_type == 'raw_session':
                self._input_queue.put({
                    'ip': sender_ip,
                    'data': payload
                })
                return jsonify({"status": "received"}), 200
            else:
                return jsonify({"warning": f"Ignored message type: {msg_type}"}), 200

    def start_server(self):
        """
        Start the Flask server in a separate daemon thread.
        This allows the main orchestration loop to run concurrently.
        """
        server_thread = threading.Thread(
            target=self.app.run, 
            kwargs={'host': self.host, 'port': self.port, 'use_reloader': False}, 
            daemon=True
        )
        server_thread.start()
        print(f"Preparation Session Channel listening on {self.host}:{self.port}")

    def get_raw_session(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves the next available RawSession from the queue.
        Corresponds to the 'get_raw_session()' method in the UML.

        :param timeout: Time in seconds to wait for a message. None blocks indefinitely.
        :return: A dictionary representing the RawSession, or None if queue is empty/timeout.
        """
        try:
            queue_item = self._input_queue.get(timeout=timeout, block=True)
            raw_session_data = queue_item.get('data')

            # Optional: Here you could interact with JsonHandler to validate the schema
            handler = JsonHandler()
            if not handler.validate_json(raw_session_data, RAW_SESSION_SCHEMA_PATH):
                print("Invalid RawSession schema received.")
                return None

            return raw_session_data

        except Empty:
            return None
        except Exception as e:
            print(f"Error retrieving raw session: {e}")
            return None

    def send_prepared_session(self, target_ip: str, target_port: int, prepared_session: Any) -> bool:
        """
        Sends a PreparedSession to the next system (Classification or Segregation).
        Corresponds to the 'send_prepared_session()' method in the UML.

        :param target_ip: IP address of the destination system.
        :param target_port: Port of the destination system.
        :param prepared_session: The PreparedSession object (or dict) to send.
        :return: True if sent successfully, False otherwise.
        """
        url = f"http://{target_ip}:{target_port}/send"
        
        # If the input is a dataclass object, convert it to a dict
        if hasattr(prepared_session, 'to_dict'):
            payload_data = prepared_session.to_dict()
        elif dataclasses.is_dataclass(prepared_session):
            payload_data = asdict(prepared_session)
        else:
            payload_data = prepared_session

        # Construct the standard message envelope
        message = {
            "port": self.port,
            "type": "prepared_session", # Tagging the message type
            "payload": payload_data
        }

        try:
            response = requests.post(url, json=message, timeout=5)
            if response.status_code == 200:
                print(f"PreparedSession sent successfully to {target_ip}:{target_port}")
                return True
            else:
                print(f"Failed to send PreparedSession. Status: {response.status_code}")
        except requests.RequestException as e:
            print(f"Connection error sending PreparedSession to {target_ip}:{target_port} - {e}")
        
        return False