from development_system.training.classifier import Classifier
from development_system.configuration_parameters import ConfigurationParameters


class TestReportModel:
    """Generates the model for the test report."""

    @staticmethod
    def generate_test_report(classifier: Classifier):
        """
            Generates a test report for the given classifier.

            Args:
                classifier (Classifier): An instance of a classifier that provides
                validation and test error metrics.
        """
        return {
            'test_tolerance': ConfigurationParameters.params['test_tolerance'],
            'validation_error': classifier.get_validation_error(),
            'test_error': classifier.get_test_error(),
            'difference': classifier.get_valid_test_error_difference(),
        }