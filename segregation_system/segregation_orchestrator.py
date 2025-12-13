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
from segregation_system.segregation_database import PreparedSessionDatabaseController
from segregation_system.segregation_configuration import SegregationSystemConfiguration
from segregation_system.prepared_session import PreparedSession

execution_state_file_path = "./segregation_system/data/execution_state.json"

class SegregationSystemOrchestrator:

    def __init__(self, testing: bool=True):

        self.set_testing(testing)
        self.db = PreparedSessionDatabaseController()
        self.message_broker = SessionReceiverAndConfigurationSender()
        self.message_broker.start_server()

    def run(self):

        SegregationSystemConfiguration.load_parameters() # Load the current Segregation System's parameters.

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

            min_num = SegregationSystemConfiguration.LOCAL_PARAMETERS['min_sessions_for_processing']

            while True:
                message = self.message_broker.get_last_message()
                message = message['message']

                if SegregationSystemJsonHandler.validate_json(message, "segregation_system/schemas/prepared_session_schema.json"):
                    print("Prepared Session Valid!")
                    try:
                        new_prepared_session = PreparedSession(message)
                        self.db.store_prepared_session(new_prepared_session)
                        number_of_collected_sessions = self.db.get_number_of_sessions_stored()
                        print("Prepared Session STORED! [", number_of_collected_sessions, "].")
                        if(new_prepared_session.uuid == ("Test")):
                            self.db.remove_all_prepared_sessions() 
                            self.reset_execution_state() 
                            return

                        if number_of_collected_sessions >= min_num:
                            print(number_of_collected_sessions, min_num)
                            break

                    except Exception:
                        print("Prepared Session Invalid! Can't store it.")
                        # Ignore invalid prepared sessions
                        continue

            print("Enough prepared session stored!")
            enough_collected_sessions = "OK"
            SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "enough_collected_sessions", "OK")

            all_prepared_sessions = self.db.get_all_prepared_sessions()

            print("Generating the balancing report...")
            balancing_report_model = BalancingReportModel.generate_balancing_report(all_prepared_sessions) 
            BalancingReportView.show_balancing_report(balancing_report_model, "plots")  
            print("Balancing report generated!")


            if self.get_testing():      # Simulating the user response...
                if balancing_report_model.is_balanced and balancing_report_model.is_minimum:
                    SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "balancing_report", "OK")
                    balancing_report_status = "OK"
                else:
                    SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "balancing_report", "NOT OK")
                    balancing_report_status = "NOT OK"
                    self.message_broker.send_configuration("unbalanced_classes")
                    self.reset_execution_state() 
                    return
                
                print("Generating the coverage report...")
                coverage_report_model = CoverageReportModel.generate_coverage_report(all_prepared_sessions) 
                CoverageReportView.show_coverage_report(coverage_report_model, "plots")  
                print("Coverage report generated!")

                if randrange(1) == 0:
                    SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "coverage_report", "OK")
                    coverage_report_status = "OK"
                else:
                    SegregationSystemJsonHandler.write_field_to_json(execution_state_file_path, "coverage_report", "NOT OK")
                    self.message_broker.send_configuration("coverage_not_satisfied")
                    coverage_report_status = "NOT OK"
                    self.reset_execution_state()
                    return
            else:
                if  coverage_report_status == "-" and balancing_report_status == "NOT OK" and enough_collected_sessions == "OK":
                    self.message_broker.send_configuration("unbalanced_classes")
                    self.reset_execution_state() 
                    return
            

        if (coverage_report_status == "-" and balancing_report_status == "OK" and enough_collected_sessions == "OK"):
            all_prepared_sessions = self.db.get_all_prepared_sessions()

            print("Generating the input coverage report...")
            coverage_report_model = CoverageReportModel.generate_coverage_report(all_prepared_sessions) 
            CoverageReportView.show_coverage_report(coverage_report_model, "plots")  
            print("Coverage report generated!")
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
            print("Learning sets sent to the Development System!")
            self.db.remove_all_prepared_sessions() 
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
        db = PreparedSessionDatabaseController()
        db.remove_all_prepared_sessions()
        while orchestrator.get_testing():
            orchestrator.run()
    else:
        orchestrator.run()
