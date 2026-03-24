"""Pytest fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def tmp_path_fixture(tmp_path: Path) -> Path:
    """临时目录 fixture."""
    return tmp_path
