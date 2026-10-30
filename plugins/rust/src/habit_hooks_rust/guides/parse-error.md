cargo could not compile the crate, so clippy never ran over it and every other lint went unchecked. Real issues in these files are currently invisible — the error is the only finding the run can make.

`cargo check` names the line and, for an `E0xxx` code, `rustc --explain E0xxx` explains it. Fix the first error first: the ones after it are often fallout from the same cause. If the build fails for a reason outside the source — an edition the installed toolchain does not know, a dependency that could not be fetched — fix the toolchain or the lockfile; the sensor reports what cargo reports.

You've fixed it when a deliberate change to a scoped file produces an ordinary clippy warning again, since that proves the lints are running. Keep the files in scope: the crate that does not compile is the one most in need of the other checks.

{% include "includes/line_level_issues.md" %}
