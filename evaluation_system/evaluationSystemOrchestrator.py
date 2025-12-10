"""
Author: Rossana Antonella Sacco
"""

import os
import time
import json
import jsonschema
import random


from evaluation_system.evaluationSystemParameters import EvaluationSystemParameters
from evaluation_system.labelReceiverAndConfigurationSender import LabelReceiverAndConfigurationSender
from evaluation_system.labelBuffer import LabelBuffer
from evaluation_system.evaluationReportModel import EvaluationReportModel
from evaluation_system.evaluationReportView import EvaluationReportView

class EvaluationSystemOrchestrator:
    """
    This class is responsible for orchestrating the Evaluation System.
    It manages the main loop, state transitions, and interactions between components.
    """

    def __init__(self, basedir: str = "."):
        """
        Initialize the Evaluation System Orchestrator.
        
        :param basedir: Base directory of the Evaluation System.
        """
        self.basedir = basedir
        self.report_view = EvaluationReportView()

        EvaluationSystemParameters.loadParameters(self.basedir)
        # Check if service mode is enabled
        self.service = EvaluationSystemParameters.LOCAL_PARAMETERS.get("service", False)

        self.labels_buffer = LabelBuffer()
        self.communication_manager = LabelReceiverAndConfigurationSender(basedir=self.basedir)
        self.report_model = EvaluationReportModel(self.basedir)

    def _get_classifier_evaluation(self) -> tuple[bool, dict | None]:
        """
        Retrieve and validate the classifier evaluation status from the workspace file.

        :return: (False, None) if file doesn't exist. (True, data_dict) if exists and valid.
        """
        file_path = os.path.join(self.basedir, "human_operator_workspace", "classifier_evaluation.json")
        schema_path = os.path.join(self.basedir, "schemas", "classifier_evaluation_schema.json")

        try:
            if not os.path.exists(file_path):
                return False, None

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Validate against schema
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as schema_file:
                    schema = json.load(schema_file)
                    jsonschema.validate(data, schema)
            else:
                print(f"Warning: Schema file not found at {schema_path}")

            return True, data
            
        except jsonschema.ValidationError as e:
            print(f"Invalid evaluation file format: {e.message}")
            return False, None
        except Exception as e:
            print(f"Error reading evaluation file: {e}")
            return False, None

    def evaluate(self):
        """
        Main loop of the Evaluation System.
        """
        print("Evaluation System Orchestrator started.")
        
        self.communication_manager.start_server()

        while True:
            try:
                eval_exists, classifier_evaluation = self._get_classifier_evaluation()

                if not eval_exists:
                    # =================================================================
                    # STATE 1: LABEL COLLECTION (File does not exist)
                    # =================================================================
                    print("\n[State] Collecting Labels...")

                    while True:
                        
                        label = self.communication_manager.get_label()
                        
                        self.labels_buffer.save_label(label)
                        print(f" -> Label stored: {label.uuid} (Expert={label.expert})")

                            # Check if we have enough labels to create a report 
                        num_clf = self.labels_buffer.get_num_classifier_labels()
                        num_exp = self.labels_buffer.get_num_expert_labels()
                        min_req = EvaluationSystemParameters.min_number_labels

                        if num_clf >= min_req and num_exp >= min_req:
                            print("[State] Sufficient number of labels reached.")
                            break
                    
                    # Retrieve labels for report
                    c_labels = self.labels_buffer.get_classifier_labels(min_req)
                    e_labels = self.labels_buffer.get_expert_labels(min_req)

                    # Create the Report
                    # This method also saves the "classifier_evaluation.json" file with status "waiting_for_evaluation"
                    success, report_obj = self.report_model.create_evaluation_report(
                        c_labels, e_labels,
                        EvaluationSystemParameters.total_errors,
                        EvaluationSystemParameters.max_consecutive_errors
                    )
                    
                    if success and report_obj is not None:
                        print("[Info] Evaluation Report created.")
                        self.report_view.show_evaluation_report(report_obj)
                        # Clear buffer for next cycle
                        self.labels_buffer.delete_labels(min_req)
                        print("[Info] Buffer cleared.")

                        # --- SERVICE MODE HANDLING (AUTOMATIC TEST) ---
                        if self.service:
                            print("[Auto-Test] Simulating Human Evaluation...")
                            
                            is_good = random.random() > 0.14
                            
                            verdict = "good" if is_good else "bad"
                            print(f"[Auto-Test] Verdict: {verdict}")

                            if verdict == "bad":
                                self.communication_manager.send_configuration()
                                print("[Auto-Test] Configuration sent.")
                            
                            
                            self._remove_evaluation_file()
                            
                        print("[Info] Waiting for Human Operator action...")

                else:
                    # =================================================================
                    # STATE 2: WAITING FOR HUMAN OPERATOR EVALUATION (File exists)  
                    # =================================================================
                    status = classifier_evaluation.get("classifier_evaluation")

                    if status == "waiting_for_evaluation":
                        
                        print("Status: Waiting for Human Operator...", end="\r")
                        time.sleep(5) # Wait 5 seconds before checking again
                    
                    elif status == "good":
                        # Human operator approved
                        print("\n[Verdict] Human Operator: GOOD")
                        
                        # Remove the file to return to STATE 1 (Collection)
                        self._remove_evaluation_file()
                    
                    elif status == "bad":
                        # Human operator rejected the classifier
                        print("\n[Verdict] Human Operator: BAD")
                        # Send retrain command
                        print("[Action] Sending Configuration/Retrain request...")
                        self.communication_manager.send_configuration()
                        
                        # Remove the file to return to STATE 1
                        self._remove_evaluation_file()
            
            except KeyboardInterrupt:
                print("\nStopping Orchestrator...")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(2)

    def _remove_evaluation_file(self):
        """Helper to remove the evaluation file safely."""
        file_path = os.path.join(self.basedir, "human_operator_workspace", "classifier_evaluation.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print("[Info] Evaluation file removed. Ready for new cycle.")
        except OSError as e:
            print(f"Error removing file: {e}")

if __name__ == "__main__":
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Working directory set to: {current_dir}")

    orchestrator = EvaluationSystemOrchestrator(basedir=current_dir)
    orchestrator.evaluate()
    