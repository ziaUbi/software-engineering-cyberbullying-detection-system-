import copy
import itertools
import os
import random

import joblib

from development_system.configuration_parameters import ConfigurationParameters
from development_system.training.trainer import Trainer
from development_system.validation.validation_report_model import ValidationReportModel
from development_system.validation.validation_report_view import ValidationReportView


class ValidationOrchestrator:
    """Orchestrator of the validation"""

    def __init__(self, basedir):
        """Initialize the orchestrator."""
        self.basedir = basedir
        self.service_flag = ConfigurationParameters.params['service_flag']
        self.validation_report_model = ValidationReportModel()

    def validation(self):
        """
            Perform a grid search for hyperparameters and generate the validation report.
        """
        classifier_trainer = Trainer(basedir=self.basedir)
        # if service flag is true, load the classifier with average hyperparameters
        if self.service_flag:
            classifier = joblib.load(os.path.join(self.basedir, "data", "classifier_avg_hyperparams.sav"))
            iterations = classifier.get_num_iterations()
        # else reads the iterations from the json
        else:
            iterations = classifier_trainer.read_number_iterations()

        # Build grid search for hyperparameters
        layers = []
        for i in range(ConfigurationParameters.params['min_layers'], ConfigurationParameters.params['max_layers'] + 1,
                       ConfigurationParameters.params['step_layers']):
            layers.append(i)

        neurons = []
        for i in range(ConfigurationParameters.params['min_neurons'], ConfigurationParameters.params['max_neurons'] + 1,
                       ConfigurationParameters.params['step_neurons']):
            neurons.append(i)

        grid_search = list(itertools.product(layers, neurons))

        # Perform grid search
        for (num_layers, num_neurons) in grid_search:
            classifier_trainer.set_hyperparameters(num_layers, num_neurons)
            classifier_trainer.train(iterations)
            classifier = classifier_trainer.validate()
            self.validation_report_model.append_classifier(classifier)

        # Generate validation report
        model = self.validation_report_model.get_model()
        ValidationReportView.show_validation_report(model)
        print("Validation report generated")

        # In service mode, randomize the validation outcome
        if self.service_flag:
            index = int(random.random() <= 0.95)
            if index == 0:  # 5%
                return False
            else:
                return True
