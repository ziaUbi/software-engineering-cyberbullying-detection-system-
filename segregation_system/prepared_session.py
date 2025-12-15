from dataclasses import dataclass, asdict
from typing import List, Tuple

@dataclass
class PreparedSession:
    def __init__(self, data: dict):
        self.uuid = data['uuid']
        self.label = data['label']
        self.tweet_length = data['tweet_length']

        self.word_fuck = data['word_fuck']
        self.word_bulli = data['word_bulli']
        self.word_muslim = data['word_muslim']
        self.word_gay = data['word_gay']
        self.word_nigger = data['word_nigger']
        self.word_rape = data['word_rape']

        self.event_score = data['event_score']
        if 'event_sending-off' in data.keys():
            self.event_sending_off = data['event_sending-off']
        elif 'event_sending_off' in data.keys():
            self.event_sending_off = data['event_sending_off']
        self.event_caution = data['event_caution']
        self.event_substitution = data['event_substitution']
        self.event_foul = data['event_foul']

        self.audio_0 = data['audio_0']
        self.audio_1 = data['audio_1']
        self.audio_2 = data['audio_2']
        self.audio_3 = data['audio_3']
        self.audio_4 = data['audio_4']
        self.audio_5 = data['audio_5']
        self.audio_6 = data['audio_6']
        self.audio_7 = data['audio_7']
        self.audio_8 = data['audio_8']
        self.audio_9 = data['audio_9']
        self.audio_10 = data['audio_10']
        self.audio_11 = data['audio_11']
        self.audio_12 = data['audio_12']
        self.audio_13 = data['audio_13']
        self.audio_14 = data['audio_14']
        self.audio_15 = data['audio_15']
        self.audio_16 = data['audio_16']
        self.audio_17 = data['audio_17']
        self.audio_18 = data['audio_18']
        self.audio_19 = data['audio_19']

    def to_dict(self):
        return asdict(self)
