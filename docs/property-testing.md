# Executable properties

A property states a rule that should hold across a defined set of inputs or
states. For example, a session must be expired whenever its idle time is at least
30 minutes. A property test generates inputs and searches for cases that violate
the rule.

Use property tests for selected requirements where broader input coverage is
valuable. Keep the assertions and generators in the project's normal test suite.
They run without vt, OFT, an agent, or a factory. Use OFT references to connect
tests to requirements; vt records results tied to the checked source.

Give an agent the packaged [property-testing skill](../versioned_traceability/skills/property-testing/SKILL.md),
or follow it manually. For example: "Add property tests for these scheduling
requirements using the existing test workflow. Preserve their meaning and retain
regression examples for any defects found." The skill reuses existing IDs and
does not require another requirements document or approval stage.

## When to add and update properties

When [documenting an existing project](recovery.md), identify existing properties
and valuable missing checks. Record the source of each proposed rule, its input
domain, assumptions, and existing tests in the requirements or claim notes.
Preserve executable tests and dependencies during that initial documentation step.

After the starting requirements are reviewed, add selected property tests using
the project's runner. Check the changes with `vt check` against that baseline.
This can continue the same task when test work is already authorized; unresolved
intent still needs a decision through the project's normal review process.

When behavior changes, update affected assertions, generators, and assumptions.
Add properties for new requirements or uncovered behavior, and keep useful
counterexamples as regression tests. Changes to a requirement's meaning follow
the existing revision and review policy. A human or agent writes these tests;
the tools supply guidance and record check results.

## Describe the property and link its tests

Keep the promise separate from how it is checked. A precise existing requirement
can be linked directly to a named test. When a derived property adds useful
detail, use the project's OFT artifact conventions (custom types are supported),
link it to the requirement, and link its tests to it. Do not duplicate every
requirement in a mandatory property layer.

The smallest useful property description states its behavior, domain, and
assumptions in Markdown beside its identity. Executable predicates, generators,
and harnesses live in the test suite and participate in the existing review.
Later runtime assertions, differential tests, schema checks, or symbolic analysis
can target the same identity with their own methods and evidence limits.

Use native JUnit or command results through the existing scope. Python can also
use the optional [per-test execution links](../versioned_traceability/skills/versioned-traceability/references/execution-links.md).
One reported property case may execute many generated examples; the JUnit case
count is not an input count or a proof count. Preserve native diagnostics, observed
statistics when available, tool versions and replay details.

Scope assumptions, exclusions, generator distributions, and test budgets affect
what was exercised. Review meaningful changes to them. A passing search does not
establish a universal claim; an absent, skipped, invalid, or timed-out check does
not become passing evidence. To require observations for critical checks,
set `tests.execution_links.required_artifacts` to their named OFT keys, such as
`["utest~expiration-boundary"]`. For each required key, the checker requires
exactly one imported revision and reported passing results. Missing declarations or results, skips, and ambiguous
revisions fail the check. Other linked test results are reported without this
additional requirement. This detects absent artifacts; it cannot detect missing
generated inputs or weakened generators.
The [execution-link reference](../versioned_traceability/skills/versioned-traceability/references/execution-links.md#require-selected-artifacts-to-pass)
defines the policy and its limits.

## Choosing a library

Use Hypothesis for Python, fast-check for JS/TS, and QuickCheck for Haskell when
the project has no established choice. Read only the corresponding skill
reference. Hegel is an optional shared engine with language-specific bindings;
its current beta/platform requirements are documented in the Hegel reference.
There is no requirement to install every framework in a project or factory image.

The [runnable examples](../examples/property-testing/README.md) use the same small
expiration obligation in the three language environments. The Python example
demonstrates individual OFT execution links; the other examples intentionally
use command-level evidence until a per-case metadata producer is validated.

## Checking property quality

Check that each property exercises the promised boundaries and detects a known
defect or deliberate mutation. Preserve useful failing inputs as regression
examples. Review generators, assumptions and budgets alongside assertions;
passing execution alone does not establish that a property is adequate.
