import os
import time
from random import randrange

from segregation_system.session_receiver_and_configuration_sender import SessionReceiverAndConfigurationSender
from segregation_system.segregation_json_handler import SegregationSystemJsonHandler
from segregation_system.balancing_report.balancing_report_model import BalancingReportModel
from segregation_system.balancing_report.balancing_report_view import BalancingReportView
from segregation_system.coverage_report.coverage_report_model import CoverageReportModel
from segregation_system.learning_set_splitter import LearningSetSplitter
from segregation_system.segregation_database import SegregationSystemDatabaseController
from segregation_system.segregation_configuration import SegregationSystemConfiguration

execution_state_file_path = "data/execution_state.json"

class SegregationSystemOrchestrator:

    def __init__(self, testing: bool):

        self.set_testing(testing)  # Set the testing attribute.
        self.db = SegregationSystemDatabaseController()
        self.message_broker = SessionReceiverAndConfigurationSender()
        self.message_broker.start_server()

    def run(self):

        SegregationSystemConfiguration.configure_parameters() # Load the current Segregation System's parameters.
        # Retrieve the previous execution state left by the user.
        enough_collected_sessions = SegregationSystemJsonHandler.read_field_from_json(execution_state_file_path,
                                                                                   "enough_collected_sessions")
        balancing_report_status = SegregationSystemJsonHandler.read_field_from_json(execution_state_file_path,
                                                                                    "balancing_report")
        coverage_report_status = SegregationSystemJsonHandler.read_field_from_json(execution_state_file_path,
                                                                                   "coverage_report")

        if (coverage_report_status == "-" and balancing_report_status == "-" and enough_collected_sessions == "-") or self.get_testing():
            # In this phase we must gather the prepared sessions, generate the balancing report and ask the user response.
            print("Waiting for a message...")

            min_num = SegregationSystemConfiguration.LOCAL_PARAMETERS['minimum_number_of_collected_sessions']

            while True:
                # Receive a prepared session from the preparation system.
                message = self.message_broker.get_last_message()
                self.message_broker.send_timestamp("start")

                # Convert the string into a dict object.
                message = SegregationSystemJsonHandler.string_to_dict(message['message'])

                # Validation of the prepared session.
                if SegregationSystemJsonHandler.validate_json(message, "schemas/preparedSessionSchema.json"):
                    # If the prepared session is valid.
                    print("Prepared Session Valid!")
                    try:
                        self.db.store_prepared_session(message) # Store the new prepared session in the database.
                        number_of_collected_sessions = self.db.get_number_of_stored_prepared_sessions()
                        print("Prepared Session STORED! [", number_of_collected_sessions, "].")

                        if number_of_collected_sessions >= min_num:
                            # if the number of session stored is a mul of the minimum, then stop the cycle.
                            break

                    except Exception:
                        # If the prepared session is not valid, just ignore it.
                        # In case of any database error, just ignore it.
                        print("Prepared Session NOT Valid!")
                        continue

                self.message_broker.send_timestamp("end")

            print("Enough prepared session stored!")
            enough_collected_sessions = "OK"

            # The minimum number of prepared session has been reached!
            SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "enough_collected_sessions", "OK")

            # Get all the prepared sessions in the database.
            all_prepared_sessions = self.db.get_all_prepared_sessions()

            print("Generating the balancing report...")
            balancing_report_model = BalancingReportModel.generate_balancing_report(all_prepared_sessions)  # Generate the Balancing Report.
            print("Balancing report generated!")
            BalancingReportView.show_balancing_report(balancing_report_model)  # Show the balancing report to the user.

            if self.get_testing():
                # Simulating the user response...
                # Randomly assign an outcome, with 20,00% probability of it being True.
                if randrange(5) == 0:
                    print("CHECK PASSED - UNIFORM INPUT COVERAGE")
                else:
                    print("CHECK NOT PASSED - NOT UNIFORM INPUT COVERAGE")
                    self.message_broker.send_configuration("unbalanced_classes")
                    self.reset_execution_state()
                    return

        if not self.get_testing():
            # If we are not in testing.
            if  coverage_report_status == "-" and balancing_report_status == "NOT OK" and enough_collected_sessions == "OK":
                self.message_broker.send_configuration("unbalanced_classes")
                self.reset_execution_state()  # Reset the user responses file.

        if (coverage_report_status == "-" and balancing_report_status == "OK" and enough_collected_sessions == "OK") or self.get_testing():
            # In this phase we must generate the input coverage report and ask the user response.
            # Get all the prepared sessions in the database.
            all_prepared_sessions = self.db.get_all_prepared_sessions()

            print("Generating the input coverage report...")
            report_model = CoverageReportModel(all_prepared_sessions)  # Create the BalancingReportModel Object.
            report_model.generateCoverageReport()  # Generate the Balancing Report.
            print("Input coverage report generated!")

            if self.get_testing():
                # Simulating the user response...
                # Randomly assign an outcome, with 33,33% probability of it being True.
                if randrange(3) == 0:
                    print("CHECK PASSED - UNIFORM INPUT COVERAGE")
                else:
                    print("CHECK NOT PASSED - NOT UNIFORM INPUT COVERAGE")
                    self.message_broker.send_configuration("coverage_not_satisfied")
                    self.reset_execution_state()
                    return

        if not self.get_testing():
            # If we are not in testing.
            if  coverage_report_status == "NOT OK" and balancing_report_status == "OK" and number_of_session_status == "OK":
                self.message_broker.send_configuration("coverage_not_satisfied")
                self.reset_execution_state()  # Reset the user responses file.

        if (coverage_report_status == "OK" and balancing_report_status == "OK" and enough_collected_sessions == "OK") or self.get_testing():
            # In this phase we must generate the learning sets according to the configuration and then send it to the Development system.

            # Get all the prepared sessions in the database.
            all_prepared_sessions = self.db.get_all_prepared_sessions()

            print("Generating the learning sets...")
            report_model = LearningSetSplitter()
            learning_sets = report_model.generateLearningSets(all_prepared_sessions)
            print("Learning sets generated!")

            network_info = SegregationSystemConfiguration.GLOBAL_PARAMETERS["Development System"]

            # Send the learning sets to the Development System.
            self.message_broker.send_message(network_info['ip'], network_info['port'],
                                             SegregationSystemJsonHandler.dict_to_string(learning_sets.to_dict()))
            self.db.reset_session_database() # Reset the prepared session database.
            self.reset_execution_state() # Reset the user responses file.

    def get_testing(self) -> bool:
        return self.testing

    def set_testing(self, testing: bool):
        if not isinstance(testing, bool):
            raise ValueError("Testing mode must be a boolean value.")
        self.testing = testing

    def reset_execution_state(self):
        SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "enough_collected_sessions", "-")
        SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "balancing_report", "-")
        SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "coverage_report", "-")


# Example to test the class
if __name__ == "__main__":
    orchestrator = SegregationSystemOrchestrator(True)

    if orchestrator.get_testing():
        orchestrator.reset_execution_state()
        db = SegregationSystemDatabaseController()
        db.reset_session_database()
        while orchestrator.get_testing():
            orchestrator.run()
    else:
        orchestrator.run()



if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    orchestrator = SegregationSystemOrchestrator(base_dir)
    try:
        orchestrator.start()
    except KeyboardInterrupt:
        print("Stopping Segregation System...")