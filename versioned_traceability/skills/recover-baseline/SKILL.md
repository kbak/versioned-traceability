---
name: recover-baseline
description: Guide baseline recovery for an existing repository, from choosing scope and preparing a draft to recovering OpenFastTrace requirements, source/test links, and evidence for review.
---

Use this for onboarding an existing project, including one with structured
requirements that need reconciliation. A request such as "Recover this repository's baseline" is enough
to start. Guide the caller through the process; do not require a prepared bundle,
CLI arguments, or knowledge of the artifact schema. Read the
[setup and bundle contract](references/recovery.md) for commands and formats.

If no bundle was supplied, identify the repository from the workspace and inspect
its documentation, source layout, test setup, and Git status. Ask for the repository
only if it cannot be identified. Honor any scope already requested. Otherwise,
recommend a practical first scope based on that inspection and ask which area
the caller wants to recover, using a small set of concrete choices. A small
project may fit one pass; explain the boundary for a larger project. A clean
checkout uses in-place recovery by default. If local work exists, offer isolated
recovery and ask whether that work should be included when the intent is unclear.
Combine unresolved choices into a short exchange and continue independent
inspection while waiting. Do not ask callers to choose flags or output paths.

Check prerequisites and run `vt recover`; it preserves the original snapshot
and chooses tool-managed storage. Use `--isolated` when a separate draft was
requested or existing work must be preserved. Do not stash or discard user work.
Resolve routine setup within the task's permissions. Read the returned
recovery.json for the mode, workspace and claims locations, then read its
inventory and original source. Reuse supplied scope/source decisions;
an automated caller that already provided them needs no intake conversation.
The caller decides which recovered promises to adopt. Recovery does not grant
approval or replace an established baseline.

The original snapshot is required in both modes. Preserve it throughout recovery,
including when using temporary files for drafting. In-place mode writes proposed
changes to the recorded checkout for normal Git review; isolated mode writes to
the bundle's draft repository. Leave the current branch and HEAD unchanged and
leave edits uncommitted. A working-tree diff is still a proposal, not acceptance.

Follow OFT's reverse-specification evidence order: user-facing documentation,
existing specifications/design, tests, public entry points, then internal code
and configuration. Extract meaningful observable behavior and constraints.
Add design items when they explain decisions; use existing OFT conventions and
avoid redundant layers. Reuse existing IDs for surviving obligations; start new
ones at revision 1. Preserve useful existing structure. Restructure where it
clarifies scattered evidence, not merely to shorten already clear requirements.

Read the bundle's original `source/` files for citations. Within selected Markdown
specification paths, add native OFT IDs and `Needs:` metadata, reorganize or rewrite
documents, and move or consolidate content when useful. Keep original paths in
specification_paths when moving/deleting documents so their IDs remain accounted
for; select a containing input directory if an old file disappears.
Record substantive edits in claims.json's document_changes with original citations,
a summary, and whether meaning is preserved, changed or uncertain. Preserve
exceptions, thresholds, negative requirements and must/should distinctions.
Do not resolve ambiguity by inventing intent or silently dropping an obligation.

Account for each original OFT ID. The checker matches unchanged identity/content
automatically, including moves. For rewrites, revisions, splits, merges or removals,
provide requirement_mappings with target IDs and reasons. A proposed removal uses
an empty target list. These explanations are pending review, not authorization to
weaken a promise. Record contradictions and possible meaning changes visibly;
never label a recovered or inferred requirement as newly approved.

Add or retarget standalone coverage comments beside the code and test assertions
that support them. Preserve all non-annotation source/test lines and existing file
modes. Capture unimplemented promises, undocumented behavior and disagreements in
claims.json. Documentation that is itself executable or used as a test fixture
must retain that behavior; keep it outside the editable specification scope.
Test names and copied documentation alone do not establish behavioral coverage.

For each selected OFT requirement/design item, record whether intent was
documented or inferred, exact original source citations, and relevant uncertainty.
Never label inferred current behavior as historically approved intent. Agreement
between generated docs, code and tests may reflect one shared mistaken assumption.
Avoid numerical confidence claims without a calibrated basis.

Prepare the proposed scope.json using the existing Versioned Traceability
scope format, including the project's real test command. The evidence inventory
is broader context; the scope selects the actual bounded trace and test policy.
For missing behavior/tests, preserve the gap and report it. Bug repairs and new
characterization tests are separate tasks, not recovery shortcuts.

Run `vt recover-check` in an active in-place workspace, or supply `--recovery`
with the bundle path. The tool chooses a fresh result directory each time.
Inspect the current invocation's result, OFT/test logs and proposal.patch. Exit 4
means automation passed but the entire proposal still needs review, including
open issues and citation meaning. Other nonzero exits cannot establish a valid
baseline. Repair draft mistakes within scope; report missing prerequisites and
unresolved contradictions without removing obligations just to obtain a pass.

Present the result in plain language: the recovered capabilities and scope,
documents added, rewritten, moved or removed, implementation/test files receiving coverage
comments, and checks that passed or failed. Explain that behavior and test
assertions are preserved; missing tests and bug fixes are follow-up work.
Highlight inferred or disputed intent, changes in meaning, removed/split/merged
obligations and unresolved gaps that need decisions. Walk through
documentation-review.json alongside the diff. Accounting for existing IDs does
not prove that every obligation in unstructured prose was recovered; state the
remaining completeness uncertainty instead of claiming exhaustive extraction.
Point to working-tree changes in in-place mode and the proposed patch in isolated
mode. Link requirements, provenance and validation results so the
caller can inspect them without navigating JSON unaided. A partial recovery
should still explain what was found and what prevents a validated baseline.

Leave adoption to the caller's existing review workflow. In-place edits already
exist in the checkout; do not apply proposal.patch over them. For an isolated
draft, transfer only the reviewed changes to the matching original source.
Retain provenance and the review decision, then validate the actual committed
baseline before normal development begins. Committing a draft alone does not
establish acceptance or activate a development policy.

This workflow is informed by OpenFastTrace's reverse-specification procedure at
4.9.0; the source and intentional differences are documented in the reference.
