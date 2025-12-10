"""
Author: Rossana Antonella Sacco
"""

from evaluation_system.evaluationReport import EvaluationReport

class EvaluationReportView:
    """
    Class responsible for displaying the Evaluation Report to the console.
    It provides a live summary of the performance metrics and specific mismatch details.
    """

    def show_evaluation_report(self, report: EvaluationReport) -> None:
        """
        Prints the formatted details of the evaluation report to the standard output.

        :param report: The EvaluationReport object containing data to display.
        """
        
        #Extract Metrics
        actual_total = report.get_actual_total_errors()
        allowed_total = report.get_total_errors()
        
        actual_consecutive = report.get_actual_max_consecutive_errors()
        allowed_consecutive = report.get_max_consecutive_errors()
        
        num_labels = len(report.get_classifier_labels())

        #Header
        print("\n" + "="*60)
        print(f"{'CYBERBULLYING EVALUATION REPORT':^60}")
        print("="*60)
        
        print(f"Labels Processed: {num_labels}")
        print("-" * 60)
        
        
        print(f"{'METRIC':<30} | {'ACTUAL':<10} | {'LIMIT (Max)':<10}")
        print("-" * 60)
        
        
        alert_total = " (!)" if actual_total > allowed_total else ""
        print(f"{'Total Errors':<30} | {str(actual_total) + alert_total:<10} | {allowed_total:<10}")
        
        alert_cons = " (!)" if actual_consecutive > allowed_consecutive else ""
        print(f"{'Max Consecutive Errors':<30} | {str(actual_consecutive) + alert_cons:<10} | {allowed_consecutive:<10}")
        
        print("-" * 60)

        
        passed = (actual_total <= allowed_total) and (actual_consecutive <= allowed_consecutive)

        if passed:
            print(f"RESULT: [PASSED]")
            print("System performance is within acceptable parameters.")
        else:
            print(f"RESULT: [FAILED]")
            print("Performance degraded. Specific errors follow below:")
            print("-" * 60)
            self._print_mismatches(report)

        print("="*60 + "\n")

    def _print_mismatches(self, report: EvaluationReport):
        """
        Helper method to print the specific labels where the Classifier disagreed with the Expert.
        Useful for debugging.
        """
        c_labels = report.get_classifier_labels()
        e_labels = report.get_expert_labels()
        
        count = 0
        limit = min(len(c_labels), len(e_labels))
        
        print(f"{'UUID (Prefix)':<12} | {'AI Prediction':<15} | {'Expert Label':<15}")
        print("-" * 46)

        for i in range(limit):
            
            val_c = str(c_labels[i].cyberbullying).strip()
            val_e = str(e_labels[i].cyberbullying).strip()
            
            if val_c.lower() != val_e.lower():
                uuid_short = c_labels[i].uuid[:8] 
                print(f"{uuid_short:<12} | {val_c:<15} | {val_e:<15}")
                count += 1
                
                if count >= 10:
                    remaining = report.get_actual_total_errors() - 10
                    if remaining > 0:
                        print(f"... and {remaining} more errors.")
                    break