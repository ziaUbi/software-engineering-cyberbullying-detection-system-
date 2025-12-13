import unittest
from unittest.mock import patch, mock_open
import json
from evaluation_system.evaluationSystemParameters import EvaluationSystemParameters

class TestParameters(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("os.path.join", return_value="dummy_path") # Mock path join
    @patch("evaluation_system.evaluationSystemParameters.EvaluationSystemParameters._validate_json", return_value=True)
    def test_load_parameters(self, mock_validate, mock_path, mock_json_load, mock_file):
        """Tests loading static parameters from simulated JSON files."""
        
        # Simulate the content of the two JSON files (Local and Global)
        # loadParameters calls json.load twice (once for local, once for global)
        mock_json_load.side_effect = [
            # Local params
            {"min_number_labels": 50, "total_errors": 10, "max_consecutive_errors": 5},
            # Global params
            {"Evaluation System": {"port": 9999}} 
        ]

        EvaluationSystemParameters.loadParameters(basedir=".")

        # Verify that class attributes have been updated correctly
        self.assertEqual(EvaluationSystemParameters.min_number_labels, 50)
        self.assertEqual(EvaluationSystemParameters.total_errors, 10)
        self.assertEqual(EvaluationSystemParameters.max_consecutive_errors, 5)