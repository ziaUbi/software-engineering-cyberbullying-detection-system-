import pytest
import os
import sys
import json
from unittest.mock import MagicMock, patch, mock_open

# --- INIZIO MODIFICA ---
# 1. Ottieni il percorso assoluto della cartella in cui si trova questo file (es. .../progetto/testUnit)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Ottieni la cartella genitore (es. .../progetto), dove risiede 'ingestion_system'
project_root = os.path.dirname(current_dir)

# 3. Aggiungi la root al path di sistema in modo che Python possa trovare i moduli
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- FINE MODIFICA ---

# Ora gli import funzioneranno correttamente
from ingestion_system.json_handler import JsonHandler
from ingestion_system.record_buffer import RecordBufferController
from ingestion_system.record_sufficiency_checker import RecordSufficiencyChecker
from ingestion_system.raw_session_creator import RawSessionCreator
from ingestion_system.raw_session import RawSession
from ingestion_system.ingestion_configuration import Parameters