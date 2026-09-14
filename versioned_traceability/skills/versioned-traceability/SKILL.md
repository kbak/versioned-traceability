---
name: versioned-traceability
description: Implement or review a task with OpenFastTrace, using a supplied baseline and scope to check linked documentation, code, tests, and source-bound evidence.
---

Use the supplied task, repository, trusted scope, baseline, and evidence
location. Read the affected requirements and find their references in code and
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

For exit-4 evidence, use `--allow-pending-review` only when the caller enforces
that review before completion. Verification leaves it pending. Recheck when
contents differ or shared-branch updates change the candidate. Task completion
requires the current check result, matching source, and the caller's review
gates.
