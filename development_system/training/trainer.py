import math
import joblib

from sklearn.metrics import log_loss

from development_system.configuration_parameters import ConfigurationParameters
from development_system.json_handler_validator import JsonHandlerValidator
from learning_sets import LearningSets
from classifier import Classifier

class Trainer:
    """Class responsible for training a classifier."""
    def __init__(self):
        """Initialize trainer parameters."""
        self.classifier = Classifier()

    
    def save_classifier(self, path: str):
        """
            Save the classifier to a .sav file.

            Args:
                path (str): The path where to save the classifier.
        """
        joblib.dump(self.classifier, path)


    def load_classifier(self, path: str):
        """
            Load the classifier from a .sav file.

            Args:
                path (str): The path from where to load the classifier.
        """
        self.classifier = joblib.load(path)


    def read_number_iterations(self):
        """
            Read the number of iterations from the json file.

            Returns:
                int: The number of iterations.
        """
        JsonHandlerValidator.validate_json("intermediate_results/iterations.json", "schemas/iterations_schema.json")
        data = JsonHandlerValidator.read_json_file("intermediate_results/iterations.json")
        return data["iterations"]


    def set_avg_hyperparameters(self):
        """Set the average hyperparameters (neurons and layers) to the classifier.
        Save the configured classifier to a .sav file."""

        avg_neurons = math.ceil((ConfigurationParameters.params['max_neurons'] + ConfigurationParameters.params['min_neurons']) / 2)
        avg_layers = math.ceil((ConfigurationParameters.params['max_layers'] + ConfigurationParameters.params['min_layers']) / 2)

        self.classifier.set_num_neurons(avg_neurons)
        self.classifier.set_num_layers(avg_layers)


    def set_hyperparameters(self, num_layers: int, num_neurons: int):
        """ Set the hyperparameters.
             Args:
                num_layers (int): The number of layers to set
                num_neurons (int): The number of neurons to set
        """
        self.classifier.set_num_neurons(num_neurons)
        self.classifier.set_num_layers(num_layers)


    def train(self, iterations, validation: bool = False):
        """
            Train the classifier.
            Args:
                iterations (int): The number of iterations for training.
                validation (bool, optional): Whether to perform validation after training. Defaults to False.

            Returns:
                object: The trained classifier.
        """
        # extract the training set and the features and labels
        training_set = LearningSets.get_training_set()
        result = LearningSets.extract_features_and_labels(training_set)

        training_features = result[0]
        training_labels = result[1]

        self.classifier.set_num_iterations(iterations)
        # Train the classifier
        self.classifier.fit(x=training_features, y=training_labels)

        return self.classifier

    def validate(self):
        """
            Validate the classifier.

            This function loads validation data, extracts features and labels,
            and computes the validation error using log loss. The validation error
            is then set for the classifier.
        """
        # extract the validation set and the features and labels
        validation_set = LearningSets.get_validation_set()
        result = LearningSets.extract_features_and_labels(validation_set)

        validation_features = result[0]
        validation_labels = result[1]

        validation_error = log_loss(y_true=validation_labels,
                                    y_pred=self.classifier.predict_proba(validation_features))

        self.classifier.set_validation_error(validation_error)
        return self.classifier