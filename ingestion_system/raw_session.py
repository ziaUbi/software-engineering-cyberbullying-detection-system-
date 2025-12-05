"""
Module: raw_session
This module represents a raw session composed of multiple records (4/5).

Author: Martina Fabiani
"""
import json


class RawSession:
    """
    Represents a raw session, which aggregates records and stores session data.

    Attributes:
        uuid (str): Unique identifier for the session.
        tweet (str): tweets associated with the session.
        audio_data (file): audio data associated with the session.
        events (list timeseries): List of events recorded during the session.
        label (str): Optional label for the session.
    """

    def __init__(self, uuid, tweet, audio_data, events, label=None):
        """
        Initialize a raw session instance.

        Args:
            uuid (str): Unique identifier for the session.
            tweet (str): tweets associated with the session.
            audio_data (file): audio data associated with the session.
            events (list timeseries): List of events recorded during the session.
            label (str): Optional label for the session.
        """
        self.uuid = uuid
        self.tweet = tweet
        self.audio_data = audio_data
        self.events = events
        self.label = label

    def to_json(self):
        """
        Convert the instance attributes to a JSON string.

        Returns:
            str: JSON string representing the instance attributes.
        """
        return json.dumps({
            "uuid": self.uuid,
            "tweet": self.tweet,
            "audio_data": self.audio_data,  # Note: Ensure audio_data is serializable
            "events": self.events,
            "label": self.label
        })