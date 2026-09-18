---
name: property-testing
description: Discover properties during onboarding; derive, maintain, and review executable properties from approved requirements during strengthening and evolution, using the project's existing test workflow.
---

During baseline recovery, use this workflow for discovery and a prioritized
handoff only: identify existing checks, candidate properties, domains and missing
evidence in the recovery capability table/claim notes. Preserve tests, generators,
dependencies and runner configuration. The authoring steps below apply to
authorized strengthening or evolution after baseline adoption; recovery success
does not approve inferred intent or authorize that transition.

Improve the maintained test suite for the selected behavior. Start from approved
requirements and their linked implementation; inferred behavior is a proposed
property until its intended meaning is established. Reuse existing test libraries,
requirements, IDs, and fixtures. Add a separate property item only when it expresses
a useful refinement, not a duplicate requirement. Ordinary example tests remain useful.

For strengthening, take selected properties from the onboarding handoff. During
evolution, follow changed obligations and implementation to their existing
properties; maintain affected assertions, generators and assumptions, adding
checks for new obligations or gaps. Preserve identities for surviving promises;
revise changed meaning through the existing requirement/review policy. Record
deferred checks and counterexamples in the same maintained documentation/tests.

For each selected property, explain its scope and assumptions in readable prose
and link an executable assertion to the same obligation. Exercise the actual
implementation. Specify generators for relevant boundaries, invalid inputs, and
operation sequences; generated valid inputs must not silently exclude promised
behavior. Pair safety constraints with required successful behavior where relevant.

Use the existing runner and one appropriate library. Read only the relevant guide:
[Hypothesis](references/python.md), [fast-check](references/typescript.md),
[QuickCheck](references/haskell.md), or [Hegel](references/hegel.md).
If an adapter supplied this text without the references, read the matching installed
file with `importlib.resources.files("versioned_traceability")` under
`skills/property-testing/references/`. No new agent service is needed.

Distinguish an implementation defect from a wrong assertion, invalid generated
input, or harness failure. Preserve the failing example before repair. Changes to
approved properties, exclusions, generators, budgets, skips, or assumptions belong
in the existing review; do not narrow them merely to obtain a pass. Use a targeted
known defect or deliberate mutation when useful to check assertion sensitivity.

Run committed tests without an LLM. Keep native replay details and turn useful
minimal failures into regression examples. Report the checked revision, method,
scope, result, and limits through the existing test/evidence flow. A property-test
pass describes a search, not a proof. Missing tests, excessive discards, timeouts,
and harness errors must remain visible. One property can exercise many inputs;
do not count those inputs as distinct requirements or proofs.

Humans can follow this same procedure without an agent. With OFT, preserve exact
requirement/test IDs and revisions and the project's existing coverage chain.
Keep property identity independent of the checking method so later runtime,
differential, schema-based, or symbolic checks can target the same obligation.
