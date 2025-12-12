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


    def correct_missing_samples(self, raw_session: RawSession, placeholder: Any) -> RawSession:
        """
            Corrects missing samples in the RawSession.
            - Events: Replaces placeholders with the MODE (most frequent event) of the list.
            """
        
        # Access the events list directly from the object
        events = raw_session.events
        
        # Proceed only if events is a valid, non-empty list
        if isinstance(events, list) and events:
            
            # 1. Filter out placeholders to find valid events
            # We look for strings that are NOT the placeholder and NOT None
            valid_events = [
                e for e in events 
                if e != str(placeholder) and e is not None
            ]

            # 2. Calculate the MODE (most frequent event)
            if valid_events:
            # most_common(1) returns a list like [('foul', 3)]
                mode_event = Counter(valid_events).most_common(1)[0][0]
            else:
                return raw_session  # No valid events to determine mode
            

            # 3. Replace placeholders with the mode
            for i in range(len(events)):
                current_event = events[i]
                
                # Check if current event is a placeholder, None, or invalid type
                if (current_event == str(placeholder) or 
                    current_event is None or 
                    not isinstance(current_event, str)):
                    
                    events[i] = mode_event

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
        
        # Iteriamo su tutte le feature presenti nel dizionario
        for key, value in session.features.items():
            
            # Applichiamo la logica SOLO alle feature audio
            if key.startswith("audio_"):
                
                # Controllo di sicurezza se il valore fosse None (non dovrebbe, ma per robustezza)
                if value is None:
                    session.features[key] = 0.0
                    continue
                
                # Logica di Clamping
                if value < min_gain:
                    session.features[key] = min_gain
                elif value > max_gain:
                    session.features[key] = max_gain
                
                # Se il valore è nel range, lo lasciamo invariato

        return session