import unittest
import os
from evaluation_system.labelBuffer import LabelBuffer
from evaluation_system.label import Label

class TestLabelBuffer(unittest.TestCase):

    def setUp(self):
        # Use a test DB name to avoid overwriting the real one
        self.test_db_name = "test_labels.db"
        self.buffer = LabelBuffer(db_name=self.test_db_name)

    def tearDown(self):
        # Remove the database file after each test to ensure a clean state
        if os.path.exists(self.buffer.db_path):
            os.remove(self.buffer.db_path)

    def test_save_and_retrieve_labels(self):
        """Verifies saving and differentiated retrieval for Expert/Classifier."""
        lbl_clf = Label(uuid="u1", label="bad", expert=False)
        lbl_exp = Label(uuid="u1", label="good", expert=True)

        self.buffer.save_label(lbl_clf)
        self.buffer.save_label(lbl_exp)

        # Verify counts
        self.assertEqual(self.buffer.get_num_classifier_labels(), 1)
        self.assertEqual(self.buffer.get_num_expert_labels(), 1)

        # Verify data retrieval
        fetched_clf = self.buffer.get_classifier_labels(limit=10)
        self.assertEqual(fetched_clf[0].label, "bad")
        self.assertFalse(fetched_clf[0].expert)

        fetched_exp = self.buffer.get_expert_labels(limit=10)
        self.assertEqual(fetched_exp[0].label, "good")
        self.assertTrue(fetched_exp[0].expert)

    def test_delete_labels(self):
        """Verifies deletion (sliding window mechanism)."""
        # Insert 3 labels for both expert and classifier
        for i in range(3):
            self.buffer.save_label(Label(f"u{i}", "lbl", False))
            self.buffer.save_label(Label(f"u{i}", "lbl", True))

        # Delete the first 2
        self.buffer.delete_labels(limit=2)

        # 1 label should remain for each
        self.assertEqual(self.buffer.get_num_classifier_labels(), 1)
        self.assertEqual(self.buffer.get_num_expert_labels(), 1)