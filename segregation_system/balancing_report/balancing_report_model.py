import os
import json
from typing import List
from segregation_system.prepared_session import PreparedSession
from segregation_system.segregation_json_handler import SegregationSystemJsonHandler
from segregation_system.balancing_report.balancing_report import BalancingReportData
from segregation_system.segregation_configuration import SegregationSystemConfiguration

class BalancingReportModel:
    def generate_balancing_report(sessions: List[PreparedSession]) -> BalancingReportData:
        total = len(sessions)
        counts = {}
        for s in sessions:
            if type(s) is dict:
                s = PreparedSession(s)
            label = s.label
            if label not in counts:
                counts[label] = 0
            counts[label] += 1

        is_minimum = True
        is_balanced = True
        report_details = {}
        tolerance = SegregationSystemConfiguration.LOCAL_PARAMETERS["balancing_report_threshold"]

        average = total / len(counts) 

        for label, count in counts.items():
            if count < SegregationSystemConfiguration.LOCAL_PARAMETERS["minimum_coverage_report_threshold"]:
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

