from typing import Any, List, Union, Optional
from collections import Counter
from ingestion_system import raw_session
from ingestion_system.raw_session import RawSession
from preparation_system.preparation_configuration import PreparationSystemParameters

class SessionCorrector:
    """
    Class responsible for correcting anomalies in the session data.
    Corresponds to the 'CORRECT MISSING SAMPLES' and 'CORRECT ABSOLUTE OUTLIERS'
    tasks in the BPMN.
    """

    def __init__(self, config: PreparationSystemParameters):
        """
        Initialize the SessionCorrector with the system configuration.

        :param config: Instance of PreparationSystemParameters containing limits (Min/Max Decibel).
        """
        self.config = config


    def correct_missing_samples(self, raw_session: Any, placeholder: Any) -> Any:
        """
            Corrects missing samples in the RawSession.
            - Events: Replaces placeholders with the MODE (most frequent event) of the list.
            Handles both Dictionary and Object (RawSession) input.
        """
        
        events = None
        if isinstance(raw_session, dict):
            events = raw_session.get("events")
        else:
            events = raw_session.events

        # Proceed only if events is a valid, non-empty list
        if isinstance(events, list) and events:
            
            # Filter out placeholders to find valid events
            valid_events = [
                e for e in events 
                if e != str(placeholder) and e is not None
            ]

            # Calculate the MODE
            if valid_events:
                mode_event = Counter(valid_events).most_common(1)[0][0]
            else:
                return raw_session 

            # Replace placeholders with the mode
            for i in range(len(events)):
                current_event = events[i]
                
                if (current_event == str(placeholder) or 
                    current_event is None or 
                    not isinstance(current_event, str)):
                    
                    events[i] = mode_event
            
            # Update the raw_session with corrected events
            if isinstance(raw_session, dict):
                raw_session["events"] = events
            else:
                raw_session.events = events
                
        return raw_session

    def correct_absolute_outliers(self, session):
        """
        Corrects absolute outliers in the audio decibel data within the PreparedSession features.
        
        Logic:
        - Iterates through session.features looking for keys starting with "audio_".
        - If value < MinDecibelGain -> clamp to MinDecibelGain
        - If value > MaxDecibelGain -> clamp to MaxDecibelGain
        
        :param session: The PreparedSession object with flattened features.
        :return: The modified PreparedSession object.
        """
        min_gain = self.config.min_decibel_gain
        max_gain = self.config.max_decibel_gain
        
        # Iterate through all features
        for key, value in session.features.items():
            
            # Apply logic ONLY to audio features
            if key.startswith("audio_"):
                
                # Safety check if the value is None (should not be, but for robustness)
                if value is None:
                    session.features[key] = 0.0
                    continue
                
                # Clamping logic
                if value < min_gain:
                    session.features[key] = min_gain
                elif value > max_gain:
                    session.features[key] = max_gain
                
                # If the value is within range, leave it unchanged

        return session