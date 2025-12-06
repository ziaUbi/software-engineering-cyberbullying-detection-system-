import json
from typing import List

import joblib
import pandas as pd

from development_system.prepared_session import PreparedSession

class LearningSet:
    """
    Represents a collection of datasets used in machine learning, including
    training, validation, and test sets.

    Attributes:
        training_set (List[PreparedSession]): A list of `PreparedSession` objects used for training.
        validation_set (List[PreparedSession]): A list of `PreparedSession` objects used for validation.
        test_set (List[PreparedSession]): A list of `PreparedSession` objects used for testing.

    """

    def __init__(self, training_set: List[PreparedSession], validation_set: List[PreparedSession], test_set: List[PreparedSession]):
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



    @staticmethod
    def extract_features_and_labels(data_set):
        """
        Extracts features and labels from a set of data.

        Args:
            data_set (dict): A dictionary which contains a set of data (ex. "test_set").


        Returns:
            list: A list containing two elements:
                  - features (pd.DataFrame): A DataFrame with the characteristics.
                  - labels (pd.Series): Series with the labels.
        """

        activity_mapping = {"shopping": 0, "sport": 1, "cooking": 2, "relax": 3, "gaming": 4}

        environment_mapping = {"slippery": 0, "plain": 1, "slope": 2, "house": 3, "track": 4}

        label_mapping = {"turnRight": 0, "turnLeft": 1, "move": 2}


        current_data = pd.DataFrame([
            {
                "psd_alpha_band": record["psd_alpha_band"],
                "psd_beta_band": record["psd_beta_band"],
                "psd_theta_band": record["psd_theta_band"],
                "psd_delta_band": record["psd_delta_band"],
                "activity": activity_mapping.get(record["activity"]),
                "environment": environment_mapping.get(record["environment"]),
                "label": record["label"]
            }
            for record in data_set
        ])

        # Separation of the features and labels
        features = current_data.drop(columns=["label"])
        true_labels = current_data["label"]

        # converts string labels in integers using map
        true_labels = true_labels.map(label_mapping)

        labels = []
        num_classes = len(label_mapping)  # number of classes

        for label in true_labels:
            new_labels = [0] * num_classes  # create an array of zeros with number of class length
            new_labels[label] = 1  # set to 1 the correspondent index of the class
            labels.append(new_labels)

        return [features, labels]

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

    @staticmethod
    def create_learning_set_from_json(json_file_path: str):
        """
        Creates a LearningSet object by loading data from a JSON file.

        Args:
            json_file_path (str): Path to the JSON file containing the learning set data.

        Returns:
            LearningSet: An object containing the training, validation, and test sets.

        Raises:
            FileNotFoundError: If the specified JSON file is not found.
            ValueError: If the JSON file cannot be decoded properly.
        """
        try:
            # Load data from the JSON file
            with open(json_file_path, 'r') as file:
                current_data = json.load(file)
        except FileNotFoundError as ex:
            raise FileNotFoundError(f"File not found: {ex}")
        except json.JSONDecodeError as ex:
            raise ValueError(f"Error decoding JSON: {ex}")

        # Convert each set in the JSON into a list of PreparedSession objects
        training_set = [PreparedSession.from_dictionary(session) for session in current_data.get('training_set', [])]
        validation_set = [PreparedSession.from_dictionary(session) for session in
                          current_data.get('validation_set', [])]
        test_set = [PreparedSession.from_dictionary(session) for session in current_data.get('test_set', [])]

        # Create and return the LearningSet object
        return LearningSet(training_set=training_set, validation_set=validation_set, test_set=test_set)


    @staticmethod
    def save_learning_set(learning_set):
        """
        Saves the training, validation, and test sets of a LearningSet instance to .sav files using joblib.

        Args:
            learning_set (LearningSet): An instance containing training, validation, and test sets.

        Returns:
            None
        """
        # Converts data using the to_dictionary method
        training_data = [session.to_dictionary() for session in learning_set.training_set]
        validation_data = [session.to_dictionary() for session in learning_set.validation_set]
        test_data = [session.to_dictionary() for session in learning_set.test_set]

        # Save data in the respective file .sav using joblib
        joblib.dump(training_data, 'data/training_set.sav')
        joblib.dump(validation_data, 'data/validation_set.sav')
        joblib.dump(test_data, 'data/test_set.sav')

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