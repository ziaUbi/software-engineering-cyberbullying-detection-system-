import os
import sys


def pytest_configure():
    """Ensure `development_system` can be imported during tests."""
    here = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(here, ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
