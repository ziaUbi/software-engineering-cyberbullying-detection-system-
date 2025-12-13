import os
from pathlib import Path

import joblib
import pytest

from development_system.configuration_parameters import ConfigurationParameters
from development_system.training.learning_sets import LearningSets
from development_system.training.trainer import Trainer


def test_extract_features_and_labels_maps_labels():
    dataset = [
        {"uuid": "1", "text": "a", "feature1": 0.1, "label": "cyberbullying"},
        {"uuid": "2", "text": "b", "feature1": 0.2, "label": "not_cyberbullying"},
    ]
    X, y = LearningSets.extract_features_and_labels(dataset)
    assert "label" not in X.columns
    assert "uuid" not in X.columns
    assert list(y.values) == [1, 0]


def test_from_dict_rejects_non_dict():
    with pytest.raises(ValueError):
        LearningSets.from_dict([1, 2, 3])  # type: ignore


def test_save_and_get_sets_roundtrip(tmp_path: Path, monkeypatch):
    # Make LearningSets use a temp basedir so we don't pollute the project folder
    monkeypatch.setattr(LearningSets, "basedir", str(tmp_path))

    ls = LearningSets(
        training_set=[{"uuid": "1", "label": "cyberbullying"}],
        validation_set=[{"uuid": "2", "label": "not_cyberbullying"}],
        test_set=[{"uuid": "3", "label": "cyberbullying"}],
    )
    LearningSets.save_learning_sets(ls)

    assert (tmp_path / "data" / "training_set.sav").exists()
    assert LearningSets.get_training_set()[0]["uuid"] == "1"
    assert LearningSets.get_validation_set()[0]["uuid"] == "2"
    assert LearningSets.get_test_set()[0]["uuid"] == "3"


def test_trainer_set_avg_hyperparameters(monkeypatch, tmp_path: Path):
    # Configure params used by set_avg_hyperparameters
    ConfigurationParameters.params = {
        "min_neurons": 2,
        "max_neurons": 6,
        "min_layers": 1,
        "max_layers": 3,
        "service_flag": False,
        "step_layers": 1,
        "step_neurons": 1,
        "validation_tolerance": 0.1,
        "test_tolerance": 0.1,
    }
    t = Trainer(basedir=str(tmp_path))
    t.set_avg_hyperparameters()

    assert t.classifier.get_num_neurons() == 4  # ceil((6+2)/2)
    assert t.classifier.get_num_layers() == 2   # ceil((3+1)/2)


def test_trainer_save_and_load_classifier(tmp_path: Path):
    ConfigurationParameters.params = {
        "min_neurons": 1,
        "max_neurons": 1,
        "min_layers": 1,
        "max_layers": 1,
        "service_flag": False,
        "step_layers": 1,
        "step_neurons": 1,
        "validation_tolerance": 0.1,
        "test_tolerance": 0.1,
    }
    t = Trainer(basedir=str(tmp_path))
    t.classifier.set_num_layers(2)
    t.classifier.set_num_neurons(10)

    p = tmp_path / "clf.sav"
    t.save_classifier(str(p))

    t2 = Trainer(basedir=str(tmp_path))
    t2.load_classifier(str(p))

    assert t2.classifier.get_num_layers() == 2
    assert t2.classifier.get_num_neurons() == 10


@pytest.mark.xfail(reason="LearningSets.from_json currently has no return statement in the provided code")
def test_from_json_returns_learning_sets(tmp_path: Path):
    # This test documents an existing bug: from_json ends without returning.
    sample = {
        "training_set": [],
        "validation_set": [],
        "test_set": [],
    }
    fp = tmp_path / "learning_sets.json"
    fp.write_text(__import__("json").dumps(sample))

    out = LearningSets.from_json(str(fp))
    assert isinstance(out, LearningSets)
