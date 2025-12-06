import math
import random

import joblib

from development_system.classifier import Classifier
from development_system.configuration_parameters import ConfigurationParameters
from development_system.json_handler_validator import JsonHandlerValidator
from development_system.learning_plot_controller import LearninPlotController
from development_system.trainer import Trainer


class TrainingOrchestrator:
    """Orchestrator of the training"""

    def __init__(self):
        """Initialize the orchestrator."""
        self.trainer = Trainer()
        self.classifier = Classifier()
        #self.plot_model = LearningPlotModel()
        #self.plot_view = LearningPlotView()
        self.plot_controller = LearningPlotController()
        self.service_flag = None
        self.json_handler = JsonHandlerValidator()

    def train_classifier(self, set_average_hyperparams):
        """
            Train the classifier with specified or dynamically determined hyperparameters.
            Args:
                set_average_hyperparams (bool):
                    If True, sets average hyperparameters (neurons and layers)
                    and saves the configured classifier. If False, adjusts the number of iterations dynamically.
        """
        if set_average_hyperparams:
            self.trainer.set_average_hyperparameters()
            # both for the test and the service phase, we save the classifier with the layers and neurons setted
            self.classifier.set_num_neurons(self.trainer.classifier.get_num_neurons())
            self.classifier.set_num_layers(self.trainer.classifier.get_num_layers())
            joblib.dump(self.classifier, "data/classifier_trainer.sav")

        else:

            self.service_flag = ConfigurationParameters.params['service_flag']
            #if testing is true, the iterations are read from the file, otherwise are randomly generated
            if self.service_flag:
                iterations = random.randint(50, 150)

                while True:

                    classifier = self.trainer.train(iterations)
                    # GENERATE LEARNING REPORT
                    learning_error = self.plot_model.generate_learning_report(classifier)
                    # CHECK LEARNING PLOT
                    self.plot_view.show_learning_plot(learning_error)

                    choice = random.randint(0, 4)
                    if choice == 0:  # 20%
                        print("CHECK LEARNING PLOT OK)")
                        # if # iterations is correct save the new classifier
                        self.classifier.set_num_iterations(iterations)
                        joblib.dump(self.classifier, "data/classifier_trainer.sav")
                        break
                    if choice <= 2:  # 40%
                        print("CHECK LEARNING PLOT INCREASE 1/3")
                        iterations = math.ceil(iterations * (1 + 1 / 3))
                    else:  # 40%
                        print("CHECK LEARNING PLOT decrease 1/3")
                        iterations = math.ceil(iterations * (1 - 1 / 3))
            else:
                iterations = self.trainer.read_number_iterations()
                classifier = self.trainer.train(iterations)
                # GENERATE LEARNING REPORT
                learning_error = self.plot_model.generate_learning_report(classifier)
                # CHECK LEARNING PLOT
                self.plot_view.show_learning_plot(learning_error)

            print("number of iterations= ", iterations)
            print("learning report generated")
            print("learning error =", learning_error.get_learning_error())