import json
from typing import List
import os
import joblib
import pandas as pd

class LearningSets:
    """
    Class representing the three sets using for development: training, validation, and testing.
    Sets are represented as lists of PreparedSession objects. 
    Each set is stored in a separate .sav file using joblib.
    
    Methods
    --------
        extract_features_and_labels(data_set): Extracts features and labels from a given dataset.
        from_json(json_file_path): Creates a LearningSet object from a JSON file.
        from_dict(dict): Creates a LearningSet object from a dictionary.
        save_learning_set(learning_set): Saves the learning set to .sav files using joblib
    """
    basedir = os.path.join(os.getcwd(), 'development_system')
    def __init__(self,
                 training_set: List[dict],
                 validation_set: List[dict],
                 test_set: List[dict]):

        self.training_set = training_set
        self.validation_set = validation_set
        self.test_set = test_set


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
        training_data = [session for session in learning_sets.training_set]
        validation_data = [session for session in learning_sets.validation_set]
        test_data = [session for session in learning_sets.test_set]

        # Save data in the respective file .sav using joblib
        if not os.path.exists(os.path.join(LearningSets.basedir, 'data')):
            os.makedirs(os.path.join(LearningSets.basedir, 'data'))

        joblib.dump(training_data, os.path.join(LearningSets.basedir, 'data', 'training_set.sav'))
        joblib.dump(validation_data, os.path.join(LearningSets.basedir, 'data', 'validation_set.sav'))
        joblib.dump(test_data, os.path.join(LearningSets.basedir, 'data', 'test_set.sav'))


    @staticmethod
    def get_training_set():
        """Loads and returns the training set from the .sav file."""
        training_data = joblib.load(os.path.join(LearningSets.basedir, 'data', 'training_set.sav'))
        return training_data
    

    @staticmethod
    def get_validation_set():
        """Loads and returns the validation set from the .sav file."""
        validation_data = joblib.load(os.path.join(LearningSets.basedir, 'data', 'validation_set.sav'))
        return validation_data
    

    @staticmethod
    def get_test_set():
        """Loads and returns the test set from the .sav file."""
        test_data = joblib.load(os.path.join(LearningSets.basedir, 'data', 'test_set.sav'))
        return test_data
    

    @staticmethod
    def extract_features_and_labels(dataset):
        """
        Extracts features and labels from a set of data.

        Args:
            dataset (list): A list of dictionaries representing the dataset.

        Returns:
            list: A list containing two elements:
                  - features (pd.DataFrame): A DataFrame with the characteristics.
                  - labels (pd.Series): Series with the labels.
        """
        df = pd.DataFrame(dataset)
        # converts string labels in integers using map
        df["label"] = df["label"].map({
            "cyberbullying": 1,
            "not_cyberbullying": 0
        })
        return df.drop(columns=["label", "uuid"]), df["label"]
        

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

        print(data["training_set"])
        return cls(
            training_set=data["training_set"],
            validation_set=data["validation_set"],
            test_set=data["test_set"],
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

        """ # Convert each set in the JSON into a list of PreparedSession objects
        training_set = [PreparedSession.from_dictionary(session) for session in current_data.get('training_set', [])]
        validation_set = [PreparedSession.from_dictionary(session) for session in
                          current_data.get('validation_set', [])]
        test_set = [PreparedSession.from_dictionary(session) for session in current_data.get('test_set', [])]

        # Create and return the LearningSet object
        return LearningSets(training_set=training_set, validation_set=validation_set, test_set=test_set) """