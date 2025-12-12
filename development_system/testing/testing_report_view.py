from development_system.configuration_parameters import ConfigurationParameters
from development_system.json_handler_validator import JsonHandlerValidator
import os

class TestReportView:
    """Shows the test report"""

    @staticmethod
    def show_test_report(model):
        """
        Displays and saves the test report.
        """
        print("Test Report:")
        print(model)
        JsonHandlerValidator.write_json_file(model, os.path.join(os.getcwd(), "development_system", "results", "test_report.json"))