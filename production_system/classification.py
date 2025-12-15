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
        
        # Construction of the feature vector based on the new PDF specifications
        features_df = self._build_feature_frame(prepared_session)
        
        # Execution of the prediction
        prediction = self._classifier.predict(features_df)[0]
        prediction_int = int(prediction)

        # 0 -> not cyberbullying, 1 -> cyberbullying
        if prediction_int == 0:
            verdict = "not_cyberbullying"
        else:
            verdict = "cyberbullying"

        return Label(
            uuid=prepared_session["uuid"],
            label=verdict
        )

    def _build_feature_frame(self, prepared_session: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert the prepared session dict into a DataFrame.
        Input: Dict (dalla PreparedSession)
        Output: DataFrame
        """
        feature_struct = {
            # 1. Textual features
            "tweet_length": prepared_session["tweet_length"],
            
            # 2. Bag of Words (specific word counts)
            "word_fuck": prepared_session["word_fuck"],
            "word_bulli": prepared_session["word_bulli"],
            "word_muslim": prepared_session["word_muslim"],
            "word_gay": prepared_session["word_gay"],
            "word_nigger": prepared_session["word_nigger"],
            "word_rape": prepared_session["word_rape"],
            
            # 3. Events
            "event_score": prepared_session["event_score"],
            "event_sending_off": prepared_session["event_sending-off"],
            "event_caution": prepared_session["event_caution"],
            "event_substitution": prepared_session["event_substitution"],
            "event_foul": prepared_session["event_foul"],
            
            # 4. Feature Audios
            "audio_0": prepared_session["audio_0"],
            "audio_1": prepared_session["audio_1"],
            "audio_2": prepared_session["audio_2"],
            "audio_3": prepared_session["audio_3"],
            "audio_4": prepared_session["audio_4"],
            "audio_5": prepared_session["audio_5"],
            "audio_6": prepared_session["audio_6"],
            "audio_7": prepared_session["audio_7"],
            "audio_8": prepared_session["audio_8"],
            "audio_9": prepared_session["audio_9"],
            "audio_10": prepared_session["audio_10"],
            "audio_11": prepared_session["audio_11"],
            "audio_12": prepared_session["audio_12"],
            "audio_13": prepared_session["audio_13"],
            "audio_14": prepared_session["audio_14"],
            "audio_15": prepared_session["audio_15"],
            "audio_16": prepared_session["audio_16"],
            "audio_17": prepared_session["audio_17"],
            "audio_18": prepared_session["audio_18"],
            "audio_19": prepared_session["audio_19"],
        }
        
        # Creation of the DataFrame with a single row (index=[0])
        return pd.DataFrame([feature_struct])


