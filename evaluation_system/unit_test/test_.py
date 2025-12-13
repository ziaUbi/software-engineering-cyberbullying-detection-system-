import pytest
import os
import json
from unittest.mock import patch, mock_open


from evaluation_system.label import Label
from evaluation_system.evaluationReport import EvaluationReport
from evaluation_system.evaluationReportModel import EvaluationReportModel
from evaluation_system.labelBuffer import LabelBuffer
from evaluation_system.evaluationSystemParameters import EvaluationSystemParameters

# ==========================================
# 1. Data Models Tests (Label & Report)
# ==========================================

def test_label_creation_and_dict():
    """Verifies Label creation and dictionary conversion."""
    lbl = Label(uuid="123-abc", label="Bullying", expert=True)
    
    assert lbl.uuid == "123-abc"
    assert lbl.label == "Bullying"
    assert lbl.expert is True
    
    expected_dict = {"uuid": "123-abc", "label": "Bullying", "expert": True}
    assert lbl.to_dict() == expected_dict

def test_evaluation_report_metrics():
    """Verifies that EvaluationReport stores data correctly."""
    c_labels = [Label("1", "A", False)]
    e_labels = [Label("1", "A", True)]
    
    report = EvaluationReport(
        classifier_labels=c_labels, 
        expert_labels=e_labels,
        total_errors=5, 
        max_consecutive_errors=3,
        actual_total_errors=0, 
        actual_max_consecutive_errors=0
    )
    
    assert report.get_total_errors() == 5
    assert report.get_actual_total_errors() == 0
    assert len(report.get_classifier_labels()) == 1

# ==========================================
# 2. Evaluation Logic Tests
# ==========================================

@pytest.fixture
def report_model():
    """Fixture that returns a clean instance of the model."""
    return EvaluationReportModel()

def test_compute_total_errors(report_model):
    """Tests the total error calculation (case-insensitive comparison)."""
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

    errors = report_model.compute_actual_total_errors(c_labels, e_labels)
    assert errors == 1, "There should be exactly 1 error"

def test_compute_consecutive_errors(report_model):
    """Tests the calculation of maximum consecutive errors."""
    # Scenario: Error, Correct, Error, Error, Correct -> Max consecutive: 2
    c_labels = [
        Label("1", "A", False), Label("2", "A", False), 
        Label("3", "A", False), Label("4", "A", False), Label("5", "A", False)
    ]
    e_labels = [
        Label("1", "B", True),  # Error
        Label("2", "A", True),  # Reset
        Label("3", "B", True),  # Error
        Label("4", "B", True),  # Error (Consecutive)
        Label("5", "A", True)   # Reset
    ]

    max_cons = report_model.compute_actual_max_consecutive_errors(c_labels, e_labels)
    assert max_cons == 2

# ==========================================
# 3. Database Tests (LabelBuffer)
# ==========================================

@pytest.fixture
def temp_db_path(tmp_path):
    """Creates a temporary file path for the database."""
    # tmp_path is a native pytest fixture providing a unique temporary directory
    d = tmp_path / "data"
    d.mkdir()
    return str(d / "test_labels.db")

@pytest.fixture
def buffer(temp_db_path):
    """Initializes the buffer with the temporary DB."""
    # We patch os.path.join because LabelBuffer calculates the path internally
    # relative to its own file location.
    
    with patch("evaluation_system.labelBuffer.os.path.join", return_value=temp_db_path):
        buf = LabelBuffer("test_labels.db")
        yield buf
        # Pytest handles tmp_path cleanup automatically

def test_save_and_retrieve_labels(buffer):
    """Verifies saving and retrieving from the DB."""
    lbl_clf = Label(uuid="u1", label="bad", expert=False)
    lbl_exp = Label(uuid="u1", label="good", expert=True)

    buffer.save_label(lbl_clf)
    buffer.save_label(lbl_exp)

    assert buffer.get_num_classifier_labels() == 1
    assert buffer.get_num_expert_labels() == 1

    fetched_clf = buffer.get_classifier_labels(limit=10)
    assert fetched_clf[0].label == "bad"
    assert fetched_clf[0].expert is False

    fetched_exp = buffer.get_expert_labels(limit=10)
    assert fetched_exp[0].label == "good"
    assert fetched_exp[0].expert is True

def test_delete_labels(buffer):
    """Verifies deletion (sliding window)."""
    for i in range(3):
        buffer.save_label(Label(f"u{i}", "lbl", False))
        buffer.save_label(Label(f"u{i}", "lbl", True))

    buffer.delete_labels(limit=2)

    assert buffer.get_num_classifier_labels() == 1
    assert buffer.get_num_expert_labels() == 1

# ==========================================
# 4. Parameters Tests (Mocking)
# ==========================================

def test_load_parameters():
    """Tests loading parameters with simulated JSON files."""
    
    mock_local_data = {"min_number_labels": 50, "total_errors": 10, "max_consecutive_errors": 5}
    mock_global_data = {"Evaluation System": {"port": 9999}}
    
    # We mock open, json.load, and _validate_json to avoid touching the disk
    with patch("builtins.open", mock_open()) as mocked_file, \
         patch("json.load", side_effect=[mock_local_data, mock_global_data]), \
         patch("evaluation_system.evaluationSystemParameters.EvaluationSystemParameters._validate_json", return_value=True):
        
        EvaluationSystemParameters.loadParameters(basedir=".")

        assert EvaluationSystemParameters.min_number_labels == 50
        assert EvaluationSystemParameters.total_errors == 10
        assert EvaluationSystemParameters.max_consecutive_errors == 5