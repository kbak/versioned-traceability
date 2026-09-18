# Executable properties

Use property tests to strengthen selected requirements with repeatable searches
for counterexamples. Tests remain ordinary project source files and run without
vt, OFT, an agent, or a factory. The project's runner supplies its own testing
library; vt adds traceability and revision-bound evidence.

Give an agent the packaged [property-testing skill](../versioned_traceability/skills/property-testing/SKILL.md),
or follow it manually. For example: "Add property tests for these scheduling
requirements using the existing test workflow. Preserve their meaning and retain
regression examples for any defects found." The skill reuses existing IDs and
does not require another requirements document or approval stage.

## Onboarding and evolution

Both recovery bundles and OpenHands recovery contexts carry this workflow.
Onboarding first discovers existing properties and candidate invariants, keeping
their origins, domains, assumptions and missing checks in the existing capability
table or claim notes. Recovery preserves executable tests and dependencies;
proposed checks do not supply historical evidence or approval.

Once the caller has adopted the baseline, an authorized strengthening task takes
the prioritized handoff and adds the selected checks. Use the project's ordinary
runner and `vt check` against that baseline. Reuse existing authorization to
continue rather than adding another approval stage; unresolved intent still
needs the caller's decision. A request limited to recovery produces a handoff.

During evolution, follow affected obligations and implementation to their
properties. Maintain assertions, generators and assumptions; add checks for new
obligations or gaps, and preserve counterexamples as regressions. Meaning changes
use the existing revision and review policy. The tools deliver instructions and
check evidence; they do not automatically generate properties without an author.

## Property, check, and evidence

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
use the optional [execution-link profile](../versioned_traceability/skills/versioned-traceability/references/execution-links.md).
One reported property case may execute many generated examples; the JUnit case
count is not an input count or a proof count. Preserve native diagnostics, observed
statistics when available, tool versions and replay details.

Scope assumptions, exclusions, generator distributions, and test budgets affect
what was exercised. Review meaningful changes to them. A passing search does not
establish a universal claim; an absent, skipped, invalid, or timed-out check does
not become passing evidence. To require observations for critical checks,
set `tests.execution_links.required_artifacts` to their named OFT keys, such as
`["utest~expiration-boundary"]`. The gate requires one imported revision per key
and passing observations for it; missing declarations, missing observations,
skips and ambiguity reject the check. Other linked artifacts remain diagnostic.
This detects absent artifacts, not missing generated inputs or weakened generators.
The [execution-link profile](../versioned_traceability/skills/versioned-traceability/references/execution-links.md#require-selected-artifacts-to-pass)
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
