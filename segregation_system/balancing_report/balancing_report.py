from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class BalancingReportData:
    total_sessions: int
    class_distribution: Dict[str, int] 
    class_percentages: Dict[str, float] 
    is_minimum: bool
    is_balanced: bool