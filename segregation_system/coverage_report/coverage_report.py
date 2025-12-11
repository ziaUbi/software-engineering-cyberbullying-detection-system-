from typing import Dict
from dataclasses import dataclass

@dataclass
class CoverageReportData:
    total_sessions: int
    tweet_length_map: Dict[int, int]
    audio_db_map: Dict[int, int]
    bad_words_map: Dict[str, int]
    events_map: Dict[str, int]

