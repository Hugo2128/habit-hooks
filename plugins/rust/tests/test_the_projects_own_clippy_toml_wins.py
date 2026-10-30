from __future__ import annotations

from pathlib import Path

import clippy_sensor


def test_a_project_without_a_clippy_toml_gets_the_shipped_thresholds(tmp_path: Path) -> None:
    environment = clippy_sensor.clippy_environment(tmp_path)

    assert environment["CLIPPY_CONF_DIR"] == str(clippy_sensor.SHIPPED_CONFIG_DIR)


def test_a_project_with_its_own_clippy_toml_is_left_to_clippy(tmp_path: Path) -> None:
    (tmp_path / "clippy.toml").write_text("too-many-arguments-threshold = 9\n", encoding="utf-8")

    assert "CLIPPY_CONF_DIR" not in clippy_sensor.clippy_environment(tmp_path)


def test_a_dotfile_config_in_a_parent_counts_too(tmp_path: Path) -> None:
    (tmp_path / ".clippy.toml").write_text("", encoding="utf-8")
    crate = tmp_path / "crates" / "api"
    crate.mkdir(parents=True)

    assert "CLIPPY_CONF_DIR" not in clippy_sensor.clippy_environment(crate)
