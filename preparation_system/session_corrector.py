from typing import Any, List, Union, Optional
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

    def correct_missing_samples(self, raw_session, placeholder) -> Any:
        """
        Corrects missing samples in the RawSession.
        - Events (Timestamp): Uses 'Linear Interpolation'.
        - Events (Name): Uses 'Forward Fill'.
        """

        events = raw_session.get("events")
        
        # Procediamo solo se events è una lista valida e non vuota
        if isinstance(events, list) and events:
            
            # A. TIMESTAMP (Interpolazione Lineare)
            for i in range(len(events)):
                # Nota: qui events[i] è già un dizionario, quindi la sintassi rimane simile
                current_ts = events[i].get("timestamp")

                if current_ts == placeholder or current_ts is None:
                    
                    # Trova il precedente (o 0.0)
                    prev_val = 0.0
                    if i > 0 and events[i-1].get("timestamp") not in [placeholder, None]:
                        prev_val = events[i-1]["timestamp"]
                    
                    # Trova il successivo
                    next_val = None
                    next_idx = -1
                    
                    for j in range(i + 1, len(events)):
                        val = events[j].get("timestamp")
                        if val != placeholder and val is not None:
                            next_val = val
                            next_idx = j
                            break
                    
                    # Calcolo
                    if next_val is not None:
                        gap = next_idx - (i - 1) if i > 0 else next_idx + 1
                        step_val = (next_val - prev_val) / gap
                        events[i]["timestamp"] = prev_val + step_val
                    else:
                        # Fallback (fine lista)
                        events[i]["timestamp"] = prev_val + 1.0

            # B. EVENT NAME (Forward Fill)
            last_valid_name = "unknown"
            
            for event_item in events:
                evt_name = event_item.get("event")
                
                if evt_name == placeholder or evt_name is None or isinstance(evt_name, (int, float)):
                    event_item["event"] = last_valid_name
                else:
                    last_valid_name = evt_name
                    
        return raw_session

    def correct_absolute_outliers(self, audio_db: List[float]) -> List[float]:
        """
        Corrects absolute outliers in the audio decibel data.
        
        Logic:
        - If value < MinDecibelGain -> clamp to MinDecibelGain
        - If value > MaxDecibelGain -> clamp to MaxDecibelGain
        
        The bounds are provided by the user via configuration.

        :param audio_db: List of float values representing audio decibels.
        :return: List of float values within the allowed bounds.
        """
        min_gain = self.config.min_decibel_gain
        max_gain = self.config.max_decibel_gain
        
        corrected_audio = []

        for value in audio_db:
            if value is None:
                # Should not happen if correct_missing_samples is called first, 
                # but for safety we keep it or assume 0.0
                corrected_audio.append(0.0) 
                continue

            if value < min_gain:
                # Clamp to lower bound
                corrected_audio.append(min_gain)
            elif value > max_gain:
                # Clamp to upper bound
                corrected_audio.append(max_gain)
            else:
                # Value is valid
                corrected_audio.append(value)

        return corrected_audio
