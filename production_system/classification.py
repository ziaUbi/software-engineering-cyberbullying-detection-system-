"""Inference component for cyberbullying detection."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np

import joblib
import pandas as pd

from .label import Label


class Classification:
    """Load the deployed classifier and translate sessions into simple moderation labels."""

    MODEL_FILENAME = "cyberbullying_classifier.sav"

    def __init__(self) -> None:
        self._classifier = None
        self._model_path = Path(__file__).resolve().parent / "model" / self.MODEL_FILENAME

    def _ensure_classifier(self) -> None:
        if self._classifier is None:
            if not self._model_path.exists():
                raise FileNotFoundError(f"Classifier artefact not found at {self._model_path}")
            self._classifier = joblib.load(self._model_path)

    def classify(self, prepared_session: Dict[str, Any], classifier_deployed: bool) -> Optional[Label]:
        """Return a :class:`Label` when a classifier is available."""
        if classifier_deployed is False:
            return None

        self._ensure_classifier()
        
        # Costruzione del feature vector basato sulle nuove specifiche PDF
        features_df = self._build_feature_frame(prepared_session)
        
        # Esecuzione predizione
        prediction = self._classifier.predict(features_df)[0]
        prediction_int = int(prediction)

        # Mapping binario: 0 -> safe, 1 -> bullying
        if prediction_int == 0:
            verdict = "safe"
        else:
            verdict = "bullying"

        return Label(
            uuid=prepared_session["uuid"],
            label=verdict
        )

    def _build_feature_frame(self, prepared_session: Dict[str, Any]) -> pd.DataFrame:
        """Convert the list-based session payload into a flat DataFrame for the model."""
        # NOTA: Le specifiche PDF  passano liste (text, audio, events).
        # Un modello ML classico (sklearn) vuole un array piatto di numeri.
        # Qui facciamo un'aggregazione semplice (media/conteggio) per rendere i dati compatibili.
        # Se il modello usa Deep Learning, questa logica andrebbe adattata per passare tensori.
        
        audio_vector = prepared_session.get("audio", [])
        events_vector = prepared_session.get("events", [])
        text_list = prepared_session.get("text", [])
        
        feature_struct = {
            # Mappiamo il campo 'tweetLenght' (con typo PDF) a snake_case pulito
            "tweet_length": prepared_session.get("tweetLenght", 0),
            
            # Feature engineering di base sui vettori ricevuti
            "audio_mean": np.mean(audio_vector) if audio_vector else 0.0,
            "audio_max": np.max(audio_vector) if audio_vector else 0.0,
            "events_count": len(events_vector),
            "events_sum": np.sum(events_vector) if events_vector else 0,
            "text_segments_count": len(text_list)
        }
        return pd.DataFrame([feature_struct])