"""Domain representation of a cyberbullying moderation decision.

Labels use the values "not cyberbullying" and "cyberbullying".
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Dict, Optional


@dataclass
class Label:
    """Describe the moderation outcome restricted to the allowed enum values.
    """

    uuid: str
    label: Optional[str]  # Enum: "not cyberbullying" or "cyberbullying"

    def to_dictionary(self) -> Dict[str, Optional[str]]:
        """Convert the label to a dictionary."""
        return asdict(self)

    def to_json_string(self) -> str:
        """Explicitly serialize the object to a JSON string."""
        return json.dumps(self.to_dictionary())