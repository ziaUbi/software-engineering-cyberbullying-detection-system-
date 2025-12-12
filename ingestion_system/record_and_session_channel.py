"""
Module: ingestion_system_json_io
Handles JSON-based input and output operations for the ingestion system.

Author: Martina Fabiani

"""
from ingestion_system import RECORD_SCHEMA_FILE_PATH
from ingestion_system.json_handler import JsonHandler


import threading
import requests
import json
from flask import Flask, request, jsonify
from queue import Queue, Empty
from typing import Optional, Dict, Tuple, Any, Union


class RecordAndSessionChannel:
    """
    A channel for sending/receiving records, sessions, and labels using Flask.
    """
    def __init__(self, host: str = '0.0.0.0', port: int = 5001):
        """
        Initialize the attributes defined in the UML.
        """
        self.app = Flask(__name__)  # -app
        self.host = host            # -host
        self.port = port            # -port
        
        # Internal components needed for functionality
        self._message_queue = Queue()

        # Internal Route definition
        @self.app.route('/send', methods=['POST'])
        def _receive_internal():
            if not request.is_json:
                 return jsonify({"error": "Content-Type must be application/json"}), 415
            
            data = request.json
            sender_ip = request.remote_addr
            sender_port = data.get('port')
            # Extract the actual data payload
            payload = data.get('payload')
            data_type = data.get('type', 'unknown') # e.g., 'record', 'raw_session', 'label'

            if not payload:
                return jsonify({"error": "Invalid format, 'payload' missing"}), 400

            # Add to queue
            self._message_queue.put({
                'ip': sender_ip,
                'port': sender_port,
                'type': data_type,
                'data': payload
            })

            return jsonify({"status": "received"}), 200

    # Start the Flask server in a separate thread
    def start_server(self):
        """Start Flask in a daemon thread."""
        thread = threading.Thread(
            target=self.app.run, 
            kwargs={'host': self.host, 'port': self.port, 'use_reloader': False}, 
            daemon=True
        )
        thread.start()


    def send_raw_session(self, target_ip: str, target_port: int, session_data: Any) -> bool:
        """
        + send_raw_session(): Sends a RawSession object (or dict representation) to a target.
        Returns True if successful.
        """
        # Convert to dict if it's an object
        # if hasattr(session_data, '__dict__'): session_data = session_data.__dict__
        
        return self._send_generic(target_ip, target_port, 'raw_session', session_data)

    def send_label(self, target_ip: str, target_port: int, label_data: Dict[str, Any]) -> bool:
        """
        + send_label(): Sends label data to a target.
        Returns True if successful.
        """
        return self._send_generic(target_ip, target_port, 'label', label_data)

    def get_record(self, timeout: Optional[float] = None) -> Optional[Tuple[bool, Any]]:

        """
        Retrieve a message from the queue, blocking if necessary.

        :param timeout: Maximum time to wait. None means wait indefinitely.
        :return: A tuple (is_valid, record_data) or None if timed out.
        """
        try:
            queue_item = self._message_queue.get(timeout=timeout, block=True)
            
            # extract raw data
            raw_data = queue_item.get('data') 

            # Parsing
            if isinstance(raw_data, str):
                record = json.loads(raw_data)
            else:
                record = raw_data

            # Validation
            handler = JsonHandler()
            is_valid = handler.validate_json(record, RECORD_SCHEMA_FILE_PATH)

            if is_valid:
                return True, record
            else:
                print(f"Warning: Invalid record received from {queue_item.get('ip')}")
                return False, record

        except Empty:
            # Timeout occurred
            # print("No messages received.") 
            return None
            
        except Exception as e:
            print(f"Error processing record in get_record: {e}")
            return False, None
            
    # --- Private Helper Method ---

    def _send_generic(self, target_ip: str, target_port: int, msg_type: str, content: Any) -> bool:
        """Internal helper to handle the HTTP POST logic."""
        url = f"http://{target_ip}:{target_port}/send"
        
        # Structure the payload
        payload = {
            "port": self.port,
            "type": msg_type,
            "payload": content
        }
        try:
            # Use a timeout to avoid hanging indefinitely
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
        except requests.RequestException as e:
            print(f"Error sending {msg_type} to {target_ip}:{target_port} - {e}")
        return False