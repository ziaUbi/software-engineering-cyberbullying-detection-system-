# evaluation_service/app.py
from flask import Flask, request
from flask_restful import Api, Resource
import os

# === MODULE METADATA ===
MODULE_NAME = "EVALUATION_SYSTEM"
# Ultimo modulo: non serve NEXT_MODULE_URL
# =======================

app = Flask(__name__)
api = Api(app)


class Health(Resource):
    def get(self):
        return {"module": MODULE_NAME, "status": "ok"}


class Process(Resource):
    def post(self):
        """
        Ultimo modulo: calcola le metriche e chiude la pipeline.
        """
        payload = request.get_json(force=True) or {}
        data = payload.get("data", {})
        metadata = payload.get("metadata", {})

        predictions = data.get("predictions", [])
        # TODO: aggiungere ground truth / target nel payload a monte

        # TODO: logica reale di evaluation (accuracy, f1, ecc.)
        # Esempio finto:
        fake_metrics = {
            "accuracy": 0.8,
            "note": "Fake metrics, replace with real evaluation logic."
        }

        new_metadata = {
            **metadata,
            "processed_by": metadata.get("processed_by", []) + [MODULE_NAME]
        }

        return {
            "from": MODULE_NAME,
            "final_metrics": fake_metrics,
            "metadata": new_metadata
        }


api.add_resource(Health, "/health")
api.add_resource(Process, "/process")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)
