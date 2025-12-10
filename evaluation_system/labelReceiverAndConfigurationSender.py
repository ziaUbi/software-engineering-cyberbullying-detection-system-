"""
Author: Rossana Antonella Sacco
"""

from typing import Optional, Dict
import json
import queue
import threading
import requests
import jsonschema
from flask import Flask, request, jsonify

from evaluation_system.evaluationSystemParameters import EvaluationSystemParameters
from evaluation_system.label import Label

class LabelReceiverAndConfigurationSender:
    """
    Evaluation System module responsible for receiving labels and sending configuration.
    Acts as the boundary between the Evaluation System and external systems (Ingestion/Production).
    """

    def __init__(self, host: str = '0.0.0.0', port: int = None, basedir: str = "."):
        """
        Initialize the Flask communication server.
        """
        #if the port is not provided, we get it from the global parameters
        if port is None:
            port = EvaluationSystemParameters.GLOBAL_PARAMETERS["Evaluation System"]["port"]

        self.app = Flask(__name__)
        self.host = host
        self.port = port
        
        #Queue for thread-safe communication with the Orchestrator
        self.label_queue = queue.Queue()

        # Path to the JSON schema 
        self.label_schema_path = f"{basedir}/schema/label_schema.json"

        # Register the Flask route for receiving labels
        @self.app.route('/send', methods=['POST'])
        def receive_label():
            return self._handle_received_packet()

    def _handle_received_packet(self):
        """
        Internal logic to process the incoming request.
        """
        sender_ip = request.remote_addr

        try:
            packet = request.get_json()
            if not packet or "payload" not in packet:
                    return jsonify({"status": "error", "payload": "Invalid packet format"}), 400

            # The message is a JSON string inside the 'payload' field
            json_label = packet.get("payload")
            #Schema Validation
            if self._validate_json_label(json_label):
                
                #Source Identification (Expert vs Classifier)
                ingestion_ip = EvaluationSystemParameters.GLOBAL_PARAMETERS["Ingestion System"]["ip"]
                production_ip = EvaluationSystemParameters.GLOBAL_PARAMETERS["Production System"]["ip"]

                expert = False
                
                if sender_ip == ingestion_ip:
                    expert = True
                elif sender_ip == production_ip:
                    expert = False
                else:
                    print(f"Warning: Unknown sender IP {sender_ip}")
                    return jsonify({"status": "error", "message": "Unauthorized Sender IP"}), 403

                #Create Label Object
                label = Label(
                    uuid=json_label['uuid'], 
                    label=str(json_label['label']), 
                    expert=expert
                )
                
                #Insert into Queue
                self.label_queue.put(label)

                return jsonify({"status": "received"}), 200
            else:
                return jsonify({"status": "error", "message": "Invalid JSON label schema"}), 400
        
        except Exception as e:
            print(f"Error processing request: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
        
    def start_server(self):
        """
        Start the Flask server in a separate thread.
        This allows the Orchestrator to run concurrently without blocking.
        """
        # daemon=True ensures the thread dies when the main program exits
        thread = threading.Thread(target=self.app.run, kwargs={'host': self.host, 'port': self.port}, daemon=True)
        thread.start()
        print(f"Server started on {self.host}:{self.port}")

    def _validate_json_label(self, json_label: Dict) -> bool:
        """
        Validate a JSON label received from a sender using the schema file.
        """
        try:
            with open(self.label_schema_path, "r") as schema_file:
                label_schema = json.load(schema_file)
            
            jsonschema.validate(json.dumps(json_label), label_schema)
            return True
        except FileNotFoundError:
            print(f"CRITICAL: Schema file not found at {self.label_schema_path}")
            return False
        except jsonschema.ValidationError as e:
            print(f"Validation Error: {e.message}")
            return False

    def send_configuration(self, config_data: Dict = None) -> bool:
        """
        Send a configuration message to the Messaging System.
        Used when the classifier needs retraining.
        """
        
        target_system = 'Messaging System' 
        
        try:
            target_ip = EvaluationSystemParameters.GLOBAL_PARAMETERS[target_system]['ip']
            target_port = EvaluationSystemParameters.GLOBAL_PARAMETERS[target_system]['port']
        except KeyError:
            print(f"Error: Configuration for '{target_system}' not found in global parameters.")
            return False
        
        url = f"http://{target_ip}:{target_port}/Configuration"

        # Default 
        if config_data is None:
            config_data = {"configuration": "restart"}

        try:
            # Creation of the standard packet
            packet = {
                "port": EvaluationSystemParameters.GLOBAL_PARAMETERS["Evaluation System"]["port"],
                "message": json.dumps(config_data)
            }

            print(f"Sending configuration to {url}...")
            response = requests.post(url, json=packet)
            
            if response.status_code == 200:
                print(f"Configuration sent successfully.")
                return True
            else:
                print(f"Failed to send configuration. Remote Status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"Network error sending configuration: {e}")
            return False

    def get_label(self) -> Optional[Label]:
        """
        Retrieves the next label from the queue.
        This method is BLOCKING: it waits until a label arrives.
        
        :return: A Label object.
        """
        #block=True ensures the Orchestrator does not consume CPU in an empty loop
        return self.label_queue.get(block=True)