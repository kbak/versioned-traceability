# Command and evidence reference

Scope schema 1 and evidence schema 2 are provisional and may change.

## Commands

| Command | Required arguments | Result |
| --- | --- | --- |
| `vt install-oft` | None; optional `--destination DIRECTORY` | Downloads and checksum-verifies the configured OFT release. |
| `vt check` | None | Traces both versions, runs candidate tests, and writes evidence. |
| `vt verify` | `--evidence` | Matches saved evidence to the selected scope, base, and candidate. |

For both `check` and `verify`:

- `--repo` defaults to the repository containing the current directory, including
  when invoked from a subdirectory. An explicit path must name the repository
  root. The repository must have a HEAD commit.
- `--base` defaults to the merge base of HEAD and the default branch. The CLI
  identifies that branch through `origin/HEAD`, preferring its local branch when
  present. Without `origin/HEAD`, it looks for local `main`, then `master`.
  It uses existing refs without fetching. On the default branch itself, or with
  detached HEAD, the baseline is HEAD. If no default branch or unique merge base
  can be found, supply `--base COMMIT` explicitly. For changes based on another
  feature or release branch, also supply the intended starting commit.
- `--candidate` defaults to `worktree`; it also accepts a commit or ref.
- `--scope` defaults to the root `scope.json` read from the resolved baseline
  commit. An explicit path is read as-is, relative to the current directory.

`check` creates a fresh `vt-evidence-*/check` directory in system temporary
storage and prints the evidence path. To retain evidence elsewhere, supply
`--out`: it must be a new directory outside the repository. Keep the full output
bundle when moving or retaining evidence. If the system temporary directory is
inside the repository, an explicit output path is required.

For `verify`, use the same baseline and scope as the original check. If the
default baseline has moved, pass its original commit with `--base`.

Checks use the JAR selected by `--oft-jar` or `VT_OFT_JAR`, falling back to the
user cache. `--java` selects the Java executable. Provision these tools before
running a check.

## Scope

```json
{
  "schema_version": 1,
  "name": "session",
  "inputs": ["requirements.md", "session.py", "tests", "run_tests.py"],
  "specification_paths": ["requirements.md"],
  "test_paths": ["tests", "run_tests.py"],
  "required_coverage": {"req": ["impl", "utest"]},
  "policy": {
    "require_revision_increase": false,
    "allow_skipped_tests": true
  },
  "tests": {
    "format": "junit",
    "command": ["python3", "run_tests.py"],
    "report": "test-results.xml",
    "timeout_seconds": 30
  }
}
```

`inputs` selects files for OFT. Each root must contain files at both versions.
Paths are literal, repository-relative POSIX paths; `.` selects the whole
snapshot. Path escapes and `.git` paths are rejected. Overlapping input roots
are imported once.

`specification_paths` and `test_paths` must lie within inputs and must not
overlap each other. Include test helpers, fixtures, and runner configuration in
test paths to expose their changes for review.

`required_coverage` selects artifact types and their minimum `Needs`. Selected
artifacts must originate within specification paths. An empty needs list is
valid. To use a design chain, for example, select `{"req": ["dsn"], "dsn":
["impl", "utest"]}`. OFT validates the relationships and revisions throughout
the chain.

The same scope applies to base and candidate. By default, it comes from the
baseline commit; changes to the candidate's copy do not change the checking
rules. A missing or invalid baseline scope fails without falling back to the
working copy. For an explicit `--scope`, keep a trusted copy outside candidate
control for checking and verification. The path can be inside or outside the
repository. Changes to the approved scope require authorization and a fresh
check. OFT's `Status: approved` and files written by the candidate do not grant
that authorization.

Unknown fields, duplicate JSON keys, invalid types, and unsupported schema
versions are errors. Both versions must pass tracing and configured coverage
checks. Validate a baseline's tests with base equal to candidate; subsequent
change checks trace the base and run only the candidate's tests.

An empty candidate normally fails. `allow_empty: true` permits status `empty`
(exit 3) when no other check fails. Removed artifacts remain in the review
record; empty scope does not count as successful coverage or test execution.

## Review and revision policy

Specification and test changes are compared against the baseline. The comparison
includes OFT artifact content, revisions, relationships, obligations, and file
content/modes. It covers intermediate design artifacts and prose outside
artifact blocks. `review.json` records the changes and their source/scope
digests; `review.patch` displays the text diff.

When automated checks pass, any specification or test change produces
`review_required`. The caller's review process decides whether the change is
adequate and authorized. Ordinary edits covered by the task proceed to that
review. Conflicts with approved requirements need a decision through the
caller's existing question or review process.

`policy.require_revision_increase` defaults to false. When true, imported
content changes require a higher revision, and revisions may not decrease. When
false, revision changes are left to review. OFT always checks reference
revisions.

Review must assess the meaning of changed requirements and the adequacy of
assertions. Structural references alone cannot establish that a requirement is
satisfied or that its particular test ran.

## Test execution

`tests.command` is an argument array. Shell syntax requires explicitly selecting
a shell, for example `["bash", "-c", "make test"]`. Commands run in the captured
candidate with the invoking account's permissions and inherited environment.
`PROJECT_DIR` points to that snapshot, and Python bytecode writes are disabled.
Set `TMPDIR` to place snapshots on a volume accessible to containerized tests.

`tests.timeout_seconds` must be an integer from 1 to 86400. The runner stops
remaining processes in the command's process group after completion or timeout.
It retains command arguments and output; it does not record environment values.
Use an isolated worker when commands need restricted access to the host.

| Format | Configuration | Passing result |
| --- | --- | --- |
| `junit` (default) | Set `tests.report` to a relative file path. | Exit 0, a fresh complete report, at least one passing case, and no failures or errors. |
| `command` | Omit `tests.report`. | Exit 0 from the configured command. No case counts or skip results are recorded. |

The JUnit adapter accepts unnamespaced XML and rejects DTDs/entities, malformed
or inconsistent reports, and reports already present in the candidate. Entirely
skipped or empty suites fail. `policy.allow_skipped_tests` defaults to true;
false also rejects mixed passing/skipped suites. Suite-level errors fail.

## Source identity

The source digest is SHA-256 of canonical JSON containing sorted `{path, mode,
sha256}` entries. JSON uses sorted keys, ASCII escaping, compact separators, and
no trailing newline. Modes are `100644` or `100755`. The retained manifest
contains those exact bytes.

Commit snapshots read Git blobs, unaffected by archive export attributes.
Worktree snapshots include tracked files as present on disk and untracked
nonignored files, including files outside trace inputs. Deleted tracked files
are absent. Tracing and tests consume the same captured candidate.

Before/after checks detect modifications to captured source and concurrent
changes to the original candidate. They cannot detect a command that changes and
restores source while running. Ignored untracked files, Git metadata, installed
dependencies, environment, and network state are outside source identity.
Snapshots omit `.git` and ignored local environments, reject symlinks and
submodules, and leave Git LFS pointers unexpanded.

## Evidence files

| Files | Contents |
| --- | --- |
| `scope.json`, `base-manifest.json`, `candidate-manifest.json` | Checked scope and source identities. |
| `base-items.xml`, `candidate-items.xml`, `*-import.log`, `*-trace.log` | OFT exports and execution logs. |
| `review.json`, `review.patch` | Specification and test changes. |
| `tests.log`, optional `tests.xml` | Command output and retained JUnit report. |
| `evidence.json` | Check outcome, identities, tool versions, review state, diagnostics, and artifact hashes. |
| `test-result.json` | Test attestation, emitted only when execution has a confirmed stable source. |

`evidence.json` uses an unsigned [in-toto Statement
v1](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md). Its
subject is `candidate-manifest.json` and the source digest. The predicate type
is `https://github.com/kbak/versioned-traceability/check/v0.2`. Error statements
may have no subject if source capture failed.

`test-result.json` uses the [in-toto Test Result
predicate](https://github.com/in-toto/attestation/blob/main/spec/predicates/test-result.md),
with the same subject and a digest of the scope file. It omits per-test names.
`tests.source_status` is `matched`, `changed`, or `unchecked`. Changed or
unchecked source suppresses this attestation, even if the subprocess passed; its
outcome remains in the check record for diagnosis. Verification requires
`matched`. Evidence without that field needs a fresh check.

Artifact hashes detect changes relative to the record. Statements are unsigned;
the caller's storage and access controls must establish who produced them.

## Exit codes and verification

| Check exit | Status | Meaning |
| --- | --- | --- |
| 0 | `passed` | Automated checks passed; no specification or test changes need this review gate. |
| 1 | `rejected` | Trace, policy, test, or source-stability checks failed. |
| 2 | `error` | Invalid input, missing tools, or execution/evidence setup failure. |
| 3 | `empty` | Empty selected scope; no successful coverage or executed-test claim. |
| 4 | `review_required` | Automated checks passed; specification or test changes await review. |

Preserve the current invocation's exit code as well as its bundle. A failed
invocation cannot be replaced with an earlier passing bundle.

`verify` checks retained artifacts and outcomes against the trusted scope, base,
and actual candidate contents. It normally accepts only `passed` evidence.
`--allow-pending-review` also accepts `review_required` and returns `review:
required`; the caller must still complete review before accepting the change.
Caller-required code review also applies to exit-0 checks.

Verification matches contents; it does not rerun tests. A worktree can match a
later exported commit with a different commit ID when the full manifest matches.
Rerun checks after repairs or shared-branch updates that change the candidate.
