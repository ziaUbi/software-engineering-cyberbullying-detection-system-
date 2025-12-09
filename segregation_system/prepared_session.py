from dataclasses import dataclass, asdict
from typing import List, Tuple


@dataclass
class PreparedSession:
    """
    The `PreparedSession` class represents a prepared session for a data segregation system.
    """
    uuid: str
    text: List[str]
    tweet_length: int
    audio_db: List[float]
    events: List[int]
    label: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "PreparedSession":
        try:
            uuid = data['uuid']
            text = data['text']
            tweet_length = data['tweet_length']
            audio_db = data['audio_db']
            events = data['events']
            label = data['label']
        except KeyError as e:
            raise KeyError(f"Missing key in input dictionary: {e}")
            
        return PreparedSession(uuid, text, tweet_length, audio_db, events, label)    
