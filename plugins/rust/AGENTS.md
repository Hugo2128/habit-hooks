# habit-hooks-rust notes

## Gotchas

### Clippy lints a crate, not a file list

Every other wrapped tool takes `${files}`. `cargo clippy` takes a manifest, compiles the crate graph and reports on whatever it compiled, so the sensor cannot narrow the run — it narrows the result. `clippy_sensor.py` walks each scoped file up to its nearest `Cargo.toml`, asks `cargo locate-project --workspace` which workspace that crate belongs to, runs clippy once per workspace with `--workspace --all-targets`, and keeps a diagnostic only when its primary span resolves to a scoped file. A `.rs` file with no `Cargo.toml` above it is not part of any crate and is left alone; cargo has nothing to say about it.

`--all-targets` means a lint on a function used by both the lib and its tests can be reported twice, once per compilation. The sensor dedupes on (smell, file, line, column, message).

### Clippy prints one JSON object per line, and the framework reads one document

`--message-format=json` is NDJSON: `compiler-message`, `compiler-artifact`, `build-finished`, one per line. `sensors/inline_run.py` does `json.loads(stdout)` on the whole thing, so a bare `tool = "cargo"` recipe with a jq transform cannot work. The Python wrapper reads the lines itself and prints a single findings array. Keep the wrapper; do not try to move the mapping into a `.jq` file.

### An error is a finding, not a failed run

Clippy exits 101 when the crate does not compile. A syntax error is exactly what `parse-error` is for, so the sensor treats every `level: "error"` diagnostic as that smell and does not fail the run on exit 101 as long as error diagnostics were read. Exit 101 with no diagnostics at all — a missing `Cargo.lock` dependency the proxy would not fetch, a broken toolchain — is a failed run carrying cargo's stderr. `no such command: clippy` is special-cased into the one-line install hint, because stock cargo without the rustup component says only that.

### `CLIPPY_CONF_DIR` is set only when the project has no config

Lint *levels* cannot live in `clippy.toml`, so the opt-in lints are switched on with `-W` on the command line. Their *thresholds* can only live in `clippy.toml`, and clippy finds that file by walking up from `CLIPPY_CONF_DIR`, else the manifest directory. The sensor sets `CLIPPY_CONF_DIR` to the plugin's directory only when no `clippy.toml` / `.clippy.toml` exists in the workspace root or any ancestor, so a project's own thresholds always win and the shipped ones apply only to a project that never chose any. A project with its own `clippy.toml` and no `excessive-nesting-threshold` gets no nesting coaching: that is clippy's rule (threshold 0 = off), reproduced, per the precedence rule in the root `AGENTS.md`.

Trailing `-- -W` flags outrank a `[lints.clippy]` table in `Cargo.toml` but not a `#![allow(...)]` attribute in source. A project that wants one of the opt-in lints silenced says so in the crate root attribute, as it would for any other lint.

### The default lint groups pass through

`clippy::all` is on by default and has hundreds of style lints (`collapsible_if`, `needless_return`, …). Those have no smell and pass through under their own name, where `uncoached` catches them — the same rule as every other plugin. It makes a first run on an unlinted crate loud. That is clippy's own verdict on the crate, and the project tunes it where clippy is tuned, not in habit-hooks.

### The build goes to the project's `target/`

The sensor uses the project's default target directory, so an incremental build is reused and a consumer's second run is fast. The `-W` flags are part of cargo's fingerprint for workspace members, so alternating `cargo clippy` by hand with a habit-hooks run relints the workspace crates each time (dependencies are not touched). A separate `CARGO_TARGET_DIR` would avoid that at the cost of a second full build tree on disk; the fingerprint churn was judged the cheaper of the two.

## Testing

Clippy behaviour is gated by `scenarios/clippy/` — the approved-output scenario runs the real tool over a sample crate, so a clippy upgrade that reword a message fails there. A machine without cargo skips the scenario visibly. The sample is a dependency-free crate, so the scenario needs no network; cargo writes `Cargo.lock` and `target/` into the staged copy, never into the plugin tree.

### clippy's `cognitive_complexity` is McCabe with early returns forgiven

The lint is in clippy's nursery group and its score is not Sonar's cognitive complexity. Reading `clippy_lints/src/cognitive_complexity.rs`: the score starts at 1, adds 1 per `if` and per `match` with more than one arm (plus 1 per guarded arm), and then subtracts the early `return`s — all of them for a function returning `Result`, half otherwise. Loops, `&&`/`||` and nesting depth add nothing; closures are not walked. So it is roughly cyclomatic complexity that rewards guard clauses, and the shipped threshold of 10 matches the python plugin's `C901` limit rather than clippy's default of 25, which almost nothing reaches. Nesting depth is `excessive_nesting`'s job. A sensor that measures complexity the way Sonar does needs its own parser; that is the tree-sitter idea, not a clippy flag.
