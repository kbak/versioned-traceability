# Requirements and design

Use the shared [semantic contract](semantics.md), included alongside this guidance
in agent contexts. Keep coverage, origin, approval and execution evidence distinct.

Normal checks read root scope.json from the adopted baseline; omit --scope to
use it. Use external scope only when supplied by the caller. Candidate scope
edits cannot authorize themselves; recovery proposals need review and adoption.

## Author requirements and design

Read the trusted scope and relevant repository guidance. Use existing headings,
capability tables or targeted searches to locate affected requirements, then read
their full promises and acceptance criteria and follow links to code and tests.
Reuse supplied context; retrieve more only to resolve a gap. Flag uncertainty:
trace links support consistency assessment but do not prove semantic agreement.

Distinguish exploration, proposed and agreed requirements, and open questions.
Formalize concrete, testable promises when useful; brainstorming is not agreement.
For changed promises, summarize the ID, before → after behavior, reason and
affected acceptance checks in the existing task or PR. Flag contradictions and
unknown rationale instead of inventing intent. Reuse this summary in the handoff.
For authorized mid-task revisions, reconcile affected design, code and assertions
through their links; preserve work and decisions that still apply.

Reuse OFT names for continuing promises. Search before assigning a new unique
name and initial revision. Follow the project's revision policy; editorial edits
need not increase the revision unless that policy requires it.

Use existing Markdown structure, OFT types and Needs/Covers chains; preserve
design/architecture links. Put meaningful rationale and rejected alternatives
in existing task/design notes when useful. Keep intended files within the
specification paths; flag scope conflicts instead of silently expanding them.

Carry agreed text, IDs/revisions, acceptance criteria, documentation paths and
authorized promise changes into the existing handoff. Keep unapproved proposals
and unresolved questions separate. No extra document, planning pass or approval
step is required; drafting does not authorize implementation or scope changes.
