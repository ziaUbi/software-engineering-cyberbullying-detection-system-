import numpy as np
import re
import os
from typing import List, Dict, Any, Union
from dataclasses import dataclass, field
from collections import Counter 
import librosa 
from preparation_system.preparation_configuration import PreparationSystemParameters

@dataclass
class PreparedSession:

    uuid: str
    label: str
    features: Dict[str, Union[int, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = {"uuid": self.uuid, "label": self.label}
        data.update(self.features)
        return data

class PreparedSessionCreator:
    
    EVENT_MAPPING = {
        "score": 0, "sending-off": 1, "caution": 2, 
        "substitution": 3, "foul": 4
    }

    BOW_VOCABULARY = ["fuck", "bulli", "muslim", "gay", "nigger", "rape"]

    MAX_AUDIO_SAMPLES = 20

    def __init__(self, config: PreparationSystemParameters):
        self.config = config

    def create_prepared_session(self, raw_session: Any) -> PreparedSession:
        
        enabled_features = self.config.features
        flat_features = {}

        clean_tokens = []
        if "tweetLength" in enabled_features or "badWords" in enabled_features:
            clean_tokens = self._preprocess_text(raw_session.get("tweet"))

        # 1. TWEET LENGTH
        if "tweetLength" in enabled_features:
            flat_features["tweet_length"] = len(clean_tokens)

        # 2. BAG OF WORDS (FREQUENCY)
        if "badWords" in enabled_features:
            bow_dict = self._create_flat_bow(clean_tokens)
            flat_features.update(bow_dict)
        
        # 3. AUDIO (FLATTENED & PADDED)
        if "audioDecibels" in enabled_features:
            raw_audio = self._extract_audio_features(raw_session.get("audio"))
            padded_audio = self._pad_or_truncate(raw_audio, self.MAX_AUDIO_SAMPLES, fill_value=0.0)
            for i, val in enumerate(padded_audio):
                flat_features[f"audio_{i}"] = val

        # 4. EVENTS (FREQUENCY)
        if "matchEvents" in enabled_features:
            events_dict = self._create_flat_events(raw_session.get("events"))
            flat_features.update(events_dict)

        label_val = raw_session.get("label", "")

        return PreparedSession(
            uuid=raw_session.get("uuid"),
            label=label_val,
            features=flat_features
        )
    

    def _create_flat_bow(self, tokens: List[str]) -> Dict[str, int]:
        """
        Counts occurrences of target words in the token list.
        """
        features = {}
        
        # Counter creates occurrences of each token
        token_counts = Counter(tokens)

        for target_word in self.BOW_VOCABULARY:
            key_name = f"word_{target_word}"
            # Set count or 0 if not present
            features[key_name] = token_counts[target_word]
        
        return features

    def _create_flat_events(self, events: List[Dict]) -> Dict[str, int]:
        """
        Count occurrences of each event type based on EVENT_MAPPING.
        """
        features = {}
        
        for event_type in self.EVENT_MAPPING.keys():
            features[f"event_{event_type}"] = 0
            
        if not events or not isinstance(events, list):
            return features

        for event_item in events:
            raw_name = None

            raw_name = event_item
            
            name_key = str(raw_name).lower()
                
            if name_key in self.EVENT_MAPPING:
                features[f"event_{name_key}"] += 1
                
        return features

    # Helper Methods ------------------------------
    def _pad_or_truncate(self, vector: List[Any], target_len: int, fill_value: Any) -> List[Any]:
        # Pads or truncates a list to the target length.
        current_len = len(vector)
        if current_len >= target_len:
            return vector[:target_len]
        else:
            padding = [fill_value] * (target_len - current_len)
            return vector + padding

    def _preprocess_text(self, text: str) -> List[str]:
        # Simple text preprocessing: lowercase, remove punctuation, tokenize, remove stopwords.
        if not text: return []
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        tokens = text.split()
        stop_words = set(self.config.stopword_list)
        return [t for t in tokens if t not in stop_words]

    def _extract_audio_features(self, file_path_dict: Union[Dict, str]) -> List[float]:
        # Extract decibel values from audio file.
        
        file_path = ""
        if isinstance(file_path_dict, dict):
            file_path = file_path_dict.get("file_path", "")
        elif isinstance(file_path_dict, str):
            file_path = file_path_dict
        
        if not file_path or not os.path.exists(file_path):
            return [] 

        if librosa:
            try:
                y, sr = librosa.load(file_path, sr=None)
                rms = librosa.feature.rms(y=y)[0]
                db_values = librosa.amplitude_to_db(rms, ref=0.00001, amin=0.00001)
                return db_values.tolist()
            except Exception as e:
                print(f"Error processing audio: {e}")
                return []
        return []