import numpy as np
import re
import os
from typing import List, Dict, Any, Union
from dataclasses import dataclass, asdict

# Import opzionale per l'audio
try:
    import librosa
except ImportError:
    librosa = None

from preparation_system.preparation_configuration import PreparationSystemParameters

@dataclass
class PreparedSession:
    uuid: str
    badWords: List[int]       # Bag of Words vector (0/1)
    tweet_length: int
    audio_db: List[float]
    events: List[int]
    label: str

    def to_dict(self):
        return asdict(self)

class PreparedSessionCreator:
    """
    Class responsible for extracting features from the corrected RawSession.
    """

    EVENT_MAPPING = {
        "score": 0,
        "sending-off": 1,
        "caution": 2,
        "substitution": 3,
        "foul": 4,
        "unknown": 99
    }

    BOW_VOCABULARY = ["fuck", "bulli", "muslim", "gay", "nigger", "rape"]

    def __init__(self, config: PreparationSystemParameters):
        self.config = config

    def create_prepared_session(self, raw_session: Any) -> PreparedSession:
        """
        Orchestrates feature extraction including Stopword removal.
        """
        
        # --- 1. PREPROCESSING TESTO (Stopwords & Cleaning) ---
        # Otteniamo la lista di token puliti (senza punteggiatura e senza stopwords)
        clean_tokens = self._preprocess_text(raw_session.tweet)

        # --- 2. EXTRACT TEXT FEATURES ---
        # Feature A: Lunghezza del tweet (basata sui token puliti)
        tweet_len = len(clean_tokens)

        # Feature B: Bag of Words (usando i token puliti)
        bow_vector = self._create_bow_vector(clean_tokens)

        # --- 3. EXTRACT AUDIO FEATURES ---
        audio_decibels = self._extract_audio_features(raw_session.audio)

        # --- 4. EXTRACT EVENT FEATURES ---
        event_ids = self._extract_event_features(raw_session.events)

        # --- 5. LABEL ---
        label_val = raw_session.label if raw_session.label else ""

        return PreparedSession(
            uuid=raw_session.uuid,
            badWords=bow_vector,
            tweet_length=tweet_len,
            audio_db=audio_decibels,
            events=event_ids,
            label=label_val
        )

    def _preprocess_text(self, text: str) -> List[str]:
        """
        Cleans text and removes STOPWORDS.
        Returns a list of significant tokens.
        """
        if not text:
            return []

        # 1. Lowercase
        text = text.lower()
        
        # 2. Rimuove punteggiatura
        text = re.sub(r'[^\w\s]', '', text)
        
        # 3. Tokenizzazione iniziale
        tokens = text.split()

        # 4. RIMOZIONE STOPWORDS
        # Recupera la lista dal file di configurazione
        stop_words = set(self.config.stopword_list)
        
        # Filtra i token: tiene solo quelli che NON sono nella stopword list
        filtered_tokens = [t for t in tokens if t not in stop_words]

        return filtered_tokens

    def _create_bow_vector(self, tokens: List[str]) -> List[int]:
        """
        Creates binary BoW vector from the CLEANED list of tokens.
        Vocabulary: (fuck, bulli, muslim, gay, nigger, rape)
        """
        # Inizializza vettore a zeri
        bow_vector = [0] * len(self.BOW_VOCABULARY)
        
        # Convertiamo la lista in set per ricerca O(1)
        tokens_set = set(tokens)

        for i, target_word in enumerate(self.BOW_VOCABULARY):
            if target_word in tokens_set:
                bow_vector[i] = 1
            else:
                bow_vector[i] = 0
        
        return bow_vector

    def _extract_audio_features(self, file_path_dict: Union[Dict, str]) -> List[float]:
        """
        Extracts decibels from audio using Librosa.
        """
        file_path = ""
        if isinstance(file_path_dict, dict):
            file_path = file_path_dict.get("file_path", "")
        elif isinstance(file_path_dict, str):
            file_path = file_path_dict
        
        if not file_path:
            return []

        if not os.path.exists(file_path):
            return [0.0]

        if librosa:
            try:
                y, sr = librosa.load(file_path, sr=None)
                rms = librosa.feature.rms(y=y)[0]
                db_values = librosa.amplitude_to_db(rms, ref=np.max)
                return db_values.tolist()
            except Exception as e:
                print(f"Error processing audio: {e}")
                return []
        return []

    def _extract_event_features(self, events: List[Dict]) -> List[int]:
        """
        Maps event strings to integers.
        """
        encoded_events = []
        if not events or not isinstance(events, list):
            return []

        for event_item in events:
            event_name = event_item.get("event")
            if event_name:
                event_name_key = str(event_name).lower()
                event_id = self.EVENT_MAPPING.get(event_name_key, self.EVENT_MAPPING["unknown"])
                encoded_events.append(event_id)
        
        return encoded_events