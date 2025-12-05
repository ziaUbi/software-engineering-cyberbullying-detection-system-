import json
import pandas as pd
import requests
import random

from service_class.UniqueRandomGenerator import UniqueRandomGenerator
from service_class.service_class_parameters import ServiceClassParameters

class RecordSender:

    def __init__(self, basedir: str = "."):
        """
        Initialize the RecordSender class by reading all the data from the CSV files.

        :param basedir: Base directory of Record Sender.
        """

        self.base_dir = basedir

        # Read the data from the CSV files
        self.calendar = RecordSender.csv_reader(f"{basedir}/../data/calendar.csv")
        self.environment = RecordSender.csv_reader(f"{basedir}/../data/environment.csv")
        self.helmet = RecordSender.csv_reader(f"{basedir}/../data/helmet.csv")
        self.labels = RecordSender.csv_reader(f"{basedir}/../data/labels.csv")

        min_len = min(len(self.calendar), len(self.environment), len(self.helmet), len(self.labels))
        # However, all the dataframes should have the same length

        # UniqueRandomGenerator instance
        self.unique_random_generator = UniqueRandomGenerator(0, min_len - 1)


    @staticmethod
    def csv_reader(csv_path: str):
        """
        Read a CSV file into a pandas DataFrame.

        :param csv_path: The path to the CSV file.
        :return: A pandas DataFrame containing the CSV data.
        """

        return pd.read_csv(csv_path)


    def prepare_bucket(self, session_count: int, include_labels: bool):
        """
        Prepare a bucket containing individual records selected from random sessions.

        :param session_count: Number of sessions to include in the bucket.
        :param include_labels: Whether to include labels in the bucket.
        :return: A list of records to be sent.
        """
        self.unique_random_generator.reset()

        bucket = []
        for _ in range(session_count):
            index = self.unique_random_generator.generate()

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
        url = f"http://{ServiceClassParameters.GLOBAL_PARAMETERS['Ingestion System']['ip']}:{ServiceClassParameters.GLOBAL_PARAMETERS['Ingestion System']['port']}/send"

        while bucket:
            record = random.choice(bucket)
            try:

                # Preparing the packet to send
                packet = {
                    "port": ServiceClassParameters.GLOBAL_PARAMETERS["Service Class"]["port"],
                    "message": json.dumps(record)
                }

                response = requests.post(url, json=packet)
                if response.status_code == 200:
                    bucket.remove(record)
                else:
                    print(f"Failed to send record: {record}")
            except requests.RequestException as e:
                print(f"Error sending record: {e}")
