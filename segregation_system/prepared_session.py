from dataclasses import dataclass, asdict
from typing import List, Any

@dataclass
class PreparedSession:
    uuid: str
    text: List[str]
    tweet_length: int
    audio_db: List[float]
    events: List[int]
    label: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict):
        return PreparedSession(
            uuid=data.get("uuid"),
            text=data.get("text", []),
            tweet_length=data.get("tweet_length", 0),
            audio_db=data.get("audio_db", []),
            events=data.get("events", []),
            label=data.get("label", "")
        )