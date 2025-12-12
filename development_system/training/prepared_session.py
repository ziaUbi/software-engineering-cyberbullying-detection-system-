from dataclasses import dataclass, asdict
from typing import List, Tuple

@dataclass
class PreparedSession:
    uuid: str
    label: str
    tweet_length: int

    word_fuck: int
    word_bulli: int
    word_muslim: int
    word_gay: int
    word_nigger: int
    word_rape: int

    event_score: int
    event_sending_off: int
    event_caution: int
    event_substitution: int
    event_foul: List[float]
    event_unknown: List[int]

    audio_0: float
    audio_1: float
    audio_2: float
    audio_3: float
    audio_4: float
    audio_5: float
    audio_6: float
    audio_7: float
    audio_8: float
    audio_9: float
    audio_10: float
    audio_11: float
    audio_12: float
    audio_13: float
    audio_14: float
    audio_15: float
    audio_16: float
    audio_17: float
    audio_18: float
    audio_19: float

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dictionary(data: dict) -> "PreparedSession":
        try:
            uuid = data['uuid']
            label = data['label']
            tweet_length = data['tweet_length']

            word_fuck = data['word_fuck']
            word_bulli = data['word_bulli']
            word_muslim = data['word_muslim']
            word_gay = data['word_gay']
            word_nigger = data['word_nigger']
            word_rape = data['word_rape']

            event_score = data['event_score']
            event_sending_off = data['event_sending-off']
            event_caution = data['event_caution']
            event_substitution = data['event_substitution']
            event_foul = data['event_foul']
            event_unknown = data['event_unknown']

            audio_0 = data['audio_0']
            audio_1 = data['audio_1']
            audio_2 = data['audio_2']
            audio_3 = data['audio_3']
            audio_4 = data['audio_4']
            audio_5 = data['audio_5']
            audio_6 = data['audio_6']
            audio_7 = data['audio_7']
            audio_8 = data['audio_8']
            audio_9 = data['audio_9']
            audio_10 = data['audio_10']
            audio_11 = data['audio_11']
            audio_12 = data['audio_12']
            audio_13 = data['audio_13']
            audio_14 = data['audio_14']
            audio_15 = data['audio_15']
            audio_16 = data['audio_16']
            audio_17 = data['audio_17']
            audio_18 = data['audio_18']
            audio_19 = data['audio_19']
        except KeyError as e:
            raise KeyError(f"Missing key in input dictionary: {e}")
            
        return PreparedSession(uuid, label, tweet_length, word_fuck, word_bulli, word_muslim, word_gay, word_nigger, word_rape, event_score, event_sending_off, event_caution, event_substitution, event_foul, event_unknown, audio_0, audio_1, audio_2, audio_3, audio_4, audio_5, audio_6, audio_7, audio_8, audio_9, audio_10, audio_11, audio_12, audio_13, audio_14, audio_15, audio_16, audio_17, audio_18, audio_19)
