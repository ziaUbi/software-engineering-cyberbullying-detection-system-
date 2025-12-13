import unittest
from evaluation_system.evaluationReportModel import EvaluationReportModel
from evaluation_system.label import Label

class TestEvaluationLogic(unittest.TestCase):

    def setUp(self):
        # Initialize the model. We don't worry about files for these pure logic tests.
        self.model = EvaluationReportModel()

    def test_compute_total_errors(self):
        """Tests the total error calculation (case-insensitive comparison)."""
        # Scenario: 1 error out of 3
        # Note: The logic uses strip().lower() for comparison
        c_labels = [
            Label("1", "Good", False),
            Label("2", "Bad", False),
            Label("3", "Good ", False) # Extra space to test strip()
        ]
        e_labels = [
            Label("1", "good", True),   # Match (case insensitive)
            Label("2", "Good", True),   # Mismatch
            Label("3", "good", True)    # Match (strip + case insensitive)
        ]

        errors = self.model.compute_actual_total_errors(c_labels, e_labels)
        self.assertEqual(errors, 1, "There should be exactly 1 error")

    def test_compute_consecutive_errors(self):
        """Tests the calculation of maximum consecutive errors."""
        # Scenario: Error, Correct, Error, Error, Correct -> Max consecutive: 2
        c_labels = [
            Label("1", "A", False), Label("2", "A", False), 
            Label("3", "A", False), Label("4", "A", False), Label("5", "A", False)
        ]
        e_labels = [
            Label("1", "B", True),  # Error 1
            Label("2", "A", True),  # Reset
            Label("3", "B", True),  # Error 1
            Label("4", "B", True),  # Error 2 (Consecutive)
            Label("5", "A", True)   # Reset
        ]

        max_cons = self.model.compute_actual_max_consecutive_errors(c_labels, e_labels)
        self.assertEqual(max_cons, 2, "Max consecutive errors should be 2")