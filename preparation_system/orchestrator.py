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

        print(f"PREPARATION ORCHESTRATOR INITIALIZED ")

    def prepare_session(self):
        """
        Main Loop: Process sessions iteratively.
        Corresponds to the main flow in the BPMN.
        """
        print("Starting preparation loop...")

        while True:
            try:
                # --- 1. RECEIVE RAW SESSION ---
                raw_session= self.json_io.get_raw_session()

                if raw_session is None:
                    continue  # Nessun messaggio, riprovo
                
                
                print(f"Processing UUID: {raw_session.get('uuid')}")
                # Stampa tutto il contenuto formattato
                # print(json.dumps(raw_session, indent=4, default=str))

                prepared_session = self.creator.create_prepared_session(raw_session)

                print("Prepared Session Created")

                # B. Correzione Outliers Audio (sulla lista di float appena estratta)
                correct_prepared_session = self.corrector.correct_absolute_outliers(prepared_session)
                
                print("Absolute Outliers Corrected")

                target_ip = ""
                target_port = 0
                
                if self.parameters.development_mode:
                    target_ip = self.parameters.configuration["ip_segregation"]
                    target_port = self.parameters.configuration["port_segregation"]
                    dest_name = "SEGREGATION"
                else:
                    # Production o Evaluation
                    target_ip = self.parameters.configuration["ip_production"]
                    target_port = self.parameters.configuration["port_production"]
                    dest_name = "PRODUCTION"

                # --- 5. SEND PREPARED SESSION ---
                success = self.json_io.send_prepared_session(target_ip, target_port, correct_prepared_session)

                if success:
                    print(f"Session {prepared_session.uuid} sent to {dest_name}.")
                else:
                    print(f"ERROR: Failed to send session {prepared_session.uuid} to {dest_name}.")

            except Exception as e:
                print(f"CRITICAL ERROR in Preparation Loop: {e}")
                time.sleep(1)


if __name__ == "__main__":
    orchestrator = PreparationSystemOrchestrator()
    orchestrator.prepare_session()