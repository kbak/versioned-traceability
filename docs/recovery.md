# Recover a baseline from an existing repository

Recovery prepares a proposed baseline from checked-in documentation, code and
tests. Requirements remain native OpenFastTrace Markdown. Extraction is performed
by a human or coding agent using the packaged recovery skill; the portable tool
does not call an LLM or claim to infer product intent automatically.

Use the shared [semantic contract](../versioned_traceability/skills/versioned-traceability/references/semantics.md)
to distinguish claim origin, authorization, and verification when reviewing a
recovered baseline. The same reference is included in recovery instructions.

## Start with your coding agent

Give the agent the [recovery skill](../versioned_traceability/skills/recover-baseline/SKILL.md)
and ask: **"Recover this repository's baseline and guide me through it."**

The agent inspects the repository, recommends an initial scope and asks about
unresolved choices, such as which subsystem to start with or whether to include
local changes. It handles prerequisites, bundle preparation, drafting and checks.
You do not need to supply commands, output paths, or a scope.json yourself.
Existing caller decisions are reused. The commands below also support manual use.

A GitHub link to the skill is enough to start when the agent has shell access to
the target project and network access for missing downloads. The skill directs it
to fetch the tool repository/ref from that link, read the matching supporting
reference and install tooling in an external Python environment. It retains the
target project path so recovery is run against the intended project. Supplied
local/package versions are reused rather than upgraded implicitly. The agent
reports concrete access or prerequisite blockers when setup cannot proceed.

## What you receive

By default, recovery leaves proposed changes in a clean Git checkout for review
in your editor or normal PR workflow. The agent summarizes the changes and
unresolved questions. An immutable original snapshot is retained separately in
both in-place and isolated modes; temporary drafting and validation directories
remain available to the agent.

| Artifact | Proposed result |
| --- | --- |
| Requirements/design Markdown | Selected documents can gain IDs, be rewritten, reorganized, consolidated, moved or removed. Useful existing structure and surviving IDs are preserved by default. |
| Implementation files | Coverage comments are added or retargeted to requirements the existing code supports. Runtime logic is preserved. |
| Test files | Coverage comments identify which requirements existing assertions check. Assertions are preserved; missing tests are recorded as gaps. |
| Scope configuration | Paths, coverage expectations and the existing test command for normal validation. |
| Evidence and review materials | Original citations, documented/inferred classifications, explanations of document changes and original ID mappings, unresolved questions, OFT/test results and a patch to inspect. |

The edits remain uncommitted and pending review. After acceptance, commit the
reviewed proposal as described below. Bug fixes and new tests are
separate development work; recovery may reveal that they are needed. Incomplete
recovery still reports its findings and gaps, but cannot establish a validated
baseline.

## Contract

1. `vt recover` captures the original source snapshot, inventories selected files
   and creates reviewable provenance records. By default the current checkout is
   the workspace; `--isolated` prepares a separate draft and leaves the original
   checkout unchanged. No model or test command runs during preparation.
2. The author annotates or restructures selected specification documents, adds
   or retargets coverage comments, supplies an ordinary scope.json, and records
   original citations, changes and unresolved questions in claims.json. Original
   snapshots, implementation behavior and test assertions are preserved.
3. `vt recover-check` validates citations against the captured original, checks
   the editing boundary, and uses the existing OFT/test checker on the assembled
   baseline. It also imports original specification IDs through OFT and requires
   explicit mappings for changed or removed requirements. It retains a proposed
   patch, source identities, documentation review, claims, and evidence.
4. A maintainer reviews the proposed promises, links, scope, and open questions.
   Successful automation always leaves recovery review pending. The caller
   establishes a real repository baseline with
   `vt check --base HEAD --candidate HEAD` after committing it.

Scope selection, resolving contradictions, and accepting promises are operational
decisions. Snapshotting, trace/test validation, citation validation, and retaining
the proposal are reusable mechanisms supplied here. No factory-specific approval
service or shared CI configuration is required.

Recovery follows the evidence order and contradiction handling in OFT's
[reverse-specification skill at 4.9.0](https://github.com/itsallcode/openfasttrace/blob/4.9.0/.agents/skills/openfasttrace-reverse-specs/SKILL.md):
user-facing documentation, existing specifications/design, tests, public code,
then internals/configuration. The bundled guidance adapts that procedure to a
bounded scope without imposing arc42 or generating redundant design layers.

## Run an experiment

Install the package and OFT using the README. From a clean local clone:

```sh
vt recover
```

This records HEAD and the current branch and checks that the index and worktree
are clean, including untracked files. Existing files must match the captured
HEAD bytes; use isolated mode for worktrees with checkout filters that change
those bytes. The tool leaves the branch, index and HEAD unchanged.

The CLI prints the retained snapshot/instructions location and creates
`.traceability/recovery/<id>/source.json` and `claims.json` in the checkout.
source.json identifies the captured original; preserve it. The author adds
source citations and unresolved questions to claims.json, adds requirements and
coverage annotations to project files, and proposes root scope.json. These are
ordinary working-tree changes. Newly created files appear in Git status/editor
source control and are not included in unstaged `git diff` until staged.

Always cite the original snapshot, even after the corresponding working file
changes. Temporary drafts are fine; put the proposed edits into the recorded
workspace before checking. Then run:

```sh
vt recover-check
```

The active recovery is discovered from Git metadata, including in linked Git
worktrees. Snapshots and raw logs are kept under the worktree's Git directory in
`versioned-traceability/recovery/`; each check creates a fresh result. They do not
appear in Git status. Use --repo to select another checkout, or --recovery to
select a retained bundle explicitly. --input on preparation selects literal
repository-relative paths; omit it to inventory the whole snapshot.

The proposed scope selects the trace graph and test command. Inspect that command
before executing a draft from an untrusted source. --scope can supply an external
proposal when existing scope.json must remain unchanged. --out can select new
storage outside the checkout, or within its tool-managed Git recovery storage.
Check output must also remain outside the source bundle itself.

Changes to the starting commit/branch, original snapshot, or durable source
record prevent a successful check. Concurrent candidate changes invalidate the
result. The tool preserves the files for inspection and never resets, stashes,
switches branches, commits, or automatically rolls back a rejected proposal.

| Exit | Meaning |
| --- | --- |
| 0 from recover | Preparation completed; no extraction or verification is claimed. |
| 4 from recover-check | OFT, tests, editing boundaries and source citations passed; baseline review remains required. |
| 1, 2, 3 from recover-check | Rejected, errored or empty proposal. Read recovery-result.json and retained diagnostics. |

Review project changes together with the durable source/claims records. The
result directory also retains proposal.patch, claims.json, normalized
provenance.json, documentation-review.json, scope.json and check/evidence.json. Full original snapshots and
raw logs should be retained as needed for the project's evidence policy.
`.traceability/recovery/` is reserved for evidence and is excluded from OFT import,
including when inputs contains `.`. Quoted historical links cannot satisfy live
coverage. Those files remain included in source identities and test snapshots.
Open issues remain in provenance and their count is shown in the result. A green
trace does not resolve an open question. Invalid proposals can retain partial
artifacts; the current recovery-result.json status governs the whole invocation.

## Restructure documentation without losing its evidence

Selected, inventoried Markdown specification documents may change in the proposal;
their originals stay in source/. Include both old and new locations in
specification_paths when moving a document. When a file is deleted, use a containing
input directory so normal OFT import does not require the deleted path to exist.
Documents outside those boundaries remain protected. Keep executable documentation
and test fixtures outside the editable specification scope.

For each substantive edit or deletion, claims.json's document_changes records the
original path, a summary, original source citations, and an author assessment of
meaning: preserved, changed or uncertain. Adding IDs/Needs metadata or editing
coverage comments alone does not require a document-change entry. New requirements
still need their ordinary claim citations. The
[authoring contract](../versioned_traceability/skills/recover-baseline/references/recovery.md)
contains the exact schema and examples; the recovery skill guides the agent through it.

OFT imports the original inventoried specification documents independently of
the proposed coverage types. Unchanged requirement identity/content is matched
automatically, including moves. Changed content or revisions, splits, merges and
removals require requirement_mappings with original ID, proposed target IDs, and a
reason. A removed obligation has an empty target list. The review report retains
the original/proposed OFT content and locations for every authored original ID in scope.
Unnamed coverage-comment IDs generated by OFT are excluded from requirement mappings;
their links still participate in graph validation. Moving those comments does not
require a requirement-migration explanation. Explicitly named coverage IDs remain
accounted for, including revision zero.
Malformed originals that OFT cannot import produce diagnostics, not a false claim
that no original requirements existed. Duplicate authored IDs in the original
specification also block recovery, even if the proposal resolves them: the current
mapping format identifies each original by ID and cannot distinguish duplicate occurrences.

Review mappings and explanations together with the diff. Neither a citation nor
a "preserved" assessment proves semantic fidelity. Preserve exceptions, thresholds,
negative requirements and must/should distinctions; flag contradictions and possible
meaning changes. Do not remove obligations or weaken tests just to make tracing
pass. Existing requirement IDs can be accounted for mechanically; completeness of
unstructured prose and non-OFT identifiers still needs an explicit human/agent
assessment. Scope exclusions must be reviewed too.

All changes remain proposals, including deliberate changes of meaning or removal.
The checker never interprets OFT item status or author notes as baseline acceptance.

## Isolated drafting

Use an isolated draft when the current checkout has unfinished work or a separate
workspace is preferred:

```sh
vt recover --isolated --repo /path/to/project --out /path/to/recovery
vt recover-check --recovery /path/to/recovery --out /path/to/recovery-result
```

The author works in recovery/draft/ and writes recovery/claims.json. HEAD is the
default source version; --candidate worktree includes existing local changes,
and a commit/ref can select another source version. Explicit storage must be
outside the original checkout. The result includes proposed/, a full copy of the
checked candidate, as well as proposal.patch. Original schema 1 bundles remain
checkable as isolated drafts.

When transferring an isolated proposal for review, check that the original
checkout still matches the recorded source, then apply only the intended patch:

```sh
git -C /path/to/project apply --check /path/to/recovery-result/proposal.patch
git -C /path/to/project apply /path/to/recovery-result/proposal.patch
```

Applying or copying draft changes into a working tree does not accept the
requirements. Patch applicability alone does not prove matching source; compare
the recorded commit and any captured local changes with the target. Preserve the
original snapshot and provenance when moving an isolated proposal.

## Accept and continue development

In-place changes are already in the checkout; do not reapply proposal.patch.
Review and resolve relevant scope/intent questions using the project's usual
process. Retain the source/claims records and review decision with the accepted
baseline, commit the reviewed changes, then validate the actual adopted commit:

```sh
vt check --repo /path/to/project --base HEAD --candidate HEAD
```

If the reviewed scope is stored separately, pass it with --scope. Recovery checks
use disposable validation commits; they cannot replace this check of the adopted
commit. Subsequent feature work uses the existing vt check / vt verify workflow.
Point the agent to the
[development skill](../versioned_traceability/skills/versioned-traceability/SKILL.md)
for those tasks. It handles standalone setup and the project's committed checking
policy; retain its reference in the project's agent instructions for later sessions.
This also avoids adding a second approval system: the caller records acceptance
through its normal review process, and the portable tool supplies evidence.

## First-version limits

This version works from a local Git checkout, including a clone from GitHub.
GitHub PRs/issues, external documents, historical intent reconstruction, and
runtime production discovery are outside extraction scope. Git commit and file
digests identify the evidence; source identity has the same exclusions as the
[normal checker](contract.md#source-identity).

Tests execute with the caller's permissions in a captured source directory;
prepare dependencies and use an isolated workspace as appropriate. Recovery
does not repair bugs or generate new tests to
make an inferred requirement pass. Such work follows baseline review.

Outside editable `.md`/`.markdown` specification documents, existing inventoried
files permit only standalone OFT coverage-comment additions, removals and replacements,
including `//` comments in `.mjs` and `.cjs` modules. All non-annotation lines and
existing file modes must remain unchanged. New files are limited to Markdown within
specification_paths, root scope.json, and the recorded source/claims files created
by in-place preparation. Existing recovery records remain unchanged.

This is a textual editing check, not proof that comments are semantically inert
inside every language construct, that Markdown is never executable, or that metadata
attaches to the intended prose.
OFT validates the resulting graph. Review annotation placement, including code
fences and multiline strings. Unsupported annotation forms require a deliberate
extension. Semantic fidelity and assertion adequacy remain review responsibilities.

A citation proves that the quoted source exists at the recorded location. It
does not prove that the source supports the proposed statement. OFT links and
suite-level test results likewise do not prove individual requirement adequacy.
Reports are unsigned and depend on the caller's custody of the recovery bundle.

Repeated recovery starts a fresh bundle; in-place preparation again requires a
clean checkout. Prior recovery records are preserved. Rechecking writes a fresh result
directory, leaving earlier proposals and outcomes intact. A source change after
capture does not update the proposal automatically; recover again or reconcile
the changes before adoption. Incomplete/failed recovery is still a useful report,
but is not an accepted baseline.
