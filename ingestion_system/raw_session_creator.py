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
        Mark which sources are missing in the RawSession (tweet or audio).
        Checks if fields are NaN or numbers.
        
        Returns:
            number of missing samples (int)
            raw_session updated (RawSession)
        """
        missing_count = 0
        fields_to_check = ['tweet', 'audio']

        for field in fields_to_check:
            # get the value of the field
            value = getattr(raw_session, field)

            # check if the value is missing (NaN or number)
            if isinstance(value, (int, float)):
                missing_count += 1
                # set the field to the placeholder
                setattr(raw_session, field, placeholder)

        validate = self.validate_raw_session(missing_count)
        return validate, raw_session

    def validate_raw_session(self, missing_count) -> bool:
        """
        Check whether the RawSession is valid according to the configuration.
        BPMN gateway: 'RAW SESSION VALID?'.
        Rule: the number of missing sources must be <= maxNumMissingSamples.
        """
        return missing_count <= self.config.maxNumMissingSamples
