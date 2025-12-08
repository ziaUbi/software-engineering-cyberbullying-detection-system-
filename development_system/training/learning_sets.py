import json
from typing import List

import joblib
import pandas as pd

from development_system.prepared_session import PreparedSession

class LearningSets:
    """
    Static class representing the three sets using for development: training, validation, and testing.
    Sets are represented as lists of PreparedSession objects. 
    Each set is stored in a separate .sav file using joblib.
    
    Methods
    --------
        extract_features_and_labels(data_set): Extracts features and labels from a given dataset.
        from_json(json_file_path): Creates a LearningSet object from a JSON file.
        from_dict(dict): Creates a LearningSet object from a dictionary.
        save_learning_set(learning_set): Saves the learning set to .sav files using joblib
    """
    def __new__(cls, *args, **kwargs):
        if cls is LearningSets:
            raise TypeError(f"'{cls.__name__}' cannot be instantiated")
        return object.__new__(cls, *args, **kwargs)


    @staticmethod
    def save_learning_sets(learning_sets):
        """
        Saves the training, validation, and test sets of a LearningSet instance to .sav files using joblib.

        Args:
            learning_set (LearningSet): An instance containing training, validation, and test sets.

        Returns:
            None
        """
        # Converts data using the to_dictionary method
        training_data = [session.to_dictionary() for session in learning_sets.training_set]
        validation_data = [session.to_dictionary() for session in learning_sets.validation_set]
        test_data = [session.to_dictionary() for session in learning_sets.test_set]

        # Save data in the respective file .sav using joblib
        joblib.dump(training_data, 'data/training_set.sav')
        joblib.dump(validation_data, 'data/validation_set.sav')
        joblib.dump(test_data, 'data/test_set.sav')


    @staticmethod
    def get_training_set():
        """Loads and returns the training set from the .sav file."""
        training_data = joblib.load('data/training_set.sav')
        return training_data
    

    @staticmethod
    def get_validation_set():
        """Loads and returns the validation set from the .sav file."""
        validation_data = joblib.load('data/validation_set.sav')
        return validation_data
    

    @staticmethod
    def get_test_set():
        """Loads and returns the test set from the .sav file."""
        test_data = joblib.load('data/test_set.sav')
        return test_data
    

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


    @classmethod
    def from_dict(cls, data: dict) -> 'LearningSets':
        """
        Creates a LearningSet object from a dictionary.

        :params: data (dict): A dictionary containing the learning set data
        :returns LearningSet: A new instance of LearningSet.
        Raises:
            ValueError: If data is not a dictionary.
        """
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary.")

        return cls(
            training_set=[PreparedSession.from_dictionary(session) for session in data["training_set"]],
            validation_set=[PreparedSession.from_dictionary(session) for session in data["validation_set"]],
            test_set=[PreparedSession.from_dictionary(session) for session in data["test_set"]],
        )
    

    @staticmethod
    def from_json(json_file_path: str):
        """
        Creates a LearningSet object from a JSON file.

        :param: json_file_path (str): Path to the JSON file containing the learning set data
        :returns LearningSet: A new instance of LearningSet.

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
        return LearningSets(training_set=training_set, validation_set=validation_set, test_set=test_set)