import unittest
from evaluation_system.label import Label
from evaluation_system.evaluationReport import EvaluationReport

class TestModels(unittest.TestCase):

    def test_label_creation_and_dict(self):
        """Verifies Label creation and dictionary conversion."""
        lbl = Label(uuid="123-abc", label="Bullying", expert=True)
        
        self.assertEqual(lbl.uuid, "123-abc")
        self.assertEqual(lbl.label, "Bullying")
        self.assertTrue(lbl.expert)
        
        # Verify to_dict method
        expected_dict = {"uuid": "123-abc", "label": "Bullying", "expert": True}
        self.assertEqual(lbl.to_dict(), expected_dict)

    def test_evaluation_report_metrics_storage(self):
        """Verifies that EvaluationReport stores data correctly."""
        c_labels = [Label("1", "A", False)]
        e_labels = [Label("1", "A", True)]
        
        # Simulate a created report
        report = EvaluationReport(
            classifier_labels=c_labels, 
            expert_labels=e_labels,
            total_errors=5, 
            max_consecutive_errors=3,
            actual_total_errors=0, 
            actual_max_consecutive_errors=0
        )
        
        self.assertEqual(report.get_total_errors(), 5)
        self.assertEqual(report.get_actual_total_errors(), 0)
        self.assertEqual(len(report.get_classifier_labels()), 1)