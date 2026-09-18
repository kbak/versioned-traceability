# Executable properties: first-iteration acceptance

The local release candidate is **versioned-traceability 0.4.5** with
**openhands-traceability 0.2.6**. It adds a portable authoring/maintenance workflow,
framework guides and examples, maintained properties for vt itself, and an
optional gate requiring selected named test artifacts to report passing results.
Properties stay in the project's ordinary test suite. No agent service or
additional core runtime dependency is required.

## Acceptance evidence

The clean Python 3.12.3 environment installed noneditable wheels built through
their source distributions. The core suite passed **218 tests** and the adapter
suite passed **14 tests**. Packaged skills and framework references were present;
adapter tests verified their delivery through serialized OpenHands contexts.
Lint, formatting, and local GitHub workflow validation passed.

| Example | Environment exercised locally | Result and evidence level |
| --- | --- | --- |
| Python | pytest 8.4.1, Hypothesis 6.168.0 | Correct and restored versions pass; boundary mutation fails with the exact OFT test identity in JUnit. |
| JavaScript / TypeScript API | Node 24.15.0, locked fast-check dependency | Correct and restored versions pass; boundary mutation fails with native counterexample output. Command-level evidence. |
| Haskell | GHC 9.4.7, QuickCheck 2.14.3 | Correct and restored versions pass; boundary mutation fails with native counterexample output and nonzero exit. Command-level evidence. |

The smoke script also verifies the retained passing evidence. GHC and QuickCheck
were extracted into temporary storage for this validation; the system installation
and running factory were not changed. The Haskell check exposed overlapping
specification/test paths in its scope, now corrected. The source-distribution
manifest now includes JavaScript, Haskell, shell and configuration files plus
the evaluation scripts, which were previously omitted.

The existing [controlled evaluation](property-evaluation.md) detected six of six
chosen injected faults. That bounded result is separate from the language smoke
checks and is not a general mutation score.

## Fresh-agent exercise

One agent, without prior conversation context, received an isolated reservation
project, an approved requirement, installed tools and the packaged guides. The
supervisor supplied tasks and reviewed results; no factory session was used.

1. **Strengthening:** The requirement accepted requests that exactly filled
   capacity. The implementation incorrectly rejected them, and the original
   examples missed that boundary. The agent derived two linked Hypothesis
   properties, found `(capacity=1, booked=0, requested=1)`, retained explicit
   regression examples and repaired the implementation without changing intent.
   The normal check recorded three passing tests, including 200 generated
   examples per property, and left test review pending.
2. **Evolution:** After simulated fixture acceptance, the supervisor explicitly
   changed the promise to leave at least one seat free. The agent preserved the
   requirement identity at revision 2, revised affected test identities and links,
   retained boundary inputs with their newly authorized expectations, and added
   a property requiring successful reservation with exactly one free seat.
   A pre-repair check failed; the repaired proposal passed four tests, including
   200 generated examples per property, with review pending. The original domains
   and budgets were preserved. Saved evidence matched the resulting source.

The agent encountered one documentation gap: `vt explain` needs the nondefault
OFT path too. The packaged procedure now explains `VT_OFT_JAR` and `--oft-jar`.
Both phases retained failures, patches, native statistics, execution links and
version-bound evidence. This is one successful usability exercise, not a measure
of autonomous reliability or a live factory integration test.

## Maintenance and remaining boundaries

The [normal CI workflow](../.github/workflows/ci.yml) builds and tests packages and
the three examples; a [separate manual workflow](../.github/workflows/property-evaluation.yml)
runs the controlled fault experiment. These workflows were checked locally;
GitHub execution awaits pushing the commits. The adapter pins this core release's
source commit as well as its package version, so registry publication is optional
for CI. Push the core commit before running adapter CI.

Python 3.11 is included in CI but was not exercised in this local acceptance run.
Hegel remains selection guidance only. JS/Haskell per-test execution metadata,
larger autonomous evaluations, factory deployment, SMT/model-checking adapters
and stronger assurance profiles remain future work. Search budgets, assumptions,
generators and changed promises still require semantic review. Sampled passes
are not proofs, and execution links do not establish assertion adequacy.

Local artifacts are retained under `.local-validation/release-candidate/`
(ignored by Git): package archives, test logs, example evidence and fresh-agent
reports. Reproduce package and example checks using [validation](validation.md)
and the [example instructions](../examples/property-testing/README.md).
