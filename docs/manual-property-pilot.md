# Manual executable-property pilot

On 2026-09-17, we exercised recovery, property authoring, evolution and evidence
checking against vt's own JUnit processing. A human-directed assistant authored
the artifacts and invoked ordinary local commands. No OpenHands agent, factory
process, deployment or runtime configuration participated.

This validates a manual workflow and selected executable properties. It does not
measure autonomous-agent quality, prove the requirements, or approve a real
repository baseline. All adoption commits and policy changes were experiment
fixtures in an isolated repository.

## Subject and setup

The subject was an 84-file capture of the current working tree, including
unpublished changes, based on upstream commit
`8ab8f76f9d95b267d77655dfee9a58dcbd56527e`. Eight existing tests from
`tests/test_reports.py` were copied into a focused harness before recovery.
The copy retained the actual vt implementation and its dependencies.

An external, installed vt 0.4.5 controlled snapshots and evidence. Test commands
imported the captured subject's code; intentional subject mutations could not
change the controller. The minimal environment used Python 3.12.3, pytest 8.4.1,
Hypothesis 6.168.0, junitparser 5.0.3 and OpenFastTrace 4.9.0, installed from a
local wheel/cache. The controller supplied the trusted execution-link scope.

Three requirements were recovered from the existing report contract, with
citations to the original snapshot and explicit verification gaps. After simulated
adoption, three properties strengthened the original eight example tests:

- Merging preserves outcomes and the completion policy, including mixed skips.
- Suite-level errors/failures still prevent completion after merging passing cases.
- Missing cases cannot be hidden behind larger declared test counts.

The properties use bounded generators, supported suite roots, ordinary final
outcomes and unique case identities within a report. Arbitrary XML, retry dialects,
conflicting outcomes and resource limits are outside these searches. Existing
example tests remain useful. No property DSL or new evidence schema was introduced.

## Observed results

| Scenario | Result |
| --- | --- |
| Recovery preflight | `incomplete`, correctly indicating tests had not run. |
| Recovery with original tests | Eight passed; `review_required`, with original citations and a proposal patch. |
| Simulated adoption | Baseline check `passed`. |
| Add properties and named execution links | Eleven passed; `review_required`. All six explicitly linked artifacts were observed passing; five other examples were unlinked. |
| Behavior-preserving merge refactor | Eleven passed; `passed`, with properties unchanged. |
| Drop outer suite error/failure attributes during merge | One property failed; check `rejected`. The selected eight original examples still passed. |
| Narrow that property's generator to exclude wrapped reports | Eleven passed despite the mutation; `review_required` because test source changed. This is an intentional demonstration of weakening, not an accepted result. |
| Stop collecting a still-declared property | Ten passed; the omitted artifact was `not_observed`; overall `review_required`. |
| Change default skip policy without updating its promise | One property failed; check `rejected`. |
| Update that promise to revision 2, its references and executable oracle | Eleven passed; `review_required`. This hypothetical behavior change remained inside the fixture. |
| Preserve the counterexample, then repeat the mutation plus generator narrowing | The explicit regression failed; check `rejected`. |
| Restore correct implementation and full generators | Eleven passed; adding the regression still required review. |
| Verify saved evidence, then change source | Initial contents matched with review still pending; changed contents were rejected as stale evidence. |

Hypothesis shrank the injected merge defect to a wrapped report with one passed
case and one declared suite error, merged with another passing report. The native
log retained a reproduction blob. The portable regression is now an explicit
`@example(passed=1, declared=1, failure="errors", wrapped=True)` in
[the maintained tests](../tests/test_report_properties.py).

The initial successful property run observed 100 passing generated examples per
property, plus explicit examples. Native statistics also reported 7 and 41 invalid
generated cases for two strategies. These are search statistics, not JUnit case
counts or a proof. The focused eleven-test run took 0.47 seconds; the failing run
with shrinking/explanation took 1.28 seconds in this environment. These timings
exclude the controller's OFT/snapshot work and are not a performance benchmark.

No defect in the original implementation was discovered. The demonstrated defect
was deliberately injected; the comparison is against the eight selected report
examples, not a claim that the entire previous suite would miss it.

The complete development suite subsequently passed: 200 tests in 138.61 seconds,
including the three maintained properties. Ruff lint and formatting checks also
passed. Scenario outcomes and the 84 captured source-file hashes were checked
against the retained records.

## Consequences and next work

This is enough to use the workflow manually on selected critical logic now. The
three properties are ordinary maintained tests, and Hypothesis is only a test
dependency. Production behavior and defaults are unchanged.

Two limits deserve explicit attention before relying on unattended acceptance:

1. Review detects changed test files, but does not establish that an oracle or
   generator still expresses the approved promise. Review must examine domain
   narrowing and retained counterexamples.
2. Execution links disclose `not_observed`, but do not enforce a required-property
   completeness policy. An opt-in rule requiring selected linked artifacts to
   have passing observations would close this specific gap.

Follow-up: the optional `tests.execution_links.required_artifacts` gate now
implements that rule. The table above preserves the original pilot results;
the current [execution-link profile](../versioned_traceability/skills/versioned-traceability/references/execution-links.md#require-selected-artifacts-to-pass)
describes enforcement and remaining limits.

Repeating the missing-property scenario with the gate enabled rejected the check
despite ten passing tests; the intact eleven-test suite remained reviewable and
its evidence verified. The distributed Hypothesis example passed with both
properties, then rejected a run selecting only the boundary property despite
pytest returning success. Original diagnostic-only evidence still verified with
its original scope. Follow-up artifacts are retained locally in
`.local-validation/required-execution/`.
The follow-up development suite passed all 210 tests; lint and formatting checks
also passed. No factory process or configuration was changed.

The pilot needed corrections to overlapping specification/test paths and the
structured open-issue records during recovery setup. The CLI diagnosed both;
their unsuccessful outputs were retained. A small worked manual onboarding
example could reduce this setup friction without changing the core protocol.

Detailed local artifacts are under
`.local-validation/executable-properties-manual/`: `capture.json`, the fixture
repository, recovery bundle, successful and unsuccessful check directories,
native logs, JUnit, execution links, source manifests and review patches. This
directory is ignored and is not distributed with the package. The maintained
properties can be rerun independently using the [test instructions](validation.md).
