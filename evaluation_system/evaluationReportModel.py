"""
Author: Rossana Antonella Sacco
"""

import os
import json
from typing import List, Optional, Tuple

from evaluation_system.label import Label
from evaluation_system.evaluationReport import EvaluationReport

class EvaluationReportModel:
    """
    Creates and saves to a JSON file the evaluation report of the Evaluation System.
    Calculates errors and manages file persistence.
    """

    def __init__(self, basedir: str = "."):
        """
        Initialize the EvaluationReportModel with an evaluation report id.

        :param basedir: Base directory of the Evaluation System.
        """
        self.basedir = basedir
        
        # creates the reports folder if it does not exist
        os.makedirs(os.path.join(self.basedir, "reports"), exist_ok=True)
        # creates the human operator workspace folder if it does not exist
        os.makedirs(os.path.join(self.basedir, "human_operator_workspace"), exist_ok=True)

        self.evaluation_report_id = self._get_next_evaluation_report_id()

    def _get_next_evaluation_report_id(self) -> int:
        """
        Get the next evaluation report id by checking the reports folder for existing report files.
        Scans 'evaluation_report_X.json' files.

        :return: The next evaluation report id.
        """
        reports_dir = os.path.join(self.basedir, "reports")
        if not os.path.exists(reports_dir):
            return 0

        report_files = [f for f in os.listdir(reports_dir) if
                        f.startswith("evaluation_report_") and f.endswith(".json")]
        
        if not report_files:
            return 0
            
        # Extract the highest existing ID and increment it
        try:
            max_id = max(int(f.split("_")[-1].split(".")[0]) for f in report_files)
            return max_id + 1
        except ValueError:
            return 0

    def create_evaluation_report(self, classifier_labels: List[Label], expert_labels: List[Label],
                                 total_errors: int, max_consecutive_errors: int) -> Tuple[bool,Optional[EvaluationReport]]:
        """
        Create an evaluation report with the given classifier and expert labels, calculate metrics,
        and save it to a JSON file.

        :return: True if the evaluation report was successfully saved, False otherwise.
        """
        
        # Compute actual errors
        actual_total_errors = self.compute_actual_total_errors(classifier_labels, expert_labels)
        actual_max_consecutive_errors = self.compute_actual_max_consecutive_errors(classifier_labels, expert_labels)

        # DTO Creation
        evaluation_report = EvaluationReport(
            classifier_labels, expert_labels,
            total_errors, max_consecutive_errors,
            actual_total_errors, actual_max_consecutive_errors
        )
        # Save to JSON file
        try:
            report_filename = f"evaluation_report_{self.evaluation_report_id}.json"
            report_path = os.path.join(self.basedir, "reports", report_filename)
            
            with open(report_path, "w", encoding="utf-8") as f:
                data = evaluation_report.to_dict()
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            # Increment the report ID for the next report
            self.evaluation_report_id += 1

            # Also save a copy in the human operator workspace
            workspace_path = os.path.join(self.basedir, "human_operator_workspace", "classifier_evaluation.json")
            with open(workspace_path, "w", encoding="utf-8") as ce:
                # Initial placeholder content
                json.dump({"classifier_evaluation": "waiting_for_evaluation"}, ce, ensure_ascii=False, indent=4)

            return True, evaluation_report           
        except Exception as e:
            print(f"Error saving evaluation report: {e}")
            return False

    def compute_actual_total_errors(self, classifier_labels: List[Label], expert_labels: List[Label]) -> int:
        """
        Compute the actual total errors in the evaluation report.
        Compares 'cyberbullying' strings.
        """
        actual_total_errors = 0
        limit = min(len(classifier_labels), len(expert_labels))
        
        for i in range(limit):
            # Compare 'cyberbullying' strings after stripping and lowering case
            val_c = str(classifier_labels[i].cyberbullying).strip().lower()
            val_e = str(expert_labels[i].cyberbullying).strip().lower()
            
            if val_c != val_e:
                actual_total_errors += 1
                
        return actual_total_errors

    def compute_actual_max_consecutive_errors(self, classifier_labels: List[Label], expert_labels: List[Label]) -> int:
        """
        Compute the actual maximum consecutive errors in the evaluation report.
        """
        actual_max_consecutive_errors = 0
        consecutive_errors = 0
        limit = min(len(classifier_labels), len(expert_labels))
        
        for i in range(limit):
            val_c = str(classifier_labels[i].cyberbullying).strip().lower()
            val_e = str(expert_labels[i].cyberbullying).strip().lower()
            
            if val_c != val_e:
                consecutive_errors += 1
                if consecutive_errors > actual_max_consecutive_errors:
                    actual_max_consecutive_errors = consecutive_errors
            else:
                consecutive_errors = 0
                
        return actual_max_consecutive_errors