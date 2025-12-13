import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from production_system.classification import Classification

class TestClassification:

    @patch("joblib.load")
    @patch("pathlib.Path.exists", return_value=True)
    def test_classify_success(self, mock_exists, mock_joblib_load):
        """Testa una classificazione corretta."""
        clf = Classification()
        
        # Mock del modello sklearn
        mock_model = MagicMock()
        # predict ritorna un array numpy, es. [1] per cyberbullying
        mock_model.predict.return_value = [1] 
        mock_joblib_load.return_value = mock_model

        # Sessione input fittizia
        session = {
            "uuid": "test-uuid",
            "tweet_length": 10,
            "word_fuck": 0, "word_bulli": 0, "word_muslim": 0, "word_gay": 0, 
            "word_nigger": 0, "word_rape": 0, "event_score": 0, 
            "event_sending-off": 0, "event_caution": 0, "event_substitution": 0, 
            "event_foul": 0
        }
        # Aggiungi le chiavi audio mancanti
        for i in range(20):
            session[f"audio_{i}"] = 0.0

        label = clf.classify(session, classifier_deployed=True)

        assert label is not None
        assert label.uuid == "test-uuid"
        assert label.label == "cyberbullying" # Poiché predict ha tornato 1

    def test_classify_not_deployed(self):
        """Se il flag deployed è False, deve tornare None subito."""
        clf = Classification()
        res = clf.classify({}, classifier_deployed=False)
        assert res is None