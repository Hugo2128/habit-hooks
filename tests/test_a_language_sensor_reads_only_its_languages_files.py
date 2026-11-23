from __future__ import annotations

from pathlib import Path

from habit_hooks.scope import Scope
from habit_hooks.sensors.execution import Execution
from habit_hooks.sensors.model import Part
from plugin_fixture import loader_for, write_plugin, write_project_config

SCOPE = ["app/main.py", "app/lib.rs", "web/index.ts"]


def _sensor_reading(name: str) -> str:
    return f'sensors = [{{ name = "{name}", tool = "${{python}}", args = ["-c", "", "${{files}}"] }}]'


def _plugin(project_dir: Path, name: str, config: str) -> None:
    write_plugin(project_dir, name, {"config.toml": config})


def _python_and_rust(project_dir: Path) -> None:
    _plugin(project_dir, "py", f'language = "python"\nfiles = ["**/*.py"]\n{_sensor_reading("lint-py")}\n')
    _plugin(project_dir, "rs", f'language = "rust"\nfiles = ["**/*.rs"]\n{_sensor_reading("lint-rs")}\n')


def _sensor(project_dir: Path, plugin: str) -> Part:
    return loader_for(project_dir).load_plugin(plugin).sensors[0]


def _scoped(project_dir: Path, sensor: Part) -> list[str]:
    return Execution(project_dir=project_dir, scope=Scope(files=SCOPE)).scoped_files(sensor)


def test_two_language_plugins_each_see_only_their_own_files(tmp_path: Path) -> None:
    write_project_config(tmp_path, 'plugins = ["py", "rs"]')
    _python_and_rust(tmp_path)

    assert _scoped(tmp_path, _sensor(tmp_path, "py")) == ["app/main.py"]
    assert _scoped(tmp_path, _sensor(tmp_path, "rs")) == ["app/lib.rs"]


def test_a_project_naming_its_own_files_still_keeps_languages_apart(tmp_path: Path) -> None:
    write_project_config(tmp_path, 'plugins = ["py", "rs"]\nfiles = ["**"]\n')
    _python_and_rust(tmp_path)

    assert _scoped(tmp_path, _sensor(tmp_path, "py")) == ["app/main.py"]
    assert _scoped(tmp_path, _sensor(tmp_path, "rs")) == ["app/lib.rs"]


def test_a_sensor_naming_its_own_files_keeps_them(tmp_path: Path) -> None:
    write_project_config(tmp_path, 'plugins = ["py", "rs"]\n[sensors.lint-py]\nfiles = ["web/**"]\n')
    _python_and_rust(tmp_path)

    assert _scoped(tmp_path, _sensor(tmp_path, "py")) == ["web/index.ts"]


def test_a_plugin_with_no_language_sees_the_whole_scope(tmp_path: Path) -> None:
    write_project_config(tmp_path, 'plugins = ["any"]')
    _plugin(tmp_path, "any", f'files = ["app/**"]\n{_sensor_reading("count")}\n')

    assert _scoped(tmp_path, _sensor(tmp_path, "any")) == SCOPE


def test_a_sensor_reading_the_whole_project_stays_whole(tmp_path: Path) -> None:
    write_project_config(tmp_path, 'plugins = ["py"]')
    _plugin(tmp_path, "py", 'language = "python"\nfiles = ["**/*.py"]\nsensors = [{ name = "deps", tool = "${python}", args = ["-c", ""] }]\n')

    sensor = _sensor(tmp_path, "py")

    assert sensor.files is None
    assert Execution(project_dir=tmp_path, scope=Scope(files=[])).whole_project(sensor)
