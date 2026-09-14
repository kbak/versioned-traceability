# Requirements and design

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
