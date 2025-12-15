import sys
import os
from pathlib import Path
import pytest
import matplotlib

matplotlib.use("Agg", force=True)

# Calculate project's root 
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Add the root to sys.path immediately to allow imports during test collection
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

@pytest.fixture(scope="session")
def project_root() -> Path:
    return _PROJECT_ROOT

@pytest.fixture(autouse=True)
def setup_paths(project_root: Path, monkeypatch: pytest.MonkeyPatch):
    """ Ensures the project root is the current working directory. """
    monkeypatch.chdir(project_root)