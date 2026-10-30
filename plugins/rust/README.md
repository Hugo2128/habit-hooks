# habit-hooks-rust

[Habit Hooks](https://github.com/habit-hooks/habit-hooks) turns best-practice coding advice into AI habits: it runs your linters, then replaces each raw rule violation with a short coaching guide an AI coding agent can act on. This package is its Rust plugin — the piece that knows Rust, cargo and how clippy's lints map onto those coaching guides.

## What it does

The plugin enables `habit-sensors` over a Rust project. `cargo clippy` runs over every workspace a scoped file belongs to, and each diagnostic landing on a scoped file is rewritten into a structural code smell from the [canonical vocabulary](https://github.com/habit-hooks/habit-hooks/blob/main/docs/smell-vocabulary.md): `too-many-parameters`, `oversized-function`, `high-complexity`, `deep-nesting`, `unused-variable`, `unused-import`, `unused-class-member`, `swallowed-exception` and `parse-error`. A lint with no mapping passes through under its own name rather than disappearing, and a cargo that cannot build fails the run rather than reporting clean.

Three of those lints are opt-in in clippy (`too_many_lines`, `cognitive_complexity`, `excessive_nesting`), so the sensor switches them on. Their thresholds come from your project's own `clippy.toml` when it has one; otherwise from the plugin's, which speaks earlier than stock clippy (5 arguments, 50 lines, cognitive complexity 10, nesting 6).

## Requirements

- Python 3.11+
- [cargo](https://rustup.rs/) on `PATH` with the `clippy` component (`rustup component add clippy`).

## Installation

The plugin ships as an extra of the core package:

```bash
pip install "habit-hooks[rust]"
```

Then list it in `.habit-hooks/config.toml` at the repo root:

```toml
plugins = ["rust", "generic"]
```

Extra cargo arguments — a feature set, a target — go to the sensor by name:

```toml
[sensors.clippy]
args = ["--all-features"]
```

The full walk-through — init, running, snoozing, CI — is in the [core README](https://github.com/habit-hooks/habit-hooks#readme).
