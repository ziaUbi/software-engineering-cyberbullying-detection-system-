from flask import Flask, request
from flask_restful import Api, Resource
import requests
import os

# === MODULE METADATA ===
MODULE_NAME = "DEVELOPMENT_SYSTEM"
# Cambia IP con PC del CLASSIFICATION_SYSTEM
NEXT_MODULE_URL = os.getenv("NEXT_MODULE_URL", "http://127.0.0.1:5005/process")
# =======================

app = Flask(__name__)
api = Api(app)


class Health(Resource):
    def get(self):
        return {"module": MODULE_NAME, "status": "ok"}


class Process(Resource):
    def post(self):
        """
        Modulo di sviluppo: addestra modello / prepara artefatti.
        """
        payload = request.get_json(force=True) or {}
        data = payload.get("data", {})
        metadata = payload.get("metadata", {})

        train_set = data.get("train_set", [])
        test_set = data.get("test_set", [])

        # TODO: logica reale di training / sviluppo modello
        # Esempio finto: "modello" = len(media lunghezza stringhe)
        fake_model = {"model_version": "0.0.1", "description": "fake model"}

        new_data = {
            "model": fake_model,
            "test_set": test_set
        }

        new_metadata = {
            **metadata,
            "processed_by": metadata.get("processed_by", []) + [MODULE_NAME]
        }

        new_payload = {
            "data": new_data,
            "metadata": new_metadata
        }

        try:
            resp = requests.post(NEXT_MODULE_URL, json=new_payload, timeout=5)
            resp.raise_for_status()
            downstream = resp.json()
        except Exception as e:
            return {
                "from": MODULE_NAME,
                "error": f"Failed to call next module: {e}"
            }, 500

        return {
            "from": MODULE_NAME,
            "forwarded_to": NEXT_MODULE_URL,
            "downstream_response": downstream
        }


api.add_resource(Health, "/health")
api.add_resource(Process, "/process")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
