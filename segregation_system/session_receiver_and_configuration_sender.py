import json
import queue
import time
import threading
from typing import Optional, Dict

import requests
from flask import Flask, request, jsonify

from segregation_system.segregation_configuration import SegregationSystemConfiguration


class SessionReceiverAndConfigurationSender:
    """
    A utility class to enable inter-module communication using Flask.

    This class supports sending and receiving messages in a blocking manner.
    """

    def __init__(self, host: str = '0.0.0.0', port: int = 5003):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.last_message = None
        self.queue = queue.Queue()

        # Lock and condition for blocking behavior
        self.message_condition = threading.Condition()

        # Define a route to receive messages
        @self.app.route('/send', methods=['POST'])
        def receive_message():
            data = request.json
            sender_ip = request.remote_addr
            sender_port = data.get('port')
            message = data.get('message')

            with self.message_condition:
                self.last_message = {
                    'ip': sender_ip,
                    'port': sender_port,
                    'message': message
                }
                self.queue.put(self.last_message)
                # Notify any threads waiting for a message
                self.message_condition.notify_all()

            return jsonify({"status": "received"}), 200

    def start_server(self):
        thread = threading.Thread(target=self.app.run, kwargs={'host': self.host, 'port': self.port}, daemon=True)
        thread.start()

    def send_message(self, target_ip: str, target_port: int, message: str , dest: str = "send") -> Optional[Dict]:
        url = f"http://{target_ip}:{target_port}/{dest}"
        payload = {
            "port": self.port,
            "message": message
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            print(f"Error sending message: {e}")
        return None

    def get_last_message(self) -> Optional[Dict]:
        """
       Wait for a message to be received and return it.

        :return: A dictionary containing the sender's IP, port, and the message content.
        """
        return self.queue.get(block=True)

    def send_configuration(self , msg : str):
        """
        Send the configuration "restart" message to the Messaging System.

        :return: True if the message was sent successfully, False otherwise.
        """

        network_info = SegregationSystemConfiguration.GLOBAL_PARAMETERS["Messaging System"]

        configuration = {
            "configuration": msg
        }

        self.send_message(network_info.get('ip') , network_info.get('port') , json.dumps(configuration) , "MessagingSystem")

    # Testing method
    def send_timestamp(self, status: str = ""):
        """
        Send the timestamp to the Service Class.

        :param status: The status of the timestamp
        :return: True if the timestamp was sent successfully, False otherwise.
        """
        network_info = SegregationSystemConfiguration.GLOBAL_PARAMETERS["Service Class"]

        timestamp_message = {
            "timestamp": time.time(),
            "system": "Segregation System",
            "status": status
        }

        self.send_message(network_info.get('ip') , network_info.get('port') , json.dumps(timestamp_message) , "Timestamp")


if __name__ == "__main__":

    # Module A (Sender)
    from time import sleep

    # Create a MessageBroker instance and start the server
    module_a = SessionReceiverAndConfigurationSender(host='0.0.0.0', port=5003)
    module_a.start_server()

    # Send a message to Module B
    response = module_a.send_message(target_ip="87.19.204.54", target_port=5004, message='{"action": "test"}')
    print("Response from Module B:", response)

    # Keep the server running
    while True:
        sleep(1)