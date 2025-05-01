import pytest
import sys
from pathlib import Path


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """
    Returns the absolute path to the project root directory.
    """
    return Path(__file__).resolve().parent
