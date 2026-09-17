---
name: versioned-traceability
description: Draft requirements or implement and review a task with OpenFastTrace, using the supplied scope and baseline to follow linked documentation, code, tests, and evidence.
---

Use the [semantic contract](references/semantics.md) from the matching tool
package or the copy included in context. Apply its distinctions in the existing
task summary; no separate report is required. For design discussions or changes
to requirements, use [requirements guidance](references/requirements.md).
Discussion does not authorize implementation.

## Task context

Reuse supplied instructions, requirement context, and matching local/package/factory
tooling. Read missing context as needed; do not reread supplied text merely to
follow this workflow. Honor pinned revisions and preserve local changes.
If tooling is missing, follow the standalone setup in the requirements guidance.

Retain the target repository's absolute path. Use the supplied scope and baseline;
in standalone use, the CLI defaults to the repository's adopted scope.json and
merge base with the locally known default branch (HEAD on that branch or detached
HEAD). Use an explicit baseline for work based on another feature/release branch.
Ask only about unresolved task or scope decisions. Without an adopted baseline,
guide the caller to recover-baseline and acceptance; ordinary development does
not repeat recovery. Candidate scope edits cannot authorize their own policy.

Read the affected promises and follow their links to implementation and test
assertions, including existing design/architecture chains. When saved evidence
is available, assemble missing context for several known IDs in one query:

```sh
vt explain 'req~first~1' 'req~second~1' --compact --evidence /path/to/check/evidence.json
```

This loads one graph, shares metadata and deduplicates linked locations. Use
`--format json` for complete structured IDs or `--snapshot base` for historical
items. It describes the saved snapshot without rerunning tests; it does not
establish that current files match or that all affected behavior was selected.
Follow indirect links or use targeted searches when context is missing. Query
again when it resolves a concrete gap; a final explain call is not mandatory.

## Implementation and review

Keep IDs beside the relevant behavior and assertions; follow the scope's coverage
and revision policy. Do not weaken promises or remove obligations to hide failures.
Keep prose and test edits visible. Authorized edits can proceed without another
confirmation; conflicts with approved requirements need a decision through the
caller's question or review process. Candidate approval files grant no authority.

Review the full candidate Git diff, including new files, and related unchanged
promises, code and assertions. Compare their meaning: does the implementation
satisfy the promise, and do tests check the affected behavior and boundary cases?
Code-only changes need this assessment too. Use focused source reads around the
links; avoid overlapping rereads or fixed small pages that fragment the review.
After a repair, inspect its delta and affected relationships; repeat a full
review if the repair changes the scope or invalidates earlier conclusions.

This is best-effort consistency review. In the existing task summary, state what
you checked and flag contradictions, suspected gaps, proposed promise changes
and uncertainty with requirement IDs and file references. Passing structural
checks do not establish semantic agreement or assertion adequacy.

## Check and handoff

Run the configured check on the completed candidate and again after repairs:

```sh
vt check --repo /path/to/repo
```

Use explicit task inputs when supplied:

```sh
vt check --repo /path/to/repo --scope /path/to/trusted-scope.json \
  --base BASE_COMMIT --candidate worktree --out /path/to/new-evidence
```

`python -m versioned_traceability` is equivalent. The runtime requires Git,
Java, OFT and the project's test dependencies. Each output directory must be new
and outside the repository. Retain the actual baseline commit, exit code and
complete bundle. Start with the printed status, counts, diagnostics and artifact
paths. Open detailed logs/reports for failures or unresolved questions; success
does not require dumping every retained artifact into context. The check already
runs the configured tests; repeat them separately only for a concrete need.

Inspect required changes in review.json. review.patch contains specification/test
changes, not the full candidate diff; it need not duplicate a review already
covering those edits. Exit 0 passes automation; exit 4 leaves specification/test
review pending. Other exits cannot establish completion. Repair in-scope failures;
report prerequisite or baseline defects without bypassing policy. Changed source
requires a fresh check; an earlier passing bundle cannot replace a failed run.

Suite success does not establish execution of each linked test. With the optional
[execution-link profile](references/execution-links.md), preserve missing, skipped
and ambiguous observations. A reported passing execution is not proof of requirement
satisfaction. An explain exit 0 means inspection succeeded, not validation passed.

After export, verify the actual commit with the original baseline:

```sh
vt verify --repo /path/to/repo --base BASE_COMMIT --candidate EXPORTED_COMMIT \
  --evidence /path/to/new-evidence/evidence.json
```

Add the same --scope if one was supplied. For exit-4 evidence, use
--allow-pending-review only when the caller enforces review before acceptance;
verification leaves it pending. Recheck changed contents. Follow the existing
Git/review process; this skill does not itself authorize publishing or acceptance.
Handoff the exact evidence path and concise assessment. Completion requires
matching current source, successful checks and the caller's review gates.
