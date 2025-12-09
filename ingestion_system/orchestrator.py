"""
Author: Martina Fabiani

"""
from dataclasses import asdict
import json
import time

from ingestion_system.ingestion_configuration import Parameters
from ingestion_system.record_buffer import RecordBufferController
from ingestion_system.raw_session_creator import RawSessionCreator
from ingestion_system.record_and_session_channel import RecordAndSessionChannel
from ingestion_system.record_sufficiency_checker import RecordSufficiencyChecker

class IngestionSystemOrchestrator:
    """
    Orchestrator for the ingestion system workflow.
    Manages instances of system components.
    """

    def __init__(self):
        """
        Initializes the IngestionSystemOrchestrator object.
        """

        print("INGESTION ORCHESTRATOR INITIALIZATION")

        # parameters class configuration
        self.parameters = Parameters()

        # record sufficiency checker configuration
        self.sufficiency_checker = RecordSufficiencyChecker()

        # buffer class configuration
        self.buffer_controller = RecordBufferController()

        # raw session configuration
        self.session_creator = RawSessionCreator()

        # IO configuration
        self.json_io = RecordAndSessionChannel(host= self.parameters.configuration["ip_ingestion"]
                                                 , port=self.parameters.configuration["port_ingestion"])  # parameters of Ingestion server
        self.json_io.start_server()

        self.current_sessions = 0  # number of sessions received in the current phase
        self.current_phase = self.parameters.configuration["current_phase"]  # current phase

        print("INGESTION ORCHESTRATOR INITIALIZED")

    def _update_session(self):
        # updates the number of session received and eventually changes the current phase
        self.current_sessions += 1

        #if we are in production and the number of sessions sent is reached, change to evaluation
        if self.current_phase == "production" and self.current_sessions == self.parameters.configuration["production_sessions"]:
            self.current_phase = "evaluation"
            self.current_sessions = 0
            print("CHANGED TO EVALUATION")
        # if we are in evaluation and the number of sessions sent is reached, change to production
        elif self.current_phase == "evaluation" and self.current_sessions == self.parameters.configuration["evaluation_sessions"]:
            self.current_phase = "production"
            self.current_sessions = 0
            print("CHANGED TO PRODUCTION")


    def process_record(self):
        """
        Process a record through the ingestion workflow.
        Main Loop of the Ingestion System.
        """
        processed_count = 0
        sessions_created = 0
        
        print("Starting processing loop...")

        while True:  # receive records iteratively
            try:
                # receives new record
                incoming_result = self.json_io.get_record(timeout=2.0)

                if incoming_result is None:
                    continue  # no record received, continue the loop

                is_valid, new_record = incoming_result
                if not is_valid or new_record is None:
                    print("Received invalid record, skipping...")
                    continue  # skip invalid records
                
                processed_count += 1
                print(f"Processed records count: {processed_count}")
                # stores record
                self.buffer_controller.store_record(new_record)

                uuid = new_record["value"]["UUID"]

                # checks if records are sufficient to create a raw session
                if not self.sufficiency_checker.are_records_sufficient(uuid, self.current_phase):
                    continue
                
                print(f"Creating RawSession for UUID: {uuid}")
                # retrieves stored records
                stored_records = self.buffer_controller.get_records(uuid)

                # creates raw session
                raw_session = self.session_creator.create_raw_session(stored_records)
                sessions_created += 1
                print(f"RawSessions created count: {sessions_created}")

                # removes records
                self.buffer_controller.remove_records(new_record["value"]["UUID"])

                # marks missing samples with "None" and checks if the session is valid
                session_valid, marked_raw_session = self.session_creator.mark_missing_samples(raw_session, None)
                
                if not session_valid:
                    continue  # do not send anything

                # if in evaluation phase, sends labels to evaluation system
                if self.current_phase == "evaluation":
                    label = {
                        "uuid": marked_raw_session.uuid,
                        "label": marked_raw_session.label
                    }
                    json_label = json.dumps(label) #json
                    print("Send Label to Evaluation System: ", json_label)

                    self.json_io.send_label(target_ip=self.parameters.configuration["ip_evaluation"],
                                              target_port=self.parameters.configuration["port_evaluation"], label_data=label)

                # sends raw session to preparation system
                session_dict = asdict(marked_raw_session)
                self.json_io.send_raw_session(target_ip=self.parameters.configuration["ip_preparation"],
                                          target_port=self.parameters.configuration["port_preparation"], raw_session_data=session_dict)

                print(f"Raw Session sent for UUID: {uuid}")
                #update the session sent counter only it is production/evaluation
                #because development is changed by the human
                if self.current_phase != "development":
                    #if it is not production testing phase, count sessions to change then phase
                    #otherwise, if it is production testing, stop counting, no phase change needed
                    if not self.parameters.configuration["service"]:
                        self._update_session()

            except Exception as e:
                print(f"Error during ingestion: {e}")
                time.sleep(1)  # brief pause before retrying




if __name__ == "__main__":
    orchestrator = IngestionSystemOrchestrator()
    orchestrator.process_record()