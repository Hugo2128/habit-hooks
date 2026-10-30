from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SENSOR = Path(__file__).resolve().parents[1] / "src" / "habit_hooks_rust" / "clippy_sensor.py"

MANIFEST = '[package]\nname = "broken"\nversion = "0.1.0"\nedition = "2021"\n'


def _broken_crate(root: Path) -> None:
    (root / "src").mkdir()
    (root / "Cargo.toml").write_text(MANIFEST, encoding="utf-8")
    (root / "src" / "lib.rs").write_text("pub fn half(x: u32) -> u32 { x / 2\n", encoding="utf-8")


def test_a_syntax_error_is_reported_as_parse_error_not_a_failed_run(tmp_path: Path, cargo: str) -> None:
    _broken_crate(tmp_path)

    result = subprocess.run(
        [sys.executable, str(SENSOR), cargo, "--", "src/lib.rs"],
        cwd=tmp_path,
        capture_output=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    findings = json.loads(result.stdout)
    assert [finding["smell"] for finding in findings] == ["parse-error"]
    issue = findings[0]["issues"][0]
    assert issue["details"]["file"].endswith("src/lib.rs")
    assert issue["details"]["source"] == "clippy:error"
