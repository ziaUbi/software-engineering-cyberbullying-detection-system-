import pytest
from segregation_system.prepared_session import PreparedSession
from segregation_system.segregation_database import PreparedSessionDatabaseController

@pytest.fixture
def sample_session_data():
    return {
        "uuid": "test-uuid-1234",
        "label": "cyberbullying",
        "tweet_length": 10,
        "word_fuck": 1, "word_bulli": 0, "word_muslim": 0, "word_gay": 0, "word_nigger": 0, "word_rape": 0,
        "event_score": 0, "event_sending-off": 0, "event_caution": 0, "event_substitution": 0, "event_foul": 0,
        "audio_0": 0.0, "audio_1": 0.0, "audio_2": 0.0, "audio_3": 0.0, "audio_4": 0.0, 
        "audio_5": 0.0, "audio_6": 0.0, "audio_7": 0.0, "audio_8": 0.0, "audio_9": 0.0,
        "audio_10": 0.0, "audio_11": 0.0, "audio_12": 0.0, "audio_13": 0.0, "audio_14": 0.0,
        "audio_15": 0.0, "audio_16": 0.0, "audio_17": 0.0, "audio_18": 0.0, "audio_19": 0.0
    }

def test_prepared_session_initialization(sample_session_data):
    """Testa che la classe PreparedSession mappi correttamente i campi."""
    session = PreparedSession(sample_session_data)
    assert session.uuid == "test-uuid-1234"
    assert session.label == "cyberbullying"
    assert session.word_fuck == 1

def test_database_store_and_retrieve(tmp_path, sample_session_data):
    """Testa le operazioni CRUD sul database SQLite."""
    # Usa un db temporaneo
    db_path = tmp_path / "test_segregation.db"
    db = PreparedSessionDatabaseController(db_path=str(db_path))

    # Assicurati che sia vuoto all'inizio (se creato nuovo) o dopo pulizia
    db.remove_all_prepared_sessions()
    assert db.get_number_of_sessions_stored() == 0

    # Salva una sessione
    session = PreparedSession(sample_session_data)
    db.store_prepared_session(session)
    
    # Verifica conteggio
    assert db.get_number_of_sessions_stored() == 1

    # Verifica recupero dati
    sessions = db.get_all_prepared_sessions()
    assert len(sessions) == 1
    assert sessions[0]["uuid"] == sample_session_data["uuid"]
    
    # Test cancellazione
    db.remove_all_prepared_sessions()
    assert db.get_number_of_sessions_stored() == 0