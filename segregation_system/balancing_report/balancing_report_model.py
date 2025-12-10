import os
import json
from segregation_json_handler import SegregationSystemJsonHandler
from segregation_system.balancing_report.balancing_report import BalancingReportData
from segregation_configuration import SegregationSystemConfiguration

class BalancingReportModel:
    def generate_balancing_report(self, sessions: list) -> dict:
        total = len(sessions)
        if total == 0:
            return {"is_balanced": False, "msg": "No sessions"}

        # Conta le classi (es. "Cyberbullying" vs "Safe")
        counts = {}
        for s in sessions:
            counts[s.label] = counts.get(s.label, 0) + 1

        is_minimum = True
        is_balanced = True
        report_details = {}
        tolerance = SegregationSystemConfiguration.balancing_report_threshold

        average = total / len(counts) 

        for label, count in counts.items():
            if count < SegregationSystemConfiguration.minimum_coverage_report_threshold:
                is_minimum = False
            if count < average * (1 - tolerance) or count > average * (1 + tolerance):
                is_balanced = False

            report_details[label] = {
                "count": count,
                "percentage": round((count / total) * 100, 2)
            }

        return BalancingReportData(
            total_sessions=total,
            class_distribution={label: details["count"] for label, details in report_details.items()},
            class_percentages={label: details["percentage"] for label, details in report_details.items()},
            is_minimum=is_minimum,
            is_balanced=is_balanced
        )

