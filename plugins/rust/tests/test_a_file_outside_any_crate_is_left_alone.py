from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SENSOR = Path(__file__).resolve().parents[1] / "src" / "habit_hooks_rust" / "clippy_sensor.py"


def run_sensor(project: Path, cargo: str, files: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SENSOR), cargo, "--", *files],
        cwd=project,
        capture_output=True,
        encoding="utf-8",
    )


def test_a_rust_file_with_no_manifest_above_it_yields_no_findings(tmp_path: Path) -> None:
    (tmp_path / "loose.rs").write_text("fn main() { let unused = 1; }\n", encoding="utf-8")

    result = run_sensor(tmp_path, "cargo-that-must-not-run", ["loose.rs"])

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == []


def test_only_rs_files_count_as_scope(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("[package]\nname = 'x'\n", encoding="utf-8")

    result = run_sensor(tmp_path, "cargo-that-must-not-run", ["Cargo.toml", "README.md"])

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == []
