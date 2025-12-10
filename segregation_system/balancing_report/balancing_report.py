from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class BalancingReportData:
    total_sessions: int
    class_distribution: Dict[str, int]  # Es: {"Cyberbullying": 30, "Safe": 70}
    class_percentages: Dict[str, float] # Es: {"Cyberbullying": 0.3, "Safe": 0.7}
    is_minimum: bool
    is_balanced: bool