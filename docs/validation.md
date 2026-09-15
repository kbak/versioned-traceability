# Running the tests

From the project checkout, in a Python virtual environment with Git and Java
available:

```sh
python3 -m pip install -e '.[test]' ruff
vt install-oft
python3 -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

Tests run OFT and example test commands in temporary Git repositories. A missing
OFT JAR fails the suite. To use an existing JAR, set `VT_OFT_JAR` instead of running
`vt install-oft`.

Execution-link tests exercise the existing session fixture and a real pytest
producer. They cover parameterized cases, deselection, skips, expected failures,
setup errors, invalid IDs/revisions, duplicate identities, unsupported retry
extensions, source mutation, and altered retained summaries. A passing suite
with an omitted linked test must report `not_observed`. The `test` extra installs
pytest only for development; it is not a vt runtime dependency.

Recovery tests start with an unannotated project, exercise citation and editing
checks, run real OFT/test validation, apply the proposed patch in the fixture,
establish the adopted baseline, and check a subsequent change. They also cover
invented/missing citations, unresolved intent, behavior/document changes, missing
links/tools, failing existing tests and concurrent edits. Compatibility tests
cover JavaScript module annotations and adding OFT IDs/Needs to existing specification
prose while retaining original citations. Documentation tests cover cited rewrites,
moves/deletions and adoption, original ID accounting, revisions, splits, merges and
removals in both recovery modes. They reject undocumented changes, fabricated citations,
test assertion edits and weakened coverage floors. Actual semantic extraction quality
is not established by these deterministic fixtures.
Coverage-comment movement tests verify that generated IDs do not require mappings,
while explicitly named IDs remain accounted for. Duplicate original authored IDs
are exercised as a currently unsupported recovery case.
In-place tests cover reviewable checkout edits, retained originals/provenance,
dirty/staged/untracked work, branch and commit changes, concurrent edits, linked
Git worktrees, automatic storage discovery, schema 1 compatibility, and exclusion
of quoted historical annotations from live coverage. Both modes exercise adoption
and subsequent development. They do not measure LLM extraction quality; use the
OpenHands recovery example for that experiment.
