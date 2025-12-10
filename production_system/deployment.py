"""Classifier deployment helper for the cyberbullying project."""
from __future__ import annotations

from pathlib import Path


class Deployment:
    """Persist the classifier artefact received from the development system."""

    MODEL_FILENAME = "cyberbullying_classifier.sav"

    def __init__(self) -> None:
        self._model_path = Path(__file__).resolve().parent / "model" / self.MODEL_FILENAME
        self._model_path.parent.mkdir(parents=True, exist_ok=True)

    def deploy(self, classifier: str) -> bool:
        """Save the binary classifier payload into the model folder."""
        try:
            binary_content = classifier.encode("latin1")
            with self._model_path.open("wb") as model_file:
                model_file.write(binary_content)
            return True
        except (UnicodeEncodeError, OSError):
            return False
