# Optional test-execution links

This provisional profile associates individual JUnit results with OFT test
artifacts. Humans and agents use the same fields. It needs no additional runtime
dependency in vt; the project supplies its own test runner.

## Enable for a scope

Add this object inside the existing `tests` configuration:

```json
"execution_links": {
  "format": "junit-properties-v1",
  "artifact_types": ["utest"]
}
```

This requires `tests.format: junit` (the default). Select the project's actual
verification types; `utest` is an example, not a universal requirement. Each
referenced artifact must be imported by OFT, have the exact ID and revision, and
originate within `test_paths`. The scope is approved policy just as before.

Omitting `execution_links` preserves the existing suite/command behavior,
including for old evidence bundles. Enabling the profile requires a fresh check.

## Author and report an explicit link

Give the OFT test marker an explicit name using its existing tag syntax:

```python
# [utest~expiration-boundary~1->req~session-expiration~1]
```

The corresponding JUnit case supplies that test artifact's complete ID:

```xml
<testcase classname="test_session" name="test_expiration_boundary">
  <properties>
    <property name="oft_id" value="utest~expiration-boundary~1"/>
  </properties>
</testcase>
```

The property identifies the test artifact, not the requirement. OFT maintains
the requirement relationships; the report does not duplicate them. Repeat
`oft_id` properties if one case explicitly maps to several test artifacts.
Identical repeated values are deduplicated. Suite-level properties do not map
individual cases. Empty IDs, wrong revisions, unknown or duplicate OFT IDs, IDs
outside the selected types/paths, and linked cases without names are invalid.
Invalid supplied metadata rejects the check even when the suite itself passes.

Prefer named OFT artifacts for continuity across source movement. Do not infer
links from similar names or nearby file/line locations. A report's claim that a
case corresponds to an artifact still needs the normal code/test review.

## Supported producer: pytest

The runnable [pytest session example](https://github.com/kbak/versioned-traceability/tree/main/examples/pytest-session)
uses a project-local collection hook to transfer `@pytest.mark.oft_id(...)`
markers into `item.user_properties`. Collection-time metadata survives skips,
expected failures and setup failures; adding a property inside the test body
would not cover those cases.

The collection hook is small and lives in the project's `conftest.py`:

```python
def pytest_collection_modifyitems(items):
    for item in items:
        for marker in item.iter_markers(name="oft_id"):
            for identifier in marker.args:
                item.user_properties.append(("oft_id", identifier))
```

The example selects `junit_family = xunit1`, registers the marker, and disables
the pytest cache provider. It was exercised with pytest 9.1.1. Other runners can
emit this profile, but are not thereby certified as compatible. Pytest notes
that testcase properties can fail strict JUnit schema validation in other
consumers; do not assume the extension works in every CI report viewer.

Sources: [pytest properties](https://docs.pytest.org/en/stable/how-to/output.html#record-property)
and [OFT named tags](https://github.com/itsallcode/openfasttrace/blob/4.9.0/doc/user_guide.md#optional-elements).

## Read the evidence

`evidence.json` retains the provisional schema-1 `tests.execution_links` object:

- `format`, `property`, `status` (`recorded` or `invalid`), and `diagnostics`.
- `artifacts`: selected test-artifact IDs, each with `status` and its `cases`.
- Each case retains its ancestor `suite` names, `classname`, `name`, status,
  ambiguity `diagnostics`, and outcome `details` (kind, type and message).
- `unlinked_cases`: cases without a resolved association, including invalid IDs.

The enclosing evidence binds these observations to the source and scope; its
artifact inventory hashes both the original JUnit report and OFT export.
`vt verify` and candidate `vt explain` recompute associations from those retained
inputs and reject altered or missing summaries. Tests are not rerun.

`vt explain` adds `linked_tests` and `execution_link_diagnostics` in JSON and
lists individual cases in text. It follows OFT's existing `covered_by` edges to
find selected test artifacts, including through design items. Explaining a test
artifact directly shows its own observations. `linked_test_execution` summarizes
only those artifacts:

| Status | Meaning |
| --- | --- |
| `passed` | All reported associated cases for the selected artifacts passed. |
| `failed` | All summarized outcomes are failures/errors. |
| `skipped` | All summarized outcomes are skipped, disabled or not run. |
| `not_observed` | The selected artifacts have no associated case in this report. |
| `ambiguous` | A case identity is repeated, has conflicting outcomes, or uses unsupported outcome/retry extensions. |
| `mixed` | The underlying statuses differ; inspect the per-artifact and per-case entries. |
| `not_established` | No usable association evidence, invalid metadata, unmatched source, command error, or no selected test artifact reachable from this item. |

Case identity includes suite ancestry, classname and name. Distinct parameterized
cases can map to one OFT artifact; duplicate case identities are ambiguous,
including an annotated case duplicated by an unannotated one. Recognized retry
extensions are not collapsed into a pass. A producer that hides retries cannot
be reconstructed from its final report. Only represented parameter cases are
known; this profile cannot discover an omitted parameter or prove that every
required scenario ran.

Missing observations, skips and ambiguity do not add a new execution-completeness
gate. Existing suite and skip policy still apply. Source changes or an incomplete
test command leave reported observations diagnostic; baseline explanations never
reuse candidate executions. The separate in-toto test statement still summarizes
the suite/command outcome and does not assert per-requirement verification.

A passing suite with the boundary test deselected must show `not_observed` for
that test artifact. Even a linked `passed` outcome establishes neither assertion
adequacy nor requirement satisfaction, and does not fill structural graph gaps.
