# raw_session_creator.py

from typing import Tuple, Any
from ingestion_system.ingestion_configuration import Parameters
from ingestion_system.raw_session import RawSession


class RawSessionCreator:
    """
    Responsible for:
    - creating a RawSession from buffered records,
    - marking missing samples,
    - validating the resulting RawSession.
    """

    def __init__(self, config: Parameters):
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
        Mark missing/invalid sources.
        - Events: Checks if the strings in the list belong to the allowed vocabulary.
        """
        missing_count = 0
        
        EVENT_MAPPING = {
            "score": 0, "sending-off": 1, "caution": 2, 
            "substitution": 3, "foul": 4
        }
        
        # Use a set for faster lookup (O(1))
        VALID_EVENT_KEYS = set(EVENT_MAPPING.keys())

        events = raw_session.events

        if isinstance(events, list):
            # Use enumerate to modify the list at index 'i'
            for i, event_item in enumerate(events):
                
                # Check if it is a valid string
                if not isinstance(event_item, str):
                    missing_count += 1
                    events[i] = str(placeholder)
                    continue

                # Check if the event is in the valid keys
                if event_item.lower() not in VALID_EVENT_KEYS:
                    missing_count += 1
                    # Replace the invalid value with the placeholder
                    events[i] = str(placeholder)

        validate = self.validate_raw_session(missing_count)
        return validate, raw_session

    def validate_raw_session(self, missing_count) -> bool:
        """
        Check whether the RawSession is valid according to the configuration.
        BPMN gateway: 'RAW SESSION VALID?'.
        Rule: the number of missing sources must be <= maxNumMissingSamples.
        """
        return missing_count <= self.config.configuration["maxNumMissingSamples"]
