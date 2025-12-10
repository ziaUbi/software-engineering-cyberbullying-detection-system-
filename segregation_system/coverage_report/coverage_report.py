from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class CoverageReportData:
    total_sessions: int
    tweet_length_stats: Dict[str, Any] # min, max, avg
    audio_db_stats: Dict[str, Any]     # min, max, avg
    issues: List[str]
    coverage_satisfied: bool