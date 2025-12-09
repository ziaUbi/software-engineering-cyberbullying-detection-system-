import threading
import queue
import requests
import json
from flask import Flask, request, jsonify
from segregation_parameters import SegregationSystemConfiguration

class SegregationCommunication:
    def __init__(self, host='0.0.0.0', port=None):
        if port is None:
            port = SegregationSystemConfiguration.GLOBAL_PARAMETERS["Segregation System"]["port"]
        
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        
        # Code per disaccoppiare ricezione e processamento
        self.session_queue = queue.Queue()
        self.config_queue = queue.Queue()

        # Endpoint per ricevere PreparedSession dal Preparation System
        @self.app.route('/PreparedSession', methods=['POST'])
        def receive_session():
            try:
                data = request.get_json()
                # Gestione del formato "message" standardizzato nel progetto
                content = json.loads(data["message"]) if "message" in data else data
                
                self.session_queue.put(content)
                return jsonify({"status": "received"}), 200
            except Exception as e:
                print(f"[Comm] Error receiving session: {e}")
                return jsonify({"status": "error", "message": str(e)}), 400

        # Endpoint per configurazioni
        @self.app.route('/Configure', methods=['POST'])
        def receive_config():
            try:
                data = request.get_json()
                content = json.loads(data["message"]) if "message" in data else data
                self.config_queue.put(content)
                return jsonify({"status": "received"}), 200
            except Exception as e:
                return jsonify({"status": "error"}), 400

    def start_listening(self):
        thread = threading.Thread(target=self.app.run, kwargs={'host': self.host, 'port': self.port}, daemon=True)
        thread.start()
        print(f"[Comm] Listening on {self.host}:{self.port}")

    def get_session(self):
        if not self.session_queue.empty():
            return self.session_queue.get()
        return None

    def get_config(self):
        if not self.config_queue.empty():
            return self.config_queue.get()
        return None

    def send_learning_sets(self, learning_sets: dict):
        target = SegregationSystemConfiguration.GLOBAL_PARAMETERS["Development System"]
        url = f"http://{target['ip']}:{target['port']}/LearningSets"
        
        packet = {
            "message": json.dumps(learning_sets),
            "sender": "Segregation System"
        }
        
        try:
            response = requests.post(url, json=packet)
            if response.status_code == 200:
                print("[Comm] Learning Sets sent successfully to Development System.")
                return True
        except Exception as e:
            print(f"[Comm] Error sending Learning Sets: {e}")
        return False