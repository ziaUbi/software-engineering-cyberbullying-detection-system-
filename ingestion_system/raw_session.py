# raw_session.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import json

@dataclass
class RawSession:
    """
    Represents a raw session.
    """
    uuid: str
    tweet: Optional[Any] = None
    audio: Optional[Any] = None
    events: Optional[List[Any]] = None
    label: Optional[str] = None

    def to_json(self) -> str:
        """
        Convert the RawSession instance into a JSON string.
        """
        return json.dumps({
            "uuid": self.uuid,
            "tweet": self.tweet,
            "audio": self.audio,
            "events": self.events,
            "label": self.label
        })