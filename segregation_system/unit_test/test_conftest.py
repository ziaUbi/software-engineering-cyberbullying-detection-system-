import sys
from pathlib import Path

import pytest


# Ensure the repo root is importable during test collection.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Matplotlib must use a non-interactive backend during tests.
try:
    import matplotlib

    matplotlib.use("Agg", force=True)
except Exception:
    pass


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Absolute path to the repository root (the folder that contains segregation_system/)."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _repo_on_path_and_cwd(project_root: Path, monkeypatch: pytest.MonkeyPatch):
    """Make imports work (segregation_system.*) and keep relative paths stable."""
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    monkeypatch.chdir(project_root)
