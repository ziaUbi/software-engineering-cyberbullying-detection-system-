import json
import os

class SegregationSystemConfiguration:
    GLOBAL_PARAMETERS = {}
    LOCAL_PARAMETERS = {}

    @staticmethod
    def configure_parameters(base_dir="."):
        # Carica configurazione globale di rete
        try:
            with open(os.path.join(base_dir, "configuration", "netconf.json"), "r") as f:
                SegregationSystemConfiguration.GLOBAL_PARAMETERS = json.load(f)
        except FileNotFoundError:
            print("[Config] netconf.json not found.")

        # Carica parametri locali del Segregation System
        try:
            with open(os.path.join(base_dir, "configuration", "segregation_parameters.json"), "r") as f:
                SegregationSystemConfiguration.LOCAL_PARAMETERS = json.load(f)
        except FileNotFoundError:
            print("[Config] segregation_parameters.json not found. Using defaults.")
            # Default fallback
            SegregationSystemConfiguration.LOCAL_PARAMETERS = {
                "min_sessions_for_processing": 2000,
                "balancing_report_threshold": 0.05,
                "minimum_coverage_report_threshold": 100,
                "number_of_record_of_session": 4,
                "training_set_percentage": 0.70,
                "validation_set_percentage": 0.20,
                "test_set_percentage": 0.10
            }