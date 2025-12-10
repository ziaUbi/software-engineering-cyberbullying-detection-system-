import json
import pandas as pd
import requests
import random
from pydub import AudioSegment
from io import BytesIO
import base64

from service_class.service_class_parameters import ServiceClassParameters

class RecordSender:

    def __init__(self, basedir: str = "."):
        """
        Initialize the RecordSender class by reading all the data from the CSV files.

        :param basedir: Base directory of Record Sender.
        """
        # Read the records data from the CSV files
        print(basedir)
        self.tweets = pd.read_csv(f"{basedir}/data/tweets.csv")
        self.events = pd.read_csv(f"{basedir}/data/events.csv")
        self.audio = AudioSegment.from_mp3(f"{basedir}/data/audio.mp3")
        self.audio_duration_ms = len(self.audio)
        self.clip_duration_ms = 20 * 1000 # 20 seconds in milliseconds
        self.labels = pd.read_csv(f"{basedir}/data/labels.csv")

        self.min_len = min(len(self.tweets), len(self.events), len(self.labels))

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
                "source": "tweet",
                "value": self.tweets.iloc[index].to_dict()
            })
            bucket.append({
                "source": "events",
                "value": self.events.iloc[index].to_dict()
            })

            max_start = max(0, self.audio_duration_ms - self.clip_duration_ms)
            start_ms = random.randint(0, max_start)
            end_ms = start_ms + self.clip_duration_ms
            # extract the audio slice
            audio_slice = self.audio[start_ms:end_ms]
            # Convert to bytes (WAV for simplicity)
            buffer = BytesIO()
            audio_slice.export(buffer, format="wav")
            audio_bytes = buffer.getvalue()
            audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

            bucket.append({
                "source": "audio",
                "value": {"audio": audio_b64, "uuid": self.tweets.iloc[index].to_dict()["uuid"]}
            })

            if include_labels:
                bucket.append({
                    "source": "label",
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
                    "payload": json.dumps(record)
                }

                response = requests.post(url, json=packet)
                if response.status_code == 200:
                    bucket.remove(record)
                else:
                    print(f"Failed to send record: {record}")
            except requests.RequestException as e:
                print(f"Error sending record: {e}")
