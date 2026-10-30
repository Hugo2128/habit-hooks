from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "habit_hooks_rust"

sys.path.insert(0, str(PACKAGE))


@pytest.fixture(scope="session")
def cargo() -> str:
    found = shutil.which("cargo")
    if found is None:
        pytest.skip("cargo is not on PATH")
    return found
