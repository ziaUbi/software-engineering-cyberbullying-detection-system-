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
        self.uuid = uuid
        self.label = label  
        self.expert = expert
        
    @property
    def uuid(self) -> str:
        return self.uuid
    
    @uuid.setter
    def uuid(self, value: str):
        self.uuid = value
        
    @property
    def label(self) -> str:
        return self.label
    
    @label.setter
    def label(self, value: str):
        self.label = value
        
    @property
    def expert(self) -> bool:
        return self.expert
    
    @expert.setter
    def expert(self, value: bool):
        self.expert = value
    
    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "label": self.label, 
            "expert": self.expert
        }