import math
import random

import joblib

from development_system.configuration_parameters import ConfigurationParameters
from development_system.json_handler_validator import JsonHandlerValidator
from development_system.training.learning_plot_model import LearningPlotModel
from development_system.training.learning_plot_view import LearningPlotView
from development_system.training.trainer import Trainer


class TrainingOrchestrator:
    """Orchestrator of the training"""

    def __init__(self):
        """Initialize the orchestrator."""
        self.trainer = Trainer()
        self.service_flag = ConfigurationParameters.params['service_flag']

    def train_classifier(self, set_avg_hyperparams):
        """
            Train the classifier with specified or dynamically determined hyperparameters.
            Args:
                set_avg_hyperparams (bool):
                    If True, sets average hyperparameters (neurons and layers)
                    and saves the configured classifier. If False, adjusts the number of iterations dynamically.
        """
        if set_avg_hyperparams:
            self.trainer.set_avg_hyperparameters()
            self.trainer.save_classifier("data/classifier_avg_hyperparams.sav")

        else:
            #if service flag is true, simulate user decisions, else read from json iterations
            if self.service_flag:
                iterations = random.randint(200, 300)

                while True:
                    self.trainer.load_classifier("data/classifier_avg_hyperparams.sav")
                    classifier = self.trainer.train(iterations)
                    # Generate learning report
                    loss_curve = LearningPlotModel.get_loss_curve()
                    LearningPlotView.show_learning_plot(loss_curve)
                    # Simulate user decision on learning plot
                    choice = random.randint(0, 4)
                    if choice == 0:  # 20%
                        print("ITERATIONS OK")
                        break
                    if choice <= 2:  # 40%
                        print("INCREASE ITERATIONS BY 1/3")
                        iterations = math.ceil(iterations * (1 + 1 / 3))
                    else:  # 40%
                        print("DECREASE ITERATIONS BY 1/3")
                        iterations = math.ceil(iterations * (1 - 1 / 3))
            
            else:
                iterations = self.trainer.read_number_iterations()
                classifier = self.trainer.train(iterations)
                # Generate learning report
                loss_curve = LearningPlotModel.get_loss_curve()
                LearningPlotView.show_learning_plot(loss_curve)

            print("Learning report generated")
            print("number of iterations = ", iterations)
            print("training error =", classifier.get_training_error())