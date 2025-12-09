"""
Author: Rossana Antonella Sacco
"""

from typing import List
from evaluation_system.label import Label

class EvaluationReport:
    """
    Model class for the Evaluation Report.
    Acts as a Data Object to hold the results of an evaluation cycle.
    """

    def __init__(self, classifier_labels: List[Label], expert_labels: List[Label],
                 total_errors: int, max_consecutive_errors: int,
                 actual_total_errors: int, actual_max_consecutive_errors: int):
        """
        Constructor for the EvaluationReport class.

        :param classifier_labels: List of classifier labels.
        :param expert_labels: List of expert labels.
        :param total_errors: Total errors allowed (Threshold from Parameters).
        :param max_consecutive_errors: Maximum consecutive errors allowed (Threshold from Parameters).
        :param actual_total_errors: Actual total errors calculated.
        :param actual_max_consecutive_errors: Actual maximum consecutive errors calculated.
        """
        self.classifier_labels = classifier_labels
        self.expert_labels = expert_labels
        
        # Thresholds from parameters
        self.total_errors = total_errors
        self.max_consecutive_errors = max_consecutive_errors
        # These are the actual results of the calculation
        self.actual_total_errors = actual_total_errors
        self.actual_max_consecutive_errors = actual_max_consecutive_errors

    def get_classifier_labels(self) -> List[Label]:
        return self.classifier_labels

    def get_expert_labels(self) -> List[Label]:
        return self.expert_labels

    def get_total_errors(self) -> int:
        return self.total_errors

    def get_max_consecutive_errors(self) -> int:
        return self.max_consecutive_errors

    def get_actual_total_errors(self) -> int:
        return self.actual_total_errors

    def get_actual_max_consecutive_errors(self) -> int:
        return self.actual_max_consecutive_errors

    def to_dict(self) -> dict:
        """
        Convert the EvaluationReport object to a dictionary.
        """
        return {
            "classifier_labels": [label.to_dict() for label in self.classifier_labels],
            "expert_labels": [label.to_dict() for label in self.expert_labels],
            "total_errors": self.total_errors,
            "max_consecutive_errors": self.max_consecutive_errors,
            "actual_total_errors": self.actual_total_errors,
            "actual_max_consecutive_errors": self.actual_max_consecutive_errors
        }