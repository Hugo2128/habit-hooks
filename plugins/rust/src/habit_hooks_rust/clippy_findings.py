from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

LINT_SMELLS = {
    "clippy::too_many_arguments": "too-many-parameters",
    "clippy::too_many_lines": "oversized-function",
    "clippy::cognitive_complexity": "high-complexity",
    "clippy::excessive_nesting": "deep-nesting",
    "unused_must_use": "swallowed-exception",
    "unused_variables": "unused-variable",
    "unused_imports": "unused-import",
    "dead_code": "unused-class-member",
}


def diagnostics(stdout: str) -> list[dict]:
    messages = []
    for line in stdout.splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get("reason") == "compiler-message":
            messages.append(record["message"])
    return messages


def has_errors(messages: list[dict]) -> bool:
    return any(message.get("level") == "error" for message in messages)


def primary_span(message: dict) -> dict | None:
    return next((span for span in message.get("spans", []) if span.get("is_primary")), None)


def lint_of(message: dict) -> str | None:
    code = message.get("code") or {}
    return code.get("code")


def smell_of(message: dict) -> str | None:
    if message.get("level") == "error":
        return "parse-error"
    lint = lint_of(message)
    if lint is None:
        return None
    return LINT_SMELLS.get(lint, lint)


def source_of(message: dict) -> str:
    lint = lint_of(message)
    return "clippy:" + (lint if lint is not None else message.get("level", "error"))


def issue(message: dict, span: dict, file: Path) -> dict:
    return {
        "key": str(file),
        "details": {
            "file": str(file),
            "line": span["line_start"],
            "column": span["column_start"],
            "message": message["message"],
            "source": source_of(message),
        },
    }


def issues_in(messages: list[dict], root: Path, scope: set[Path]) -> dict[str, list[dict]]:
    by_smell: dict[str, list[dict]] = defaultdict(list)
    seen: set[tuple] = set()
    for message in messages:
        span = primary_span(message)
        smell = smell_of(message)
        if span is None or smell is None:
            continue
        file = (root / span["file_name"]).resolve()
        identity = (smell, file, span["line_start"], span["column_start"], message["message"])
        if file not in scope or identity in seen:
            continue
        seen.add(identity)
        by_smell[smell].append(issue(message, span, file))
    return by_smell


def merge(into: dict[str, list[dict]], more: dict[str, list[dict]]) -> None:
    for smell, issues in more.items():
        into.setdefault(smell, []).extend(issues)


def findings_of(by_smell: dict[str, list[dict]]) -> list[dict]:
    return [
        {"smell": smell, "language": "rust", "details": {}, "issues": issues}
        for smell, issues in sorted(by_smell.items())
    ]
