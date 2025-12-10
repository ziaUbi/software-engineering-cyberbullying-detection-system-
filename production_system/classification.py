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
            self._classifier = joblib.load(self._model_path)    # Carica il modello ML salvato

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

        # Mapping binario: 0 -> not cyberbullying, 1 -> cyber5+
        # +bullying
        if prediction_int == 0:
            verdict = "not cyberbullying"
        else:
            verdict = "cyberbullying"

        return Label(
            uuid=prepared_session["uuid"],
            label=verdict
        )

    def _build_feature_frame(self, prepared_session: Dict[str, Any]) -> pd.DataFrame:
        """Convert the prepared session payload into a DataFrame."""
        
        # Rimuoviamo i campi di metadati che non servono al classificatore
        features_only = prepared_session.copy()
        if "uuid" in features_only:
            del features_only["uuid"]
        if "label" in features_only:
            del features_only["label"]
            
        # Il modello (joblib) si aspetta le colonne nello stesso ordine del training.
        # Creiamo un DataFrame con una sola riga.
        # NOTA: Se il dizionario ha chiavi extra che il modello non conosce, 
        # sklearn di solito le ignora o da errore a seconda della versione.
        # L'ideale è assicurarsi che features_only corrisponda alle feature del training.
        
        return pd.DataFrame([features_only])