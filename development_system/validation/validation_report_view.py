from development_system.json_handler_validator import JsonHandlerValidator
import os

class ValidationReportView:
    """Shows the validation report"""

    @staticmethod
    def show_validation_report(model):
        """
            Display and save the validation report.

            Args:
                validation_report (ValidationReport):
                    The validation report object containing the results of the validation process.
        """
        report = {'report': model['top_5_classifiers'],
                  'validation_tolerance': model['validation_tolerance']}
        print("Validation Report:")
        print(report)
        
        JsonHandlerValidator.write_json_file(report, os.path.join(os.getcwd(), "development_system", "results", "validation_report.json"))