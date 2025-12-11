import os
import time
from random import randrange

from segregation_system.session_receiver_and_configuration_sender import SessionReceiverAndConfigurationSender
from segregation_system.segregation_json_handler import SegregationSystemJsonHandler
from segregation_system.balancing_report.balancing_report_model import BalancingReportModel
from segregation_system.balancing_report.balancing_report_view import BalancingReportView
from segregation_system.coverage_report.coverage_report_model import CoverageReportModel
from segregation_system.coverage_report.coverage_report_view import CoverageReportView
from segregation_system.learning_set_splitter import LearningSetSplitter
from segregation_system.segregation_database import SegregationSystemDatabaseController
from segregation_system.segregation_configuration import SegregationSystemConfiguration

execution_state_file_path = "data/execution_state.json"

class SegregationSystemOrchestrator:

    def __init__(self, testing: bool=True):

        self.set_testing(testing)
        self.db = SegregationSystemDatabaseController()
        self.message_broker = SessionReceiverAndConfigurationSender()
        self.message_broker.start_server()

    def run(self):

        SegregationSystemConfiguration.configure_parameters() # Load the current Segregation System's parameters.

        self.set_testing(SegregationSystemJsonHandler.read_field_from_json(execution_state_file_path,
                                                                                   "service_flag")) 
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

                # Convert the string into a dict object.
                message = SegregationSystemJsonHandler.string_to_dict(message['message'])

                # Validation of the prepared session.
                if SegregationSystemJsonHandler.validate_json(message, "schemas/prepared_session_schema.json"):
                    print("Prepared Session Valid!")
                    try:
                        self.db.store_prepared_session(message)
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

            print("Enough prepared session stored!")
            enough_collected_sessions = "OK"

            # The minimum number of prepared session has been reached!
            SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "enough_collected_sessions", "OK")

            # Get all the prepared sessions in the database.
            all_prepared_sessions = self.db.get_all_prepared_sessions()

            print("Generating the balancing report...")
            balancing_report_model = BalancingReportModel.generate_balancing_report(all_prepared_sessions)  # Generate the Balancing Report.
            print("Balancing report generated!")
            BalancingReportView.show_balancing_report(balancing_report_model, "plots")  # Show the balancing report to the user.

            if self.get_testing():
                # Simulating the user response...
                if balancing_report_model.is_balanced and balancing_report_model.is_minimum:
                    SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "balancing_report", "OK")
                else:
                    SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "balancing_report", "NOT OK")
                    self.message_broker.send_configuration("unbalanced_classes")
                    self.reset_execution_state() 

                coverage_report_model = CoverageReportModel.generate_coverage_report(all_prepared_sessions) 
                CoverageReportView.show_coverage_report(coverage_report_model, "plots")  

                if randrange(5) == 0:
                    SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "coverage_report", "OK")
                else:
                    SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "coverage_report", "NOT OK")
                    self.message_broker.send_configuration("features_not_covered")
                    self.reset_execution_state()
                    return
            else:
                return

        if not self.get_testing():
            if  coverage_report_status == "-" and balancing_report_status == "NOT OK" and enough_collected_sessions == "OK":
                self.message_broker.send_configuration("unbalanced_classes")
                self.reset_execution_state() 
                return

        if (coverage_report_status == "-" and balancing_report_status == "OK" and enough_collected_sessions == "OK"):
            # In this phase we must generate the input coverage report and ask the user response.
            # Get all the prepared sessions in the database.
            all_prepared_sessions = self.db.get_all_prepared_sessions()

            print("Generating the input coverage report...")
            coverage_report_model = CoverageReportModel.generate_coverage_report(all_prepared_sessions) 
            print("Input coverage report generated!")
            CoverageReportView.show_coverage_report(coverage_report_model, "plots")  

            return

        if not self.get_testing():
            if  coverage_report_status == "NOT OK" and balancing_report_status == "OK" and enough_collected_sessions == "OK":
                self.message_broker.send_configuration("coverage_not_satisfied")
                self.reset_execution_state()  
                return

        if (coverage_report_status == "OK" and balancing_report_status == "OK" and enough_collected_sessions == "OK"):
            # In this phase we must generate the learning sets according to the configuration and then send it to the Development system.
            # Get all the prepared sessions in the database.
            all_prepared_sessions = self.db.get_all_prepared_sessions()

            print("Generating the learning sets...")
            report_model = LearningSetSplitter()
            learning_sets = report_model.generateLearningSets(all_prepared_sessions)
            print("Learning sets generated!")

            network_info = SegregationSystemConfiguration.GLOBAL_PARAMETERS["Development System"]

            self.message_broker.send_message(network_info['ip'], network_info['port'],
                                             SegregationSystemJsonHandler.dict_to_string(learning_sets.to_dict()))
            self.db.reset_session_database() 
            self.reset_execution_state() 

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
