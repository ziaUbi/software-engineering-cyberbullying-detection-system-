import glob
import os
import random
import shutil

import joblib

from sklearn.metrics import log_loss

from development_system.classifier import Classifier
from development_system.configuration_parameters import ConfigurationParameters
from development_system.json_validator_reader_and_writer import JsonValidatorReaderAndWriter
from development_system.test_report_model import TestReportModel
from development_system.test_report_view import TestReportView
from development_system.learning_set import LearningSet


class TestingOrchestrator:
    """Orchestrator of the testing"""

    def __init__(self):
        """Initialize the orchestrator."""
        self.json_handler = JsonValidatorReaderAndWriter()
        self.winner_network = Classifier()
        self.test_report = None
        self.test_report_model = TestReportModel()
        self.test_report_view = TestReportView()
        self.service_flag = None
        self.learning_set = LearningSet([], [], [])

    @staticmethod
    def _delete_files_pattern(pattern):
        """Deletes a specific file.
            Attributes: pattern indicates the file to delete
         """
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)

    def test(self):
        """
            Executes the testing phase for the classifier and generates a test report.

            Returns:
                Union[TestReport, bool]: The test report (if `service_flag` is True) or
                a boolean indicating the test result (if `service_flag` is False).
        """

        self.service_flag = ConfigurationParameters.params['service_flag']
        if self.service_flag:
            classifier_index = random.randint(1, 5)
        else:
            self.json_handler.validate_json("intermediate_results/winner_network.json","schemas/winner_network_schema.json")
            data = self.json_handler.read_json_file("intermediate_results/winner_network.json")
            classifier_index = data["index"]
        # retrieve the winner network from the file
        self.winner_network = joblib.load("data/classifier" + str(classifier_index ) + ".sav")
        # extract the test set and the features and labels
        test_data = joblib.load("data/test_set.sav")
        result = self.learning_set.extract_features_and_labels(test_data)

        test_features = result[0]
        test_labels = result[1]

        self.winner_network.set_test_error(log_loss(test_labels, self.winner_network.predict_proba(test_features)))

        # GENERATE TEST REPORT
        self.test_report = self.test_report_model.generate_test_report(self.winner_network)
        print("test report generated")
        print("test error =", self.test_report.get_test_error())

        #remove all saved classifiers
        self._delete_files_pattern("data/classifier*.sav")

        # save winner network (we have to save again it because, now the test_error is updated)
        joblib.dump(self.winner_network, "data/classifier.sav")

        # CHECK TEST RESULT
        self.test_report_view.show_test_report(self.test_report)

        if self.service_flag:
            # true if the test is passed, false otherwise
            index = int(random.random() <= 0.99)
            if index == 1:
                return True
            else:
                return False
        else:
            # useful only for the test of the test report format
            return self.test_report