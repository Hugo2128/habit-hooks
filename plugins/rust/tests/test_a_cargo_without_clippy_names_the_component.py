from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

SENSOR = Path(__file__).resolve().parents[1] / "src" / "habit_hooks_rust" / "clippy_sensor.py"

MANIFEST = '[package]\nname = "x"\nversion = "0.1.0"\n'


def _cargo_without_clippy(bin_dir: Path) -> Path:
    bin_dir.mkdir()
    stub = bin_dir / "cargo"
    stub.write_text(
        "#!/bin/sh\n"
        'case "$1" in\n'
        '  locate-project) echo "$PWD/Cargo.toml";;\n'
        '  clippy) echo "error: no such command: \\`clippy\\`" >&2; exit 101;;\n'
        "esac\n",
        encoding="utf-8",
    )
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    return stub


@pytest.mark.skipif(os.name == "nt", reason="the stub is a POSIX shell script")
def test_the_failure_names_the_rustup_component(tmp_path: Path) -> None:
    cargo = _cargo_without_clippy(tmp_path / "bin")
    (tmp_path / "Cargo.toml").write_text(MANIFEST, encoding="utf-8")
    (tmp_path / "lib.rs").write_text("", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SENSOR), str(cargo), "--", "lib.rs"],
        cwd=tmp_path,
        capture_output=True,
        encoding="utf-8",
    )

    assert result.returncode == 2
    assert "rustup component add clippy" in result.stderr
    assert result.stdout == ""
