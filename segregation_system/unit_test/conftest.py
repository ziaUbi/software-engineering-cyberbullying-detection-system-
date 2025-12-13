import sys
import os
from pathlib import Path
import pytest
import matplotlib

# Imposta il backend di matplotlib su "Agg" per evitare errori di GUI durante i test
matplotlib.use("Agg", force=True)

# Calcola la root del progetto (salendo di 2 livelli da unit_test/conftest.py)
# Livello 0: conftest.py
# Parents[0]: unit_test
# Parents[1]: segregation_system (il modulo)
# Parents[2]: La root del repository (che contiene segregation_system)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Aggiungi la root al sys.path subito, per permettere gli import durante la "collection" dei test
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Restituisce il percorso assoluto della root del progetto."""
    return _PROJECT_ROOT

@pytest.fixture(autouse=True)
def setup_paths(project_root: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Assicura che la root del progetto sia la working directory corrente
    per coerenza con i path relativi nel codice sorgente.
    """
    monkeypatch.chdir(project_root)