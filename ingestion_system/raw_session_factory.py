"""
Module: raw_session_preparation
Handles the preparation of raw sessions from records.

Author: Martina Fabiani

"""
import math
import os
from .raw_session import RawSession

class RawSessionFactory:
    """
    Prepares raw sessions and marks missing samples in the records.
    """

    def create_raw_session(self, records: list):
        """
        Create a raw session from the given records.

        Args:
            records (list): List of records to include in the raw session.

        Returns:
            RawSession: A new raw session instance.
        """
        uuid = records[0]
        tweet = records[1]
        audio_data = records[2]
        events = records[3]
        label = records[4] if len(records) > 4 else None

        return RawSession(uuid, tweet, audio_data, events, label)




def mark_missing_samples(self, raw_session, placeholder):
    """
    Check tweet, audio_data, and events fields.
    Replace missing/empty values with placeholder.
    """

    missing_samples = 0

    # --- TWEET (str) ---
    tweet = raw_session.tweet
    if (
        tweet is None
        or (isinstance(tweet, str) and tweet.strip() == "")
        or (isinstance(tweet, float) and math.isnan(tweet))
    ):
        raw_session.tweet = placeholder
        missing_samples += 1

    # --- AUDIO_DATA (file) ---
    audio = raw_session.audio_data
    if (
        audio is None
        or (isinstance(audio, str) and not os.path.exists(audio))  # path non valido
        or (isinstance(audio, float) and math.isnan(audio))
        or audio == ""  # path vuoto
    ):
        raw_session.audio_data = placeholder
        missing_samples += 1

    # --- EVENTS (list of timeseries) ---
    events = raw_session.events
    if (
        events is None
        or (isinstance(events, list) and len(events) == 0)
    ):
        raw_session.events = placeholder
        missing_samples += 1

    return missing_samples, raw_session


