"""Pytest configuration and shared fixtures."""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def data_dir():
    """Fixture for data directory path."""
    return project_root / "data"


@pytest.fixture
def output_dir():
    """Fixture for output directory path."""
    return project_root / "outputs"


@pytest.fixture
def scripts_dir():
    """Fixture for scripts directory path."""
    return project_root / "scripts"
