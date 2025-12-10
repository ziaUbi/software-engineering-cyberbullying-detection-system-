from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class CoverageReportData:
    total_sessions: int
    tweet_length_list: List[int]  
    audio_db_list: List[int]    
    badWords: List[int]
    events_list: List[int]
    coverage_satisfied: bool