rustc's `dead_code` names an item nobody reaches — a function, struct, enum variant, field or constant with no path to it from the crate's public surface or its entry point. The compiler is rarely wrong here: it sees every call, every pattern and every `use`, and it has already discounted tests and `#[cfg]`-gated code it was asked to compile.

Decide what the item was for before deleting it. Three shapes are common: a leftover from a refactor that moved the logic elsewhere (delete it, with any helper that existed only for it); a half-finished feature whose caller never arrived (finish the thread or remove it — a `TODO` is not a caller); a field written but never read, which usually means the struct carries state it does not need.

Make the item honest rather than hiding the warning. `pub` on something only this crate uses, `#[allow(dead_code)]`, or an `_` prefix all keep the dead surface and silence the one voice pointing at it. The exceptions are real and narrow: a field kept alive for a `Drop` side effect, FFI layout or serde round-tripping — there, say so where the field is declared, so the next reader does not reopen the question.

The unreachable items:

{% include "includes/line_level_issues.md" %}
