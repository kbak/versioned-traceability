# Requirements and design

Use the shared [semantic contract](semantics.md) when interpreting existing
artifacts or proposing new ones. Keep declared coverage, claim origin, approval,
and execution evidence distinct in discussions and handoffs. When this guidance
is embedded in an agent context, the semantic contract is included alongside it.

## Standalone setup for implementation

Discussion alone does not require installing or running tooling. For authorized
implementation, use the chosen tool checkout/revision and its matching skill.
Resolve relative references there, not in the target project. Reuse a supplied
local checkout, packaged skill/runtime or inline reference when available. If an
installed vt cannot be tied to that source, install from the chosen checkout into
a fresh external environment; a version number alone does not establish a match.

The runtime needs Python 3.11+, Git, Java 17+, the portable package and the target
project's test dependencies. Keep tool checkouts and environments outside the target
project and preserve existing local work. After choosing absolute paths in
vt_checkout and vt_env:

```sh
python3 -m venv "$vt_env"
"$vt_env/bin/python" -m pip install "$vt_checkout"
"$vt_env/bin/python" -m versioned_traceability check --help
"$vt_env/bin/python" -m versioned_traceability verify --help
"$vt_env/bin/python" -m versioned_traceability install-oft
```

Reuse an existing pinned OFT JAR via VT_OFT_JAR when available. Use the same
interpreter for checks and verification, with an explicit target --repo after
setup. Prepare the project's real test runner using its instructions; installing
vt does not install those dependencies. Resolve routine setup within task
permissions and report concrete blockers. Do not change project dependency
manifests solely to install the checker or silently substitute an unavailable
requested tool revision.

An adopted baseline normally includes a committed root scope.json. Normal checks
read that file from the base commit; omit --scope to use it. Use an external
trusted scope only when the caller supplied one. A working-copy scope change
does not authorize itself. Recovery proposals require review and adoption before
the ordinary development workflow can rely on them.

## Author requirements and design

Read the trusted scope, existing requirements, and relevant repository guidance
before proposing requirements. Follow links to related documentation, code, and
tests to understand existing promises and constraints. Inspect missing context
with targeted searches and flag what remains uncertain. Trace links support a
best-effort consistency assessment; they do not prove semantic agreement.

Keep exploratory ideas, proposed requirements, agreed requirements, and open
questions distinguishable in the discussion. Formalize concrete, testable
promises when they are useful to the design; brainstorming alone does not make
a requirement agreed. Flag contradictions with existing promises and make any
proposed change explicit, including which requirement it affects.

Reuse existing OFT requirement IDs for the same promise. For a new concrete
requirement, choose a unique, stable name and initial revision following the
repository's OFT conventions. Search existing artifacts before assigning an ID.
Keep the name stable when wording changes, and follow the configured revision
policy and repository guidance when proposing a revision. Do not treat every
editorial edit as requiring an increase unless that policy requires it.

Write readable Markdown in the repository's existing style. Use its OFT artifact
types, Needs/Covers relationships, and coverage chains from the scope; do not
replace design or architecture artifacts with mandatory direct code/test links.
Identify the intended files within the configured specification paths, keeping
existing documentation locations and structure. If those paths cannot represent
the proposed work, flag the scope conflict instead of silently expanding it.

Carry agreed requirement text, IDs and revisions, acceptance criteria, intended
documentation paths, and any authorized changes to existing promises into the
implementation handoff. Keep unapproved proposals and unresolved questions
separate from agreed work. Use the caller's existing specification or task; no
separate requirements document is needed just for the handoff. Drafting does
not authorize implementation or changes to the approved scope.
