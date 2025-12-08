from development_system.json_handler_validator import JsonHandlerValidator

class ValidationReportView:
    """Shows the validation report"""

    @staticmethod
    def show_validation_report(classifiers, validation_tolerance):
        """
            Display and save the validation report.

            Args:
                validation_report (ValidationReport):
                    The validation report object containing the results of the validation process.
        """
        report = {'report': classifiers,
                  'validation_tolerance': validation_tolerance}
        print("Validation Report:")
        print(report)
        
        JsonHandlerValidator.write_json_file(report, "results/validation_report.json")