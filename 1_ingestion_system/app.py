#----------------------------------------------

#   allows data to be uploaded via .csv and combine them

#----------------------------------------------

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import requests
import os

# === MODULE METADATA ===
MODULE_NAME = "INGESTION_SYSTEM"
# Di default punta al PREPARATION_SYSTEM, ma si può sovrascrivere con una env var
NEXT_MODULE_URL = os.getenv("NEXT_MODULE_URL", "http://192.168.1.11:5002/process")
# =======================

app = Flask(__name__)
api = Api(app)


class Health(Resource):
    def get(self):
        return {"module": MODULE_NAME, "status": "ok"}


class Process(Resource):
    def post(self):
        """
        Primo modulo della pipeline.
        Riceve un JSON del tipo:
        {
          "raw_text": "stringa di input"
        }
        Lo converte nel payload standard e lo inoltra al modulo successivo.
        """
        body = request.get_json(force=True) or {}

        raw_text = body.get("raw_text", "")

        # Costruisco il payload standard
        payload = {
            "data": {
                "text": raw_text
            },
            "metadata": {
                "source": MODULE_NAME,
                "processed_by": [MODULE_NAME]
            }
        }

        # Inoltra al modulo successivo
        resp = requests.post(NEXT_MODULE_URL, json=payload, timeout=5)
        resp.raise_for_status()

        return {
            "from": MODULE_NAME,
            "forwarded_to": NEXT_MODULE_URL,
            "downstream_response": resp.json()
        }


api.add_resource(Health, "/health")
api.add_resource(Process, "/process")


if __name__ == "__main__":
    # esponi su tutta la rete locale
    app.run(host="0.0.0.0", port=5001, debug=True)
