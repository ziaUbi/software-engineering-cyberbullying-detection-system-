import time
import sys
import logging
from dataclasses import asdict
import json

# Import dei moduli interni del Preparation System
from preparation_system.preparation_configuration import PreparationSystemParameters
from preparation_system.preparation_session_channel import PreparationSessionChannel
from preparation_system.session_corrector import SessionCorrector
from preparation_system.prepared_session_creator import PreparedSessionCreator


class PreparationSystemOrchestrator:
    """
    Orchestrator for the Preparation System workflow.
    Manages the lifecycle: Receive -> Correct -> Extract -> Send.
    """

    def __init__(self):
        """
        Initializes the Orchestrator and all its sub-components.
        """
        print("PREPARATION ORCHESTRATOR INITIALIZATION")
        
        # 1. Load Configuration
        self.parameters = PreparationSystemParameters()
        
        # 2. Setup Communication Channel
        self.json_io = PreparationSessionChannel(
            host=self.parameters.ip_preparation,
            port=self.parameters.port_preparation
        )
        self.json_io.start_server()

        # 3. Setup Logic Components
        self.corrector = SessionCorrector(self.parameters)
        self.creator = PreparedSessionCreator(self.parameters)

        self.current_phase = self.parameters.configuration["current_phase"]  # current phase
        self.current_sessions = 0  # number of sessions processed in the current phase

        print(f"PREPARATION ORCHESTRATOR INITIALIZED ")
    
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
        elif self.current_phase == "development" and self.current_sessions == self.parameters.configuration["development_sessions"]:
            self.current_phase = "production"
            self.current_sessions = 0
            print("CHANGED TO PRODUCTION")

        
    def prepare_session(self):
        """
        Main Loop: Process sessions iteratively.
        Corresponds to the main flow in the BPMN.
        """
        print("Starting preparation loop...")

        while True:
            try:
                # --- RECEIVE RAW SESSION ---
                raw_session= self.json_io.get_raw_session()

                if raw_session is None:
                    continue  # No session received, retry
                
                
                # print(f"Processing UUID: {raw_session.get('uuid')}")
                # print(json.dumps(raw_session, indent=4, default=str))

                # --- CORRECT MISSING SAMPLES (events) ---
                corrected_raw_session = self.corrector.correct_missing_samples(raw_session, None)

                # Create prepared session from raw session, extracting features
                prepared_session = self.creator.create_prepared_session(corrected_raw_session)

                print("Prepared Session Created")

                # Correct absolute outliers
                correct_prepared_session = self.corrector.correct_absolute_outliers(prepared_session)
                # print(json.dumps(asdict(correct_prepared_session), indent=4, default=str))
                
                # print("Absolute Outliers Corrected")

                target_ip = ""
                target_port = 0
                
                if self.current_phase == "development":
                    target_ip = self.parameters.configuration["ip_segregation"]
                    target_port = self.parameters.configuration["port_segregation"]
                    dest_name = "SEGREGATION"
                else:
                    # Production o Evaluation
                    target_ip = self.parameters.configuration["ip_production"]
                    target_port = self.parameters.configuration["port_production"]
                    dest_name = "PRODUCTION"

                # --- SEND PREPARED SESSION ---
                success = self.json_io.send_prepared_session(target_ip, target_port, correct_prepared_session)

                if success:
                    print(f"Prepared Session sent to {dest_name}.")
                else:
                    print(f"ERROR: Failed to send session {correct_prepared_session.uuid} to {dest_name}.")

                if self.parameters.configuration["service"]:
                    self._update_session()

            except Exception as e:
                print(f"CRITICAL ERROR in Preparation Loop: {e}")
                time.sleep(1)


if __name__ == "__main__":
    orchestrator = PreparationSystemOrchestrator()
    orchestrator.prepare_session()