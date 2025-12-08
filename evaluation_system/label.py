"""
Author: Rossana Antonella Sacco
"""

class Label:
    """
    Data Object representing a label used in the evaluation system.
    """
    
    # Usa il nome della tua classe Enum come tipo
    def __init__(self, uuid: str, cyberbullying: str, expert: bool):
        """
        Initializes a Label object.
        :param uuid: Unique identifier for the label.
        :param cyberbullying: String indicating the status.
        :param expert: Boolean indicating if the label was assigned by an expert.
        """
        self.uuid = uuid
        self.cyberbullying = cyberbullying
        self.expert = expert
        
    @property
    def uuid(self) -> str:
        return self.uuid
    
    @uuid.setter
    def uuid(self, value: str):
        self.uuid = value
        
    @property
    def cyberbullying(self) -> str:
        return self.cyberbullying
    
    @cyberbullying.setter
    def cyberbullying(self, value: str):
        self.cyberbullying = value
        
    @property
    def expert(self) -> bool:
        return self.expert
    
    @expert.setter
    def expert(self, value: bool):
        self.expert = value
    
    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "cyberbullying": self.cyberbullying, 
            "expert": self.expert
        }