import numpy as np
from sklearn.neural_network import MLPClassifier

class Classifier(MLPClassifier):
    """Class representing a classifier."""

    def __init__(self):
        """Initialize classifier attributes."""
        super(Classifier, self).__init__()
        self.num_layers = 0
        self.num_neurons = 0
        self.training_error = 0.0
        self.validation_error = 0.0
        self.test_error = 0.0


    def get_train_valid_error_difference(self):
        """Computes the difference between the validation error and training error over the validation error"""
        if self.get_validation_error() == 0:
            return 1
        return (self.get_validation_error() - self.get_training_error()) / self.get_validation_error()


    def get_valid_test_error_difference(self):
        """Computes the difference between the test error and validation error over the test error"""
        if self.get_test_error() == 0:
            return 1
        return (self.get_test_error() - self.get_validation_error()) / self.get_test_error()


    def classifier_report(self):
        """Defines the report of the classifier."""
        return {'num_iterations': self.get_num_iterations(),
                'validation_error': self.get_validation_error(),
                'training_error': self.get_training_error(),
                'difference': self.get_train_valid_error_difference(),
                'num_layers': self.get_num_layers(),
                'num_neurons': self.get_num_neurons(),
                'network_complexity': self.get_num_layers() * self.get_num_neurons()
                }
    

    def fit(self, x, y):
        """
           Configures the hidden layer sizes and trains the model.

           Args:
               x: Features for training.
               y: Target values for training.

           Returns:
               None
        """
        self.hidden_layer_sizes = np.full((self.num_layers,), self.num_neurons, dtype=int)
        super().fit(x, y)


    def get_loss_curve(self):
        """Get the MSE vector.
        Returns: the loss_curve
        """
        return self.loss_curve_
    
    # ========================= Getters and Setters =========================

    def set_num_iterations(self, num_iterations: int):
        self.max_iter = num_iterations # max_iter is the attribute of the parent class MLPClassifier

    def get_num_iterations(self):
        return self.max_iter

    def set_num_layers(self, value):
        self.num_layers = value

    def get_num_layers(self):
        return self.num_layers

    def set_num_neurons(self, value):
        self.num_neurons = value

    def get_num_neurons(self):
        return self.num_neurons

    def set_training_error(self, training_error = 0):
        if training_error == 0:
            self.training_error = self.loss_ # loss_ is the attribute of the parent class MLPClassifier
        else:
            self.training_error = training_error

    def get_training_error(self):
        return self.loss_ 

    def set_validation_error(self, value):
        self.validation_error = value

    def get_validation_error(self):
        return self.validation_error

    def set_test_error(self, value):
        self.test_error = value

    def get_test_error(self):
        return self.test_error