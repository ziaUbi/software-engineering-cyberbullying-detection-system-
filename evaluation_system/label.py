"""
Author: Rossana Antonella Sacco
"""

class Label:
    """
    Data Object representing a label used in the evaluation system.
    """
    
    # Usa il nome della tua classe Enum come tipo
    def __init__(self, uuid: str, label: str, expert: bool):
        """
        Initializes a Label object.
        :param uuid: Unique identifier for the label.
        :param label: String indicating the status.
        :param expert: Boolean indicating if the label was assigned by an expert.
        """
        self._uuid = uuid
        self._label = label  
        self._expert = expert
        
    @property
    def uuid(self) -> str:
        return self._uuid
    
    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value
        
    @property
    def label(self) -> str:
        return self._label
    
    @label.setter
    def label(self, value: str):
        self._label = value
        
    @property
    def expert(self) -> bool:
        return self._expert
    
    @expert.setter
    def expert(self, value: bool):
        self._expert = value
    
    def to_dict(self) -> dict:
        return {
            "uuid": self._uuid,
            "label": self._label, 
            "expert": self._expert
        }