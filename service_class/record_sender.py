import json
import pandas as pd
import requests
import random

from service_class.service_class_parameters import ServiceClassParameters

class RecordSender:

    def __init__(self, basedir: str = "."):
        """
        Initialize the RecordSender class by reading all the data from the CSV files.

        :param basedir: Base directory of Record Sender.
        """
        self.base_dir = basedir
        # Read the records data from the CSV files
        self.calendar = pd.read_csv(f"{basedir}/../data/calendar.csv")
        self.environment = pd.read_csv(f"{basedir}/../data/environment.csv")
        self.helmet = pd.read_csv(f"{basedir}/../data/helmet.csv")
        self.labels = pd.read_csv(f"{basedir}/../data/labels.csv")

        self.min_len = min(len(self.calendar), len(self.environment), len(self.helmet), len(self.labels))


    def prepare_bucket(self, session_count: int, include_labels: bool):
        """
        Prepare a bucket containing individual records selected from random sessions.

        :param session_count: Number of sessions to include in the bucket.
        :param include_labels: Whether to include labels in the bucket.
        :return: A list of records to be sent.
        """
        indexes = random.sample(range(self.min_len), session_count)

        bucket = []
        for _ in range(session_count):
            index = indexes.pop()

            bucket.append({
                "source": "calendar",
                "value": self.calendar.iloc[index].to_dict()
            })
            bucket.append({
                "source": "environment",
                "value": self.environment.iloc[index].to_dict()
            })
            bucket.append({
                "source": "helmet",
                "value": self.helmet.iloc[index].to_dict()
            })

            if include_labels:
                bucket.append({
                    "source": "labels",
                    "value": self.labels.iloc[index].to_dict()
                })

        return bucket

    def send_bucket(self, bucket: list):
        """
        Send records from the bucket to the Ingestion System randomly.

        :param bucket: The list of records to send.
        """
        ip = ServiceClassParameters.GLOBAL_PARAMETERS['Ingestion System']['ip']
        port = ServiceClassParameters.GLOBAL_PARAMETERS['Ingestion System']['port']

        url = f"http://{ip}:{port}/send"

        while bucket:
            record = random.choice(bucket)
            try:

                packet = {
                    "port": port,
                    "message": json.dumps(record)
                }

                response = requests.post(url, json=packet)
                if response.status_code == 200:
                    bucket.remove(record)
                else:
                    print(f"Failed to send record: {record}")
            except requests.RequestException as e:
                print(f"Error sending record: {e}")
