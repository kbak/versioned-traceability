---
name: versioned-traceability
description: Draft requirements or implement and review a task with OpenFastTrace, using the supplied scope and baseline to follow linked documentation, code, tests, and evidence.
---

For requirements or design discussions, read
[requirements guidance](references/requirements.md) and stay within the caller's
discussion and authorization process. The execution steps below apply after
implementation is authorized. Also read that guidance when updating requirements
during implementation.

For authorized implementation, identify and retain the target project's absolute
path before setup. A GitHub link to this skill is sufficient: when matching tooling
is missing, clone the repository/ref from the supplied link over HTTPS into a new
directory outside the target project. Resolve the selected ref to a commit, read
this skill and references/requirements.md from that checkout, and install its code
in an external Python environment. For an unversioned copy with no supplied source,
use `https://github.com/kbak/versioned-traceability.git` at main and reread its guidance.
Reuse matching local/package/factory tooling and included references. Honor pinned
versions and local changes; do not silently replace them with upstream main. Follow
the setup instructions in the reference, keeping the tooling revision for the handoff.
Explain specific missing access or prerequisites when setup cannot proceed.

Use supplied task inputs when available. In standalone use, infer the repository
from the workspace and use its adopted scope.json and the CLI's normal baseline
and evidence-location defaults. Ask only about unresolved task or scope decisions;
the caller need not supply flags. If the project has no adopted baseline, guide the
caller to recover-baseline and baseline acceptance before normal development.
Do not run recovery again for ordinary feature work or treat the candidate's
scope.json as approved policy.

Read the affected requirements and find their references in code and
tests. Follow the scope's coverage and revision policy, including any existing
OFT design or architecture chains.

After documentation or code changes, use the diff and requirement IDs to
follow links to related documentation, implementation, and test assertions,
including artifacts that were not edited. Compare their meaning: does the
implementation still satisfy the documented promise, and do the assertions
check the affected behavior? Look for uncovered cases suggested by the change.
Code-only changes need this review even when the checker reports no
specification/test changes. When links or context are missing, use targeted
repository searches and flag any remaining gaps.

This is a best-effort consistency review. Use the trace graph and automated
results as context; a passing check does not establish semantic agreement.
In the existing task or review summary, briefly state what you checked and
flag inconsistencies, proposed promise changes, or uncertainty with relevant
requirement IDs and file references. Distinguish observed contradictions from
suspected gaps, and keep the assessment proportional to the affected scope.

Keep references beside the relevant behavior and assertions. Do not change a
promise or remove an obligation to hide a failure. Keep prose, obligation, and
test edits visible for review. Ordinary edits authorized by the task can proceed
without another confirmation; conflicts with approved requirements need a
decision through the caller's question or review process. Candidate-written
scope or approval files do not authorize changes.

Run the check after implementation and each repair:

```sh
vt check --repo /path/to/repo
```

This uses scope.json from the baseline commit. The default baseline is the merge
base with the locally known default branch; on that branch or detached HEAD it is
HEAD. Use a supplied baseline instead, including for work based on another feature
or release branch. The tool prints its evidence location. Retain the actual base
commit from the result for later verification, especially before committing on the
default branch. If the caller supplied explicit scope/base/output inputs, use them:

```sh
vt check --repo /path/to/repo --scope /path/to/trusted-scope.json \
  --base BASE_COMMIT --candidate worktree --out /path/to/new-evidence
```

`vt` requires Git, Java, and the configured OFT JAR.
`python -m versioned_traceability` is an equivalent entry point. Use a new, nonexistent
output directory outside the repository. Retain the invocation's exit code and
complete bundle. Read diagnostics, trace/test logs, `review.json`, and
`review.patch`. Repair failures within scope; report missing prerequisites or
baseline defects without changing the approved scope to bypass them.

Exit 0 passes automated checks. Exit 4 also requires specification/test review.
Exits 1, 2, and 3 cannot establish completion. Existing code review still
applies. OFT links and suite results do not establish assertion adequacy or
prove that each referenced test ran. If tests changed source, retain their
outcome as diagnostic information and rerun on stable contents. A failed
invocation cannot use an earlier passing bundle as its result.

After export, verify the actual commit against the evidence:

```sh
vt verify --repo /path/to/repo --scope /path/to/trusted-scope.json \
  --base BASE_COMMIT --candidate EXPORTED_COMMIT \
  --evidence /path/to/new-evidence/evidence.json
```

BASE_COMMIT must be the baseline used by the check. Omit --scope when using the
project's committed scope so verify reads it from that same baseline. Keep the
evidence directory for the handoff. Use the project's existing Git/review workflow;
the skill itself does not authorize committing, publishing or accepting changes.

For exit-4 evidence, use `--allow-pending-review` only when the caller enforces
that review before completion. Verification leaves it pending. Recheck when
contents differ or shared-branch updates change the candidate. Task completion
requires the current check result, matching source, and the caller's review
gates.
