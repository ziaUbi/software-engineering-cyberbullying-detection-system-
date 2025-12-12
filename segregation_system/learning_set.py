from typing import List
from segregation_system.prepared_session import PreparedSession

class LearningSet:
    def __init__(self,
                 training_set: List[PreparedSession],
                 validation_set: List[PreparedSession],
                 test_set: List[PreparedSession]):

        self._training_set = training_set
        self._validation_set = validation_set
        self._test_set = test_set

    @property
    def training_set(self) -> List[PreparedSession]:
        return self._training_set

    @training_set.setter
    def training_set(self, value: List[PreparedSession]):
        if not isinstance(value, list) or not all(isinstance(item, PreparedSession) for item in value):
            raise ValueError("training_set must be a list of PreparedSession objects.")
        self._training_set = value

    @property
    def validation_set(self) -> List[PreparedSession]:
        return self._validation_set

    @validation_set.setter
    def validation_set(self, value: List[PreparedSession]):
        if not isinstance(value, list) or not all(isinstance(item, PreparedSession) for item in value):
            raise ValueError("validation_set must be a list of PreparedSession objects.")
        self._validation_set = value

    @property
    def test_set(self) -> List[PreparedSession]:
        return self._test_set

    @test_set.setter
    def test_set(self, value: List[PreparedSession]):
        if not isinstance(value, list) or not all(isinstance(item, PreparedSession) for item in value):
            raise ValueError("test_set must be a list of PreparedSession objects.")
        self._test_set = value

    def to_dict(self) -> dict:
        return {
            "training_set": [session for session in self._training_set],
            "validation_set": [session for session in self._validation_set],
            "test_set": [session for session in self._test_set],
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LearningSet':
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary.")

        return cls(
            training_set=[PreparedSession(session) for session in data["training_set"]],
            validation_set=[PreparedSession(session) for session in data["validation_set"]],
            test_set=[PreparedSession(session) for session in data["test_set"]],
        )