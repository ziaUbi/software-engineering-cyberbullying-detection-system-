import pytest
import os
import sys
from unittest.mock import MagicMock, patch, mock_open

# Import dei moduli del sistema
from ingestion_system.json_handler import JsonHandler
from ingestion_system.record_buffer import RecordBufferController
from ingestion_system.record_sufficiency_checker import RecordSufficiencyChecker
from ingestion_system.raw_session_creator import RawSessionCreator
from ingestion_system.raw_session import RawSession
from ingestion_system.ingestion_configuration import Parameters

# ==========================================
# 1. FIXTURES (Configurazione Comune)
# ==========================================

@pytest.fixture
def json_handler():
    """Restituisce un'istanza pulita di JsonHandler"""
    return JsonHandler()

@pytest.fixture
def buffer_controller():
    """
    Restituisce un controller connesso a un DB in memoria.
    Viene chiuso automaticamente alla fine del test.
    """
    with patch("ingestion_system.record_buffer.DATABASE_FILE_PATH", ":memory:"):
        controller = RecordBufferController()
        yield controller
        controller.close()

@pytest.fixture
def mock_buffer():
    """Mock del buffer per testare il checker isolatamente"""
    return MagicMock(spec=RecordBufferController)

@pytest.fixture
def sufficiency_checker(mock_buffer):
    """Istanza del checker che usa il mock del buffer"""
    return RecordSufficiencyChecker(mock_buffer)

@pytest.fixture
def mock_config():
    """Mock della configurazione"""
    config = MagicMock(spec=Parameters)
    config.configuration = {"maxNumMissingSamples": 2}
    return config

@pytest.fixture
def raw_session_creator(mock_config):
    """Istanza del creator che usa il mock della config"""
    return RawSessionCreator(mock_config)


# ==========================================
# 2. TEST: JsonHandler
# ==========================================

def test_read_json_file_success(json_handler):
    mock_data = '{"key": "value"}'
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = json_handler.read_json_file("dummy.json")
        assert result == {"key": "value"}

def test_read_json_file_error(json_handler):
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = json_handler.read_json_file("non_existent.json")
        assert result is None

def test_validate_json_valid(json_handler):
    mock_schema = '{"type": "object"}'
    with patch("builtins.open", mock_open(read_data=mock_schema)), \
         patch("ingestion_system.json_handler.jsonschema.validate") as mock_validate:
        
        result = json_handler.validate_json({"a": 1}, "schema.json")
        assert result is True
        mock_validate.assert_called()

def test_save_base64_audio_to_file(tmp_path):
    # Simuliamo una stringa base64 (header + dati)
    b64_str = "data:audio/wav;base64,UklGRi4AAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQcAAAAAAA=="
    
    # tmp_path è una fixture nativa di pytest che crea una cartella temporanea
    output_dir = tmp_path / "out"
    
    with patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open()) as mock_file, \
         patch("uuid.uuid4", return_value="test-uuid"):
        
        # Passiamo il path temporaneo come stringa
        path = JsonHandler.save_base64_audio_to_file(b64_str, str(output_dir))
        
        # Verifica che il nome file contenga l'UUID generato
        assert "test-uuid.wav" in path
        
        # Costruiamo il path atteso in modo agnostico rispetto al sistema operativo
        expected_path = os.path.join(str(output_dir), "test-uuid.wav")
        
        # Verifica che open sia stato chiamato con 'wb' (write binary) sul path corretto
        mock_file.assert_called_with(os.path.abspath(expected_path), "wb")


# ==========================================
# 3. TEST: RecordBufferController
# ==========================================

def test_store_and_get_record(buffer_controller):
    uuid = "123-abc"
    
    # 1. Salvataggio Tweet (crea la riga)
    record_tweet = {
        "source": "tweet",
        "value": {"uuid": uuid, "tweet": "Hello Pytest"}
    }
    buffer_controller.store_record(record_tweet)
    
    # 2. Salvataggio Audio (aggiorna la riga esistente)
    record_audio = {
        "source": "audio",
        "value": {"uuid": uuid, "file_path": "/tmp/audio.wav"}
    }
    buffer_controller.store_record(record_audio)

    # Recupero
    records = buffer_controller.get_records(uuid)
    
    # records format: [uuid, tweet, audio, events, label]
    assert records[0] == uuid
    assert records[1] == "Hello Pytest"      # Tweet presente
    assert records[2] == "/tmp/audio.wav"    # Audio presente
    assert records[3] is None                # Events ancora vuoto

def test_remove_records(buffer_controller):
    uuid = "delete-me"
    record = {"source": "label", "value": {"uuid": uuid, "label": "bullying"}}
    buffer_controller.store_record(record)
    
    # Verifica che esista
    assert len(buffer_controller.get_records(uuid)) > 0
    
    # Cancellazione
    buffer_controller.remove_records(uuid)
    
    # Verifica che sia vuoto
    result = buffer_controller.get_records(uuid)
    assert result == []


# ==========================================
# 4. TEST: RecordSufficiencyChecker
# ==========================================

def test_insufficient_records_basic(sufficiency_checker, mock_buffer):
    uuid = "test-uuid"
    # Il buffer restituisce [uuid, None, None, None, None] -> Tutto mancante
    mock_buffer.get_records.return_value = [uuid, None, None, None, None]
    
    result = sufficiency_checker.are_records_sufficient(uuid, "development")
    assert result is False

def test_sufficient_development_mode(sufficiency_checker, mock_buffer):
    uuid = "test-uuid"
    # In development serve TUTTO (Tweet, Audio, Events, Label)
    mock_buffer.get_records.return_value = [
        uuid, "text", "path.wav", ["ev1"], "label_val"
    ]
    
    result = sufficiency_checker.are_records_sufficient(uuid, "development")
    assert result is True

def test_insufficient_development_missing_label(sufficiency_checker, mock_buffer):
    uuid = "test-uuid"
    # Manca la label (ultimo elemento None)
    mock_buffer.get_records.return_value = [
        uuid, "text", "path.wav", ["ev1"], None
    ]
    
    # In development deve fallire senza label
    result = sufficiency_checker.are_records_sufficient(uuid, "development")
    assert result is False

def test_sufficient_production_mode(sufficiency_checker, mock_buffer):
    uuid = "test-uuid"
    # In production la label NON serve
    mock_buffer.get_records.return_value = [
        uuid, "text", "path.wav", ["ev1"], None
    ]
    
    result = sufficiency_checker.are_records_sufficient(uuid, "production")
    assert result is True


# ==========================================
# 5. TEST: RawSessionCreator
# ==========================================

def test_create_raw_session(raw_session_creator):
    # Input simulato dal buffer
    records = ["uuid-1", "tweet text", "audio.wav", ["foul"], "cyberbullying"]
    
    session = raw_session_creator.create_raw_session(records)
    
    assert isinstance(session, RawSession)
    assert session.uuid == "uuid-1"
    assert session.tweet == "tweet text"
    assert session.label == "cyberbullying"

def test_mark_missing_samples_valid(raw_session_creator):
    # Eventi misti: alcuni validi, altri invalidi
    events = ["foul", "INVALID_ONE", "score", 999] 
    
    session = RawSession(uuid="1", events=events)
    
    is_valid, processed_session = raw_session_creator.mark_missing_samples(session, "PLACEHOLDER")
    
    # Verifica sostituzione invalidi
    assert processed_session.events[1] == "PLACEHOLDER"
    assert processed_session.events[3] == "PLACEHOLDER"
    
    # Verifica mantenimento validi
    assert processed_session.events[0] == "foul"
    
    # 2 errori <= 2 permessi (config mockata) -> True
    assert is_valid is True

def test_mark_missing_samples_invalid_too_many_errors(raw_session_creator, mock_config):
    # Sovrascriviamo la config per questo specifico test (più severa)
    mock_config.configuration = {"maxNumMissingSamples": 0}
    
    events = ["invalid_event", "foul"] # 1 errore presente
    session = RawSession(uuid="1", events=events)
    
    is_valid, _ = raw_session_creator.mark_missing_samples(session, "None")
    
    # 1 errore > 0 permessi -> False
    assert is_valid is False