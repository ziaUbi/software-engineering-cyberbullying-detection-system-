"""
Module: ingestion_system_json_io
Handles JSON-based input and output operations for the ingestion system.

Author: Martina Fabiani

"""
import json

from flask import Flask, request, jsonify
import threading
import requests
from queue import Queue, Empty
from typing import Optional, Dict

from ingestion_system import RECORD_SCHEMA_FILE_PATH
from .json_handler import JsonHandler


class SessionAndRecordExchanger:
    """
    A utility class to enable inter-module communication using Flask.

    This class supports sending and receiving messages using a thread-safe queue.
    """
    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        """
        Initialize the Flask communication server.

        :param host: The host address for the Flask server.
        :param port: The port number for the Flask server.
        """
        self.app = Flask(__name__)
        self.host = host
        self.port = port

        # Thread-safe queue for received messages
        self.message_queue = Queue()

        # Define a route to receive messages
        @self.app.route('/send', methods=['POST'])
        def receive_message():
            data = request.json
            sender_ip = request.remote_addr
            sender_port = data.get('port')
            message = data.get('message')

            if not message:
                return jsonify({"error": "Invalid message format"}), 400

            # Add the message to the queue
            self.message_queue.put({
                'ip': sender_ip,
                'port': sender_port,
                'message': message
            })

            return jsonify({"status": "received"}), 200

    def start_server(self):
        """
        Start the Flask server in a separate thread.
        """
        thread = threading.Thread(target=self.app.run, kwargs={'host': self.host, 'port': self.port}, daemon=True)
        thread.start()

    def send_message(self, target_ip: str, target_port: int, message) -> Optional[Dict]:
        """
        Send a message to a target module.

        :param target_ip: The IP address of the target module.
        :param target_port: The port of the target module.
        :param message: The message to send (typically a JSON string).
        :return: The response from the target, if any.
        """
        url = f"http://{target_ip}:{target_port}/send"
        payload = {
            "port": self.port,
            "message": message
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            print(f"Error sending message: {e}")
        return None

    def get_message(self, timeout: Optional[float] = None) :
        """
        Retrieve a message from the queue, blocking if necessary.

        :param timeout: Maximum time to wait for a message (in seconds). None means wait indefinitely.
        :return: A dictionary containing the sender's IP, port, and the message content, or None if timed out.
        """
        try:
            message = self.message_queue.get(timeout=timeout, block=True)
            record_message = message['message']  # json
            handler = JsonHandler()
            new_record = json.loads(record_message)  # dictionary
            is_valid = handler.validate_json(new_record, RECORD_SCHEMA_FILE_PATH)
            if not is_valid:
                return True, new_record

            return False, new_record
        except Empty:
            print("No messages received within the timeout period.")
            return None