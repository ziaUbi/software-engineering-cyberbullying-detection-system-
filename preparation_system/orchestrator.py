import time
import sys
import logging
from dataclasses import asdict

# Import dei moduli interni del Preparation System
from preparation_system.preparation_configuration import PreparationSystemParameters
from preparation_system.preparation_session_channel import PreparationSessionChannel
from preparation_system.session_corrector import SessionCorrector
from preparation_system.prepared_session_creator import PreparedSessionCreator

# Import opzionale per type hinting
from typing import Dict, Any

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
                # Bloccante con timeout per permettere graceful shutdown se necessario
                raw_session= self.json_io.get_raw_session(timeout=2.0)

                if raw_session is None:
                    continue  # Nessun messaggio, riprovo
                
                
                print(f"Processing UUID: {raw_session.get('uuid')}")

                # --- 2. CORRECT MISSING SAMPLES ---
                # Usa placeholder 'None' o specifico se definito
                self.corrector.correct_missing_samples(raw_session, None)

                prepared_session = self.creator.create_prepared_session(raw_session)

                # B. Correzione Outliers Audio (sulla lista di float appena estratta)
                corrected_audio_db = self.corrector.correct_absolute_outliers(prepared_session.audio_db)
                prepared_session.audio_db = corrected_audio_db

                target_ip = ""
                target_port = 0
                
                if self.parameters.development_mode:
                    target_ip = self.parameters.ip_segregation
                    target_port = self.parameters.port_segregation
                    dest_name = "SEGREGATION"
                else:
                    # Production o Evaluation
                    target_ip = self.parameters.ip_classification
                    target_port = self.parameters.port_classification
                    dest_name = "CLASSIFICATION"

                # --- 5. SEND PREPARED SESSION ---
                success = self.json_io.send_prepared_session(target_ip, target_port, prepared_session)

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