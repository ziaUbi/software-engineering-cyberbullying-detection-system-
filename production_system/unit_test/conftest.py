import sys
import os
from pathlib import Path
import pytest

# Aggiunge la root del progetto al PYTHONPATH per permettere gli import
# Assumendo che la struttura sia root/production_system/unit_test
# Dobbiamo risalire di due livelli per vedere il package "production_system"
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

@pytest.fixture
def mock_fs(mocker):
    """Mock generico per le operazioni su file system."""
    mocker.patch("pathlib.Path.open", mocker.mock_open())
    mocker.patch("pathlib.Path.mkdir")
    mocker.patch("pathlib.Path.exists", return_value=True)
    return mocker