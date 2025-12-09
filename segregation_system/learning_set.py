from typing import List
from segregation_system.prepared_session import PreparedSession

class LearningSet:
    """
    Represents a collection of datasets used in machine learning, including
    training, validation, and test sets.

    Attributes:
        training_set (List[PreparedSession]): A list of `PreparedSession` objects used for training.
        validation_set (List[PreparedSession]): A list of `PreparedSession` objects used for validation.
        test_set (List[PreparedSession]): A list of `PreparedSession` objects used for testing.
    """

    def __init__(self,
                 training_set: List[PreparedSession],
                 validation_set: List[PreparedSession],
                 test_set: List[PreparedSession]):
        """
        Initializes a new instance of the `LearningSet` class.

        Args:
            training_set (List[PreparedSession]): Training dataset as a list of `PreparedSession` objects.
            validation_set (List[PreparedSession]): Validation dataset as a list of `PreparedSession` objects.
            test_set (List[PreparedSession]): Test dataset as a list of `PreparedSession` objects.
        """
        self._training_set = training_set
        self._validation_set = validation_set
        self._test_set = test_set

    @property
    def training_set(self) -> List[PreparedSession]:
        """
        Gets the training dataset.

        Returns:
            List[PreparedSession]: The training dataset.
        """
        return self._training_set

    @training_set.setter
    def training_set(self, value: List[PreparedSession]):
        """
        Sets the training dataset.

        Args:
            value (List[PreparedSession]): A new list of `PreparedSession` objects for training.

        Raises:
            ValueError: If the input is not a list of `PreparedSession` objects.
        """
        if not isinstance(value, list) or not all(isinstance(item, PreparedSession) for item in value):
            raise ValueError("training_set must be a list of PreparedSession objects.")
        self._training_set = value

    @property
    def validation_set(self) -> List[PreparedSession]:
        """
        Gets the validation dataset.

        Returns:
            List[PreparedSession]: The validation dataset.
        """
        return self._validation_set

    @validation_set.setter
    def validation_set(self, value: List[PreparedSession]):
        """
        Sets the validation dataset.

        Args:
            value (List[PreparedSession]): A new list of `PreparedSession` objects for validation.

        Raises:
            ValueError: If the input is not a list of `PreparedSession` objects.
        """
        if not isinstance(value, list) or not all(isinstance(item, PreparedSession) for item in value):
            raise ValueError("validation_set must be a list of PreparedSession objects.")
        self._validation_set = value

    @property
    def test_set(self) -> List[PreparedSession]:
        """
        Gets the test dataset.

        Returns:
            List[PreparedSession]: The test dataset.
        """
        return self._test_set

    @test_set.setter
    def test_set(self, value: List[PreparedSession]):
        """
        Sets the test dataset.

        Args:
            value (List[PreparedSession]): A new list of `PreparedSession` objects for testing.

        Raises:
            ValueError: If the input is not a list of `PreparedSession` objects.
        """
        if not isinstance(value, list) or not all(isinstance(item, PreparedSession) for item in value):
            raise ValueError("test_set must be a list of PreparedSession objects.")
        self._test_set = value

    def to_dict(self) -> dict:
        """
        Converts the LearningSet instance into a dictionary.

        Returns:
            dict: A dictionary representation of the LearningSet.
        """
        return {
            "training_set": [session.to_dictionary() for session in self._training_set],
            "validation_set": [session.to_dictionary() for session in self._validation_set],
            "test_set": [session.to_dictionary() for session in self._test_set],
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LearningSet':
        """
        Creates a LearningSet instance from a dictionary.

        Args:
            data (dict): A dictionary containing the learning set data.

        Returns:
            LearningSet: A new instance of LearningSet.
        """
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary.")

        return cls(
            training_set=[PreparedSession.from_dictionary(session) for session in data["training_set"]],
            validation_set=[PreparedSession.from_dictionary(session) for session in data["validation_set"]],
            test_set=[PreparedSession.from_dictionary(session) for session in data["test_set"]],
        )