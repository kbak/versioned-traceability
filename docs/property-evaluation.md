# Snapshot, revision and evidence properties

These tests strengthen the existing [source identity, review and evidence
contract](contract.md). They use Hypothesis and ordinary Python tests. No factory,
agent, new runtime dependency, formal language or new evidence schema is needed.
Their fixtures do not approve a baseline for vt itself or change production
behavior.

## What is checked

| Contract | Executable checks | Domain and limits |
| --- | --- | --- |
| Captured bytes, paths and Git modes define source identity. | [Snapshot properties](../tests/test_snapshot_properties.py) compare real worktree, staged, committed and archive captures; edits, renames and executable-bit changes alter identity; exact restoration restores it. Timestamps and ignored untracked files do not alter identity. Tracked ignored files remain captured. | One to four regular files, up to 32 bytes each, nested/space/Unicode paths, regular/executable modes. Symlinks, submodules, filters and concurrent writers are outside these generators. Existing examples cover other supported cases. |
| Requirement meaning changes and removals remain reviewable. | [Revision properties](../tests/test_revision_properties.py) require a higher revision for changed content under the strict policy, reject decreases, retain removals, and distinguish file movement from meaning changes. Disabling the bump policy does not remove changes from review. | Synthetic records with the shape of OFT exports; up to eight requirements and bounded revisions/descriptions. These checks exercise review logic; actual graph validation stays with OFT. |
| Saved evidence must match the captured source under the same baseline and scope. | [Lifecycle properties](../tests/test_lifecycle_properties.py) run real Git, OFT, check and verify against the session fixture. A reference map of raw bytes and modes predicts whether saved evidence should match after each operation. | Sequential edit/delete/rename/chmod/stage/commit/touch/ignored-file/revision/restore/check operations; up to 12 generated steps per trace and at most two fresh checks per instance. No concurrent interleavings or external environment changes. |

The lifecycle model stores raw contents, not vt's own digest calculation. Changed
contents must reject saved evidence; restoring the tested contents must match
again. Staging or a new candidate commit with identical contents does not itself
make evidence stale when the checked baseline and trusted scope remain fixed.
Revision changes retarget the existing requirement's references, and successful
checks preserve pending review. A deterministic sequence also exercises these
transitions regardless of which generated traces are selected.

## Run normally

Install the existing test extra and pinned OFT as described in
[validation](validation.md), then run:

```sh
python -m pytest tests/test_snapshot_properties.py tests/test_revision_properties.py tests/test_lifecycle_properties.py --hypothesis-show-statistics
```

The same tests run through unittest discovery. The normal suite now includes
three snapshot properties, three revision properties, one state machine and one
fixed lifecycle regression. Settings retain bounded deterministic searches with
health checks enabled. Repeating the same search is reproducibility, not broader
coverage; future exploration should deliberately vary budgets and inputs.

## Evaluate sensitivity to controlled defects

The repository includes a small optional experiment using six fixed mutations:

```sh
python scripts/evaluate_properties.py --out .local-validation/property-evaluation-run
```

The output directory must be new. The script first checks the unmodified tests
in a disposable source copy. It then applies one isolated mutation at a time and
runs the relevant test. It retains source hashes, dependency versions, patches,
native Hypothesis diagnostics, JUnit and a JSON summary. Source files in the
working repository are never mutated. It returns nonzero if a mutation survives
or the experiment fails; timeouts, collection failures and unrelated exceptions
are not counted as detections. This is a bounded experiment, not a general
mutation-testing framework.

The initial evaluation detected all six injected defects:

| Injected defect | Observable failure |
| --- | --- |
| Omit untracked files from source capture | A created file is absent from the captured source. |
| Discard executable mode | A chmod operation incorrectly preserves source identity. |
| Hash only file data, omitting paths and modes | A rename incorrectly preserves source identity. |
| Permit changed meaning at the same revision | The revision policy fails to reject the change. |
| Hide removed requirements from review | A removed promise disappears from the review record. |
| Accept stale source evidence | Verification accepts changed contents. |

The unmodified eight-test suite passed. Native statistics observed 30 passing
generated examples for each snapshot property, 100 for each revision property,
and 12 passing state-machine examples. Three strategies also reported 1, 16 and
14 invalid generated examples respectively; none were silently counted as passes.
That run took 18.17 seconds in the local Python 3.12.3, pytest 8.4.1, Hypothesis
6.168.0, junitparser 5.0.3 and OFT 4.9.0 environment. These are local observations,
not promised timings or counts of proven claims.

Shrunk examples for path/mode changes, unchanged revisions and requirement
removal are now explicit `@example` regressions. The fixed lifecycle sequence
catches stale-evidence acceptance. Initial logs, including a corrected test
harness setup error, are retained under `.local-validation/`; detailed fault
results are under `.local-validation/lifecycle-evaluation/`. These local artifacts
are ignored by Git; the executable tests and evaluation script are maintained.

After retaining the regression examples, the evaluation was repeated in
`.local-validation/lifecycle-evaluation-regressions/`: the baseline passed and
all six injected defects still produced assertion failures. The complete
development suite passed all 218 tests in 161.36 seconds; lint and formatting
checks also passed. This step changed tests and developer documentation/tools,
not production logic or the running factory.

No original implementation bug was found in this experiment. Detecting six
chosen defects demonstrates sensitivity to those faults; it is not an estimate
of all possible bugs, a proof, or an evaluation of autonomous property authors.
Generator domains, assumptions, budgets and assertions still need semantic
review. The required-execution gate establishes that designated checks ran and
reported passing observations; it cannot establish their adequacy.
