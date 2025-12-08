# record_sufficiency_checker.py
from typing import Set

from typing import List, Optional, Any
from .ingestion_configuration import Parameters  
from .record_buffer import RecordBufferController 

class RecordSufficiencyChecker:
    """
    Service class that checks whether we have enough records in the buffer
    to build a RawSession (BPMN gateway: 'RECORDS SUFFICIENT?').
    """

    def __init__(self, buffer: RecordBufferController):
        """
        Initialize the checker with configuration and buffer access.
        
        :param buffer: Instance of RecordBufferController to access the DB.
        """
        self.buffer = buffer

    def are_records_sufficient(self, uuid: str, current_phase: str) -> bool:
        """
        Return True if all required sources for this UUID are present
        in the buffer, based on the current system phase.
        
        Logic:
        - Tweet, Audio, Events: ALWAYS required.
        - Label: Required ONLY if phase is NOT 'production'.
        """
        
        stored_records = self.buffer.get_records(uuid)
        
        if not stored_records:
            return False

        # 0=UUID, 1=Tweet, 2=Audio, 3=Events, 4=Label
        has_tweet = stored_records[1] is not None
        has_audio = stored_records[2] is not None
        has_events = stored_records[3] is not None
        has_label = stored_records[4] is not None

        core_requirements_met = has_tweet and has_audio and has_events
        
        if not core_requirements_met:
            return False
        
        # if not production, label is also required
        if current_phase != "production":
            if not has_label:
                return False
        
        return True