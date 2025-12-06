# raw_session.py
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


import json

class RawSession:
    """
    Represents a raw session, aggregating heterogeneous records coming from 
    multiple client-side systems (tweet, audio, events, label). 
    
    Attributes:
        uuid (str): Unique identifier of the session.
        tweet: Record coming from the tweet client system.
        audio: Record coming from the audio client system.
        events: Time-series events describing contextual information.
        label: Label used for evaluation (may be None during production).
    """

    def __init__(self, uuid, tweet=None, audio=None, events=None, label=None):
        """
        Initialize a RawSession instance.
        """
        self.uuid = uuid
        self.tweet = tweet
        self.audio = audio
        self.events = events
        self.label = label

    def to_json(self) -> str:
        """
        Convert the RawSession instance into a JSON string.
        Useful for sending the session to the Preparation System.
        
        Returns:
            str: JSON representation of the RawSession.
        """
        return json.dumps({
            "uuid": self.uuid,
            "tweet": self.tweet,
            "audio": self.audio,
            "events": self.events,
            "label": self.label
        })
