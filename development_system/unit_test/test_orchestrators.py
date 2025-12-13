import json
import os
from pathlib import Path

import pytest

from development_system.configuration_parameters import ConfigurationParameters


def test_validation_orchestrator_grid_search_runs(monkeypatch, tmp_path: Path):
    # Arrange config for a small grid that still satisfies ValidationReportModel's
    # assumption of at least 5 classifiers. layers [1..5], neurons [3].
    ConfigurationParameters.params = {
        "service_flag": False,
        "min_layers": 1,
        "max_layers": 5,
        "step_layers": 1,
        "min_neurons": 3,
        "max_neurons": 3,
        "step_neurons": 1,
        "validation_tolerance": 0.1,
        "test_tolerance": 0.1,
    }

    # Create inputs/iterations.json expected by Trainer.read_number_iterations, but we will monkeypatch validator calls
    (tmp_path / "inputs").mkdir()
    (tmp_path / "schemas").mkdir()
    (tmp_path / "inputs" / "iterations.json").write_text(json.dumps({"iterations": 5}))

    # Dummy Trainer that records hyperparameters and returns a simple object
    trained = []

    class DummyClassifier:
        def __init__(self, layers, neurons):
            self._layers = layers
            self._neurons = neurons
            # lower is better, make it depend on layers so we can rank deterministically
            self._val_err = 1.0 / layers

        def get_validation_error(self):
            return self._val_err

        def get_training_error(self):
            return self._val_err + 0.1

        def get_num_iterations(self):
            return 5

        def get_num_layers(self):
            return self._layers

        def get_num_neurons(self):
            return self._neurons

        def get_train_valid_error_difference(self):
            return 0.0

        def classifier_report(self):
            return {
                "num_iterations": self.get_num_iterations(),
                "validation_error": self.get_validation_error(),
                "training_error": self.get_training_error(),
                "difference": self.get_train_valid_error_difference(),
                "num_layers": self.get_num_layers(),
                "num_neurons": self.get_num_neurons(),
                "network_complexity": self.get_num_layers() * self.get_num_neurons(),
            }

    class DummyTrainer:
        def __init__(self, basedir):
            self.basedir = basedir
            self._layers = None
            self._neurons = None

        def read_number_iterations(self):
            return 5

        def set_hyperparameters(self, num_layers, num_neurons):
            self._layers = num_layers
            self._neurons = num_neurons

        def train(self, iterations):
            trained.append((self._layers, self._neurons, iterations))

        def validate(self):
            return DummyClassifier(self._layers, self._neurons)

    # Patch Trainer used inside ValidationOrchestrator
    import development_system.validation_orchestrator as vo
    monkeypatch.setattr(vo, "Trainer", DummyTrainer)

    # Avoid UI: capture the model passed to the view
    captured = {}
    monkeypatch.setattr(vo.ValidationReportView, "show_validation_report", lambda model: captured.setdefault("model", model))

    # Avoid filesystem writes performed by ValidationReportModel.get_model
    import development_system.validation.validation_report_model as vrm
    monkeypatch.setattr(vrm.joblib, "dump", lambda *args, **kwargs: None)

    # Act
    orch = vo.ValidationOrchestrator(basedir=str(tmp_path))
    result = orch.validation()

    # Assert: non-service mode returns None (no explicit return)
    assert result is None

    # Grid should have produced 5 * 1 = 5 combinations
    assert trained == [(1, 3, 5), (2, 3, 5), (3, 3, 5), (4, 3, 5), (5, 3, 5)]

    assert "model" in captured
    model = captured["model"]
    assert "top_5_classifiers" in model
    assert len(model["top_5_classifiers"]) == 5
    assert model["top_5_classifiers"][0]["num_layers"] in range(1, 6)


def test_testing_orchestrator_uses_winner_network_index(monkeypatch, tmp_path: Path):
    """Test non-service path: reads winner_network.json, loads classifierN.sav, computes test error, dumps classifier.sav."""
    # Arrange
    ConfigurationParameters.params = {
        "service_flag": False,
        "min_layers": 1,
        "max_layers": 1,
        "step_layers": 1,
        "min_neurons": 1,
        "max_neurons": 1,
        "step_neurons": 1,
        "validation_tolerance": 0.1,
        "test_tolerance": 0.1,
    }

    basedir = tmp_path
    (basedir / "inputs").mkdir()
    (basedir / "schemas").mkdir()
    (basedir / "data").mkdir()

    (basedir / "inputs" / "winner_network.json").write_text(json.dumps({"index": 7}))

    # Patch schema validation away (we are not asserting jsonschema correctness here)
    import development_system.testing_orchestrator as to
    monkeypatch.setattr(to.JsonHandlerValidator, "validate_json", lambda *args, **kwargs: True)

    # Provide a dummy winner classifier with predict_proba + set_test_error
    class DummyWinner:
        def __init__(self):
            self.test_error = None

        def predict_proba(self, X):
            # 2 samples, binary probs
            return [[0.9, 0.1], [0.1, 0.9]]

        def set_test_error(self, value):
            self.test_error = value

        def get_test_error(self):
            return self.test_error

        def get_validation_error(self):
            # required by TestReportModel
            return 0.5

        def get_valid_test_error_difference(self):
            if self.get_test_error() in (0, None):
                return 1
            return (self.get_test_error() - self.get_validation_error()) / self.get_test_error()

    dummy = DummyWinner()

    # Patch joblib load/dump
    loads = []
    dumps = []

    def fake_load(path):
        loads.append(path)
        return dummy

    def fake_dump(obj, path):
        dumps.append((obj, path))

    monkeypatch.setattr(to.joblib, "load", fake_load)
    monkeypatch.setattr(to.joblib, "dump", fake_dump)

    # Patch LearningSets to return a deterministic test set
    test_set = [
        {"uuid": "1", "f1": 0.0, "label": "cyberbullying"},
        {"uuid": "2", "f1": 1.0, "label": "not_cyberbullying"},
    ]
    monkeypatch.setattr(to.LearningSets, "get_test_set", lambda: test_set)

    # Avoid report UI
    monkeypatch.setattr(to.TestReportView, "show_test_report", lambda self, model: None)

    # Avoid filesystem cleanup complexity: return a couple of paths and stub out os.remove
    monkeypatch.setattr(to.glob, "glob", lambda pattern: [str(basedir / "data" / "classifier7.sav"), str(basedir / "data" / "classifier5.sav")])
    monkeypatch.setattr(to.os.path, "isfile", lambda p: True)

    removed = []
    monkeypatch.setattr(to.os, "remove", lambda p: removed.append(p))

    # Act
    orch = to.TestingOrchestrator(basedir=str(basedir))
    result = orch.test()

    # Assert
    assert result is None  # non-service mode has no explicit return
    assert any(p.endswith("classifier7.sav") for p in loads)
    assert removed  # some cleanup attempted
    assert any(path.endswith(os.path.join("data", "classifier.sav")) for _, path in dumps)
    assert dummy.test_error is not None
