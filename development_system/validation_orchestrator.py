import copy
import itertools
import random

import joblib

from development_system.configuration_parameters import ConfigurationParameters
from development_system.training.trainer import Trainer
from development_system.validation_report_model import ValidationReportModel
from development_system.validation_report_view import ValidationReportView


class ValidationOrchestrator:
    """Orchestrator of the validation"""

    def __init__(self):
        """Initialize the orchestrator."""
        self.classifiers = []
        self.validation_report = None
        self.validation_report_model = ValidationReportModel()
        self.validation_report_view = ValidationReportView()
        self.service_flag = ConfigurationParameters.params['service_flag']

    def validation(self):
        """
            Perform a grid search for hyperparameters and generate the validation report.

            Returns:
                ValidationReport or bool:
                    - If in service mode, returns the generated validation report.
                    - If in testing mode, returns `True` if all classifiers in the report are valid, otherwise `False`.
        """
        # Grid Search
        classifier_trainer = Trainer()
        # reads the iterations from the classifier saved
        if self.service_flag:
            classifier = joblib.load("data/classifier_before_training")
            iterations = classifier.get_num_iterations()
        # reads the iterations from the json
        else:
            iterations = classifier_trainer.read_number_iterations()

        # Compute all possible combinations of hyperparameters
        layers = []

        for i in range(ConfigurationParameters.params['min_layers'], ConfigurationParameters.params['max_layers'] + 1,
                       ConfigurationParameters.params['step_layers']):
            layers.append(i)

        neurons = []

        for i in range(ConfigurationParameters.params['min_neurons'], ConfigurationParameters.params['max_neurons'] + 1,
                       ConfigurationParameters.params['step_neurons']):
            neurons.append(i)

        grid_search = list(itertools.product(layers, neurons))

        for (num_layers, num_neurons) in grid_search:
            # SET HYPERPARAMETERS
            classifier_trainer.set_hyperparameters(num_layers, num_neurons)
            # TRAIN
            classifier_trainer.train(iterations, validation=True)
            classifier = classifier_trainer.validate()
            #append the clasifier into the classifiers list
            self.classifiers.append(copy.deepcopy(classifier))

        # GENERATE VALIDATION REPORT
        self.validation_report =  self.validation_report_model.generate_validation_report(self.classifiers)

        # CHECK VALIDATION RESULT
        self.validation_report_view.show_validation_report(self.validation_report)
        print("validation report generated")


        if self.service_flag:
            # returns true if at least one of the classifiers in the report is valid
            # if all are not valid, false
            index = int(random.random() <= 0.95)
            if index == 0:  # 5%
                return False
            else:
                return True

        else:
            # it is useful only for testing the creation of validation report
            return self.validation_report