import json
from pathlib import Path

import pytest

from segregation_system.prepared_session import PreparedSession
from segregation_system.segregation_database import PreparedSessionDatabaseController


@pytest.fixture()
def sample_prepared_session_dict(project_root: Path) -> dict:
    p = project_root / "segregation_system" / "inputs" / "prepared_session.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_prepared_session_constructor_maps_fields(sample_prepared_session_dict: dict):
    s = PreparedSession(sample_prepared_session_dict)
    assert s.uuid == sample_prepared_session_dict["uuid"]
    assert s.label == sample_prepared_session_dict["label"]
    # NOTE: schema uses 'event_sending-off'
    assert s.event_sending_off == sample_prepared_session_dict["event_sending-off"]


def test_prepared_session_to_dict_is_currently_broken(sample_prepared_session_dict: dict):
    """PreparedSession is not a @dataclass but calls dataclasses.asdict(); this should raise.

    This test documents the current behavior so failures are explicit.
    """
    s = PreparedSession(sample_prepared_session_dict)
    with pytest.raises(TypeError):
        _ = s.to_dict()


def test_sqlite_store_and_get_all(tmp_path: Path, sample_prepared_session_dict: dict):
    db_path = tmp_path / "test.db"
    db = PreparedSessionDatabaseController(db_path=str(db_path))

    s = PreparedSession(sample_prepared_session_dict)
    db.store_prepared_session(s)
    assert db.get_number_of_sessions_stored() == 1

    rows = db.get_all_prepared_sessions()
    assert isinstance(rows, list)
    assert rows[0]["uuid"] == s.uuid
    assert rows[0]["label"] == s.label

    db.remove_all_prepared_sessions()
    assert db.get_number_of_sessions_stored() == 0
