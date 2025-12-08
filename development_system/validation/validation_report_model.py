from typing import List

import joblib

from development_system.training.classifier import Classifier
from development_system.configuration_parameters import ConfigurationParameters


class ValidationReportModel:
    """Generates the report for the validation report"""

    def __init__(self):
        """Initialize the validation report model."""
        self.classifiers = []


    def append_classifier(self, classifier: Classifier):
        """
            Append a classifier to the list of classifiers.

            Args:
                classifier (Classifier): The classifier to append.
        """
        self.classifiers.append(classifier)


    def get_model(self):
        """
            Generate the validation report.
            Returns:
                   validation_report: is the validation report object.
        """
        # Assuming at least 5 classifiers to do a report
        top_5_classifiers = []
        for i in range(1, 6):

            min_validation_error = -1
            top_classifier = None

            # find the classifier with the minimum validation error
            for classifier in self.classifiers:  
                current_validation_error = classifier.get_validation_error()
                if min_validation_error == -1:
                    min_validation_error = current_validation_error
                    top_classifier = classifier
                elif min_validation_error > current_validation_error:
                    min_validation_error = current_validation_error
                    top_classifier = classifier

            #generate classifier report
            classifier_report = {'index': i}
            classifier_report.update(top_classifier.classifier_report())
            top_5_classifiers.append(classifier_report)
            #joblib.dump(top_classifier, "data/classifier" + str(i) + ".sav")

        return top_5_classifiers, ConfigurationParameters.params['validation_tolerance']