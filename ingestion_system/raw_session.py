# raw_session.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import json

@dataclass
class RawSession:
    """
    Represents a raw session.
    """
    # --- DICHIARAZIONE CAMPI (Fondamentale per asdict) ---
    uuid: str
    tweet: Optional[Any] = None
    audio: Optional[Any] = None
    events: Optional[List[Any]] = None
    label: Optional[str] = None

    # --- RIMUOVI IL METODO __init__ MANUALE! ---
    # La dataclass lo crea automaticamente basandosi sui campi qui sopra.

    def to_json(self) -> str:
        """
        Convert the RawSession instance into a JSON string.
        """
        # Ora puoi usare self.tweet, self.audio etc. normalmente
        return json.dumps({
            "uuid": self.uuid,
            "tweet": self.tweet,
            "audio": self.audio,
            "events": self.events,
            "label": self.label
        })