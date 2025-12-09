# raw_session_creator.py

from typing import Tuple, Any
from .ingestion_configuration import IngestionConfiguration
from .raw_session import RawSession


class RawSessionCreator:
    """
    Responsible for:
    - creating a RawSession from buffered records,
    - marking missing samples,
    - validating the resulting RawSession.
    """

    def __init__(self, config: IngestionConfiguration):
        self.config = config

    def create_raw_session(self, records) -> RawSession:
        """
        Aggregate records belonging to the same UUID into a RawSession object.
        BPMN: 'CREATE RAW SESSION' task.
        """

        raw_session = RawSession(
            uuid=records[0],
            tweet=records[1],
            audio=records[2],
            events=records[3],
            label=records[4]
        )
        return raw_session

   

    def mark_missing_samples(self, raw_session: RawSession, placeholder: Any) -> Tuple[bool, RawSession]:
        """
        Mark missing sources.
        - Events: Check if specific keys inside are missing.
        """
        missing_count = 0
        events = raw_session.events

        if isinstance(events, list):
            for event_item in events:
                if event_item.get("timestamp") is None:
                    missing_count += 1
                    event_item["timestamp"] = placeholder

                if event_item.get("event") is None or isinstance(event_item.get("event"), (int, float)):
                    missing_count += 1
                    event_item["event"] = placeholder

        validate = self.validate_raw_session(missing_count)
        return validate, raw_session

    def validate_raw_session(self, missing_count) -> bool:
        """
        Check whether the RawSession is valid according to the configuration.
        BPMN gateway: 'RAW SESSION VALID?'.
        Rule: the number of missing sources must be <= maxNumMissingSamples.
        """
        return missing_count <= self.config.maxNumMissingSamples
