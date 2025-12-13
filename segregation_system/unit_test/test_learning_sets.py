import json
from pathlib import Path

import pytest

from segregation_system.learning_set import LearningSet
from segregation_system.learning_set_splitter import LearningSetSplitter
from segregation_system.prepared_session import PreparedSession
from segregation_system.segregation_configuration import SegregationSystemConfiguration


@pytest.fixture()
def prepared_session_dict(project_root: Path) -> dict:
    p = project_root / "segregation_system" / "inputs" / "prepared_session.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_learning_set_property_validation(prepared_session_dict: dict):
    ps = PreparedSession(prepared_session_dict)
    ls = LearningSet([ps], [ps], [ps])

    with pytest.raises(ValueError):
        ls.training_set = ["not a prepared session"]


def test_learning_set_to_dict_returns_objects(prepared_session_dict: dict):
    ps = PreparedSession(prepared_session_dict)
    ls = LearningSet([ps], [], [])
    d = ls.to_dict()
    # Current implementation returns PreparedSession objects (not dicts).
    assert d["training_set"][0] is ps


def test_splitter_respects_percentages(monkeypatch: pytest.MonkeyPatch, prepared_session_dict: dict):
    # Arrange configuration and make shuffle deterministic
    SegregationSystemConfiguration.LOCAL_PARAMETERS = {
        "training_set_percentage": 0.5,
        "validation_set_percentage": 0.25,
        "test_set_percentage": 0.25,
    }
    monkeypatch.setattr("segregation_system.learning_set_splitter.random.shuffle", lambda x: None)

    sessions = [PreparedSession(prepared_session_dict) for _ in range(8)]

    splitter = LearningSetSplitter()
    ls = splitter.generateLearningSets(sessions)

    assert len(ls.training_set) == 4
    assert len(ls.validation_set) == 2
    assert len(ls.test_set) == 2