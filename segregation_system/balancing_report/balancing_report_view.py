import os
import matplotlib.pyplot as plt
from segregation_system.balancing_report.balancing_report import BalancingReportData

class BalancingReportView:
    def show_balancing_report(balancing_report_model: BalancingReportData, workspace_dir):
        print("Balancing Report:")
        print(f"Total Sessions: {balancing_report_model.total_sessions}")
        print("Class Distribution:")
        for label, count in balancing_report_model.class_distribution.items():
            percentage = balancing_report_model.class_percentages[label]
            print(f" - {label}: {count} sessions ({percentage}%)")
        print(f"Classes Meet Minimum Coverage: {'Yes' if balancing_report_model.is_minimum else 'No'}")
        print(f"Classes Are Balanced: {'Yes' if balancing_report_model.is_balanced else 'No'}")

        labels = list(balancing_report_model.class_distribution.keys())
        counts = list(balancing_report_model.class_distribution.values())

        plt.bar(labels, counts, color='skyblue')
        plt.xlabel('Class Labels')
        plt.ylabel('Number of Sessions')
        plt.title('Class Distribution in Prepared Sessions')
        plt.xticks(rotation=45)
        plt.tight_layout()
        # plt.show()
        plt_path = "segregation_system/" + workspace_dir + '/balancing_report.png'
        plt.savefig(plt_path)
        return
