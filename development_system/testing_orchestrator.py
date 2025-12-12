import glob
import os
import random
import shutil
import joblib
from sklearn.metrics import log_loss

from development_system.training.classifier import Classifier
from development_system.configuration_parameters import ConfigurationParameters
from development_system.json_handler_validator import JsonHandlerValidator
from development_system.testing.testing_report_model import TestReportModel
from development_system.testing.testing_report_view import TestReportView
from development_system.training.learning_sets import LearningSets


class TestingOrchestrator:
    """Orchestrator of the testing"""

    def __init__(self, basedir):
        """Initialize the orchestrator."""
        self.basedir = basedir
        self.winner_network = Classifier()
        self.test_report = None
        self.test_report_model = TestReportModel()
        self.test_report_view = TestReportView()
        self.service_flag = ConfigurationParameters.params['service_flag']
        

    def test(self):
        """
            Executes the testing phase for the classifier and generates a test report.
        """        
        if self.service_flag:
            # in service mode, the winner network is the best classifier found during validation
            classifier_index = 1
        else:
            JsonHandlerValidator.validate_json(os.path.join(self.basedir, "inputs", "winner_network.json"), os.path.join(self.basedir, "schemas", "winner_network_schema.json"))
            data = JsonHandlerValidator.read_json_file(os.path.join(self.basedir, "inputs", "winner_network.json"))
            classifier_index = data["index"]

        # Retrieve the winner network from the classifier file
        self.winner_network = joblib.load(os.path.join(self.basedir, "data", "classifier" + str(classifier_index ) + ".sav"))
        
        test_set = LearningSets.get_test_set()
        result = LearningSets.extract_features_and_labels(test_set)

        test_features = result[0]
        test_labels = result[1]

        self.winner_network.set_test_error(log_loss(test_labels, self.winner_network.predict_proba(test_features)))

        # Remove all saved validation classifiers and save winner classifier
        for file_path in glob.glob(os.path.join(self.basedir, "data", "classifier*.sav")):
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)

        joblib.dump(self.winner_network, os.path.join(self.basedir, "data", "classifier.sav"))

        # Generate test report
        model = self.test_report_model.generate_test_report(self.winner_network)
        self.test_report_view.show_test_report(model)
        print("Test report generated")

        # In service mode, randomize the test outcome
        if self.service_flag:
            index = int(random.random() <= 0.99)
            if index == 1:
                return True
            else:
                return False
            