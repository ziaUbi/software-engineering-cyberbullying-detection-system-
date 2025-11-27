# classification_service/app.py
from flask import Flask, request
from flask_restful import Api, Resource
import requests
import os

# === MODULE METADATA ===
MODULE_NAME = "CLASSIFICATION_SYSTEM"
# Cambia IP con PC dell'EVALUATION_SYSTEM
NEXT_MODULE_URL = os.getenv("NEXT_MODULE_URL", "http://127.0.0.1:5006/process")
# =======================

app = Flask(__name__)
api = Api(app)


class Health(Resource):
    def get(self):
        return {"module": MODULE_NAME, "status": "ok"}


class Process(Resource):
    def post(self):
        """
        Usa il modello per classificare il test_set e inoltra i risultati per la valutazione.
        """
        payload = request.get_json(force=True) or {}
        data = payload.get("data", {})
        metadata = payload.get("metadata", {})

        model = data.get("model", {})
        test_set = data.get("test_set", [])

        # TODO: logica reale di classificazione
        # Esempio finto: per ogni elemento, prediction = "POSITIVE"
        predictions = [{"input": x, "prediction": "POSITIVE"} for x in test_set]

        new_data = {
            "model": model,
            "test_set": test_set,
            "predictions": predictions
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
    app.run(host="0.0.0.0", port=5005, debug=True)
