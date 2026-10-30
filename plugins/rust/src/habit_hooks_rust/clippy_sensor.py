from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from clippy_findings import diagnostics, findings_of, has_errors, issues_in, merge

OPT_IN_LINTS = (
    "clippy::too_many_lines",
    "clippy::cognitive_complexity",
    "clippy::excessive_nesting",
    "clippy::let_underscore_must_use",
)

CONFIG_NAMES = ("clippy.toml", ".clippy.toml")

SHIPPED_CONFIG_DIR = Path(__file__).resolve().parent

CLIPPY_MISSING = "no such command: `clippy`"

INSTALL_CLIPPY = "rustup component add clippy"


@dataclass(frozen=True)
class Cargo:
    executable: str
    extra_args: list[str]


def split_argv(argv: list[str]) -> tuple[list[str], list[str]]:
    if "--" not in argv:
        return argv, []
    index = len(argv) - 1 - argv[::-1].index("--")
    return argv[:index], argv[index + 1 :]


def manifest_dir_of(file: Path) -> Path | None:
    for ancestor in file.parents:
        if (ancestor / "Cargo.toml").is_file():
            return ancestor
    return None


def workspace_root(cargo: str, manifest_dir: Path) -> Path:
    located = subprocess.run(
        [cargo, "locate-project", "--workspace", "--message-format", "plain"],
        cwd=manifest_dir,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if located.returncode != 0:
        return manifest_dir
    return Path(located.stdout.strip()).parent


def workspaces_of(cargo: str, files: list[Path]) -> set[Path]:
    manifest_dirs = {dir for dir in map(manifest_dir_of, files) if dir is not None}
    return {workspace_root(cargo, dir) for dir in manifest_dirs}


def has_own_config(root: Path) -> bool:
    return any(
        (ancestor / name).is_file()
        for ancestor in (root, *root.parents)
        for name in CONFIG_NAMES
    )


def clippy_environment(root: Path) -> dict[str, str]:
    environment = dict(os.environ)
    if not has_own_config(root):
        environment["CLIPPY_CONF_DIR"] = str(SHIPPED_CONFIG_DIR)
    return environment


def lint_flags() -> list[str]:
    return [flag for lint in OPT_IN_LINTS for flag in ("-W", lint)]


def run_clippy(cargo: Cargo, root: Path) -> subprocess.CompletedProcess[str]:
    command = [cargo.executable, "clippy", "--quiet", "--workspace", "--all-targets",
               "--message-format=json", *cargo.extra_args, "--", *lint_flags()]
    return subprocess.run(
        command,
        cwd=root,
        env=clippy_environment(root),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def clippy_failed(result: subprocess.CompletedProcess[str], messages: list[dict]) -> str | None:
    if CLIPPY_MISSING in result.stderr:
        return f"cargo has no clippy component — {INSTALL_CLIPPY}\n"
    if result.returncode == 0 or has_errors(messages):
        return None
    return result.stderr or result.stdout or f"cargo clippy exited {result.returncode}\n"


def lint_workspace(cargo: Cargo, root: Path, scope: set[Path]) -> dict[str, list[dict]]:
    result = run_clippy(cargo, root)
    messages = diagnostics(result.stdout)
    failure = clippy_failed(result, messages)
    if failure is not None:
        sys.stderr.write(failure)
        sys.exit(2)
    return issues_in(messages, root, scope)


def main() -> int:
    extra, files = split_argv(sys.argv[2:])
    cargo = Cargo(sys.argv[1], extra)
    scope = {Path(file).resolve() for file in files if file.endswith(".rs")}
    by_smell: dict[str, list[dict]] = {}
    for root in sorted(workspaces_of(cargo.executable, sorted(scope))):
        merge(by_smell, lint_workspace(cargo, root, scope))
    print(json.dumps(findings_of(by_smell)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
