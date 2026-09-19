# Versioned Traceability

Versioned Traceability checks requirement links, runs your project's tests, and
records results tied to the source snapshot checked. It compares requirements
and tests against a Git baseline to identify changes requiring review.

It uses [OpenFastTrace (OFT)](https://github.com/itsallcode/openfasttrace) to read
requirements and references in Markdown and source files and check their declared
traceability coverage. You can use it manually, with a coding agent, or in CI.

## How it works

Keep requirements beside your code and tests. Give each requirement an OFT ID and
reference that ID from the implementation and tests. For example:

```markdown
### Session expiration
`req~session-expiration~1`

Sessions expire after 30 minutes of inactivity.

Needs: impl, utest
```

Here, `1` is the requirement's revision, and `Needs` asks for implementation and
unit-test links. Add references beside the relevant code and test assertions:

```python
# [impl->req~session-expiration~1]  # In the implementation
# [utest->req~session-expiration~1] # In its test
```

OFT checks that the required links exist and reference the right revision. Your
tests check behavior. Review determines whether the requirements and assertions
are adequate. See the [session example](examples/session) for complete files.

Each check uses three inputs:

- **Baseline:** the Git commit used as the starting point for comparison.
- **Candidate:** the source being checked, either a commit or your current files.
- **Scope:** a JSON file selecting what to trace, the required coverage, and the
  test command. The checker uses a trusted copy from the baseline or the caller.

The tool checks links in both versions, runs the candidate's tests, and saves
**evidence**: results, logs, source identities, and changes requiring review.
Passing checks do not approve requirement changes or prove the software correct.
The [concepts and result meanings](versioned_traceability/skills/versioned-traceability/references/semantics.md)
explain these distinctions in detail.

## Install

Requires Python 3.11+, Git, and Java 17+ on Linux or macOS. In a Python virtual
environment, from this tool's checkout:

```sh
python3 -m pip install .
vt install-oft
```

The OFT installer downloads and checksum-verifies the configured release.
For an existing JAR, set `VT_OFT_JAR` or pass `--oft-jar` to `vt check`.

## Add traceability to an existing project

Start with the behavior you intend to change next, including its dependencies and
boundary cases. Use existing documentation, code, and tests to propose requirements
and links. Review them before using them as the baseline for future changes.

Give a coding agent the [existing-project skill](versioned_traceability/skills/recover-baseline/SKILL.md)
and ask: **"Document this project's session expiration requirements and link them
to the existing code and tests. Flag inferred behavior and missing checks."**
The skill covers setup, drafting, checks, and review. It works with any coding
agent that has shell access; missing tools may require network access.

For manual use, start in a clean project checkout:

```sh
vt recover
```

The command name calls this *baseline recovery*: reconstructing requirements from
existing sources. It saves the original source and prepares citation records;
it does not write requirements or run an agent. You then add requirements,
code/test references, a proposed `scope.json`, and citations following the
[existing-project guide](docs/recovery.md).

Check the proposal:

```sh
vt recover-check --preflight  # Check edits, citations, and links without tests
vt recover-check            # Also run the existing tests
```

Exit 5 from preflight means tests remain unrun. Exit 4 from the full check means
automation passed and the proposal needs review. Read the generated
`recovery-review.md`, resolve open questions, and commit the reviewed changes.
Then validate that commit as described below.

The default leaves proposed edits uncommitted in your checkout. Use `--isolated`
for a separate draft. Both modes retain originals and results under Git metadata;
those local files are not included in a push. The guide explains how to retain
and share them. Bug fixes and new tests follow review of the starting requirements.

## Check a change

### 1. Configure the project

Copy [scope.json](examples/session/scope.json) and adapt its paths and test
command. Use `tests.format: "junit"` with a JUnit XML report, or `"command"` for
the command's exit status and log; omit `report` for the latter.

Commit the reviewed `scope.json` at the repository root with the starting
requirements and references. Checks read this file from the baseline commit,
so candidate edits cannot change their own checking rules. Alternatively, keep
a trusted scope separately and pass `--scope /path/to/scope.json` to each command.
Keep that copy outside the candidate's control.

Tests run in a captured source directory without Git metadata or ignored local
environments. Provide the test dependencies in the environment that runs the
checker. Relative symlinks within the captured source are supported; submodules
are rejected. See [source identity](docs/contract.md#source-identity) for details.

### 2. Validate the starting commit

From the project's checkout:

```sh
vt check --base HEAD --candidate HEAD
```

This checks links and tests in the same commit, establishing whether the starting
point passes the configured checks.

### 3. Make changes and check them

Edit the project normally, then run:

```sh
vt check
```

The command uses these defaults:

| Argument | Default |
| --- | --- |
| `--repo` | The repository containing the current directory. |
| `--base` | The merge base of your branch and the default branch; `HEAD` on the default branch or with detached HEAD. |
| `--candidate` | `worktree`: current source files, including uncommitted changes. |
| `--scope` | Root `scope.json` from the baseline commit. |
| `--out` | A fresh temporary directory; its path is printed. |

Pass `--base COMMIT` when you need a different starting point. Default-branch
detection uses local Git refs; see the [command reference](docs/contract.md#check-and-verify-inputs).
Your branch and working files remain unchanged by the check.

Each run writes a new evidence directory. To retain results outside temporary
storage, use `--out /path/to/check-1`, choosing a new directory outside the project.
Recheck after edits: saved results describe only the contents checked.

## Understand and review the result

The command prints the outcome and evidence location. Open `summary.md` there for
changed requirement IDs, test results, pending review, and links to full reports.

| Exit from `vt check` | Meaning |
| --- | --- |
| 0 | Automated checks passed; no specification or test files changed. |
| 4 | Automated checks passed; specification or test changes need review. |
| 1, 2, 3 | Validation failed, could not run, or had an empty scope. |

Review the full Git diff and related behavior. `review.patch` contains only
specification/test changes and does not replace code review. Handle approval
through your project's normal review process.

To inspect a particular requirement and its immediate links in saved evidence:

```sh
vt explain 'req~session-expiration~1' --evidence /path/to/check/evidence.json
```

Supply several IDs to assemble their context together. Use `--format json` for
tools or `--snapshot base` to inspect the baseline. This command reads saved
results; it does not rerun tests or check current files. See the
[explanation reference](docs/contract.md#explain-saved-evidence).

To confirm that a later commit contains the source already checked:

```sh
vt verify --candidate HEAD --evidence /path/to/check/evidence.json
```

Use the same baseline and scope as the original check; pass them explicitly if
the defaults have changed. For exit-4 evidence, `--allow-pending-review` permits
matching while leaving review pending. Verification does not rerun tests.

## Work with an agent

Once the starting requirements are reviewed and committed, give your agent the
[development skill](versioned_traceability/skills/versioned-traceability/SKILL.md)
and the task: **"Implement this change following the traceability skill."**
The agent follows requirement links, maintains code and tests, and runs checks.
Review and discussion tasks can use the same skill. Initial documentation does
not need to be repeated for ordinary feature work.

Reference the skill in your project's agent instructions, or provide its link
with each task. Instructions guide agents; configure CI separately when checks
must be enforced for pull requests. An OpenHands integration is available in
[openhands-traceability](https://github.com/kbak/openhands-traceability).

## Add property tests

The [property-testing guide](docs/property-testing.md) explains how to turn selected
requirements into executable assertions over generated inputs. Reuse the project's
library, or use the examples for Hypothesis, fast-check, and QuickCheck. Tests run
through the project's normal runner without an agent. Passing searches provide
evidence about exercised inputs; they are not proofs.

For critical or ambiguous rules, add an optional [logical statement](docs/property-testing.md#optional-logical-statements)
beside the requirement: its domain, assumptions, and precise guarantee. Tests and
later formal models can reference the same property ID and revision.

To link individual reported test outcomes to requirement coverage, use the optional
[execution-link configuration](versioned_traceability/skills/versioned-traceability/references/execution-links.md)
and [pytest example](examples/pytest-session). This can also require selected
named tests to run and pass.

See the [command and evidence reference](docs/contract.md) for configuration and
limits, and [running the tests](docs/validation.md) for contributing to this tool.

## Inspect requirement evolution

Use `vt impact --evidence /path/to/evidence.json` to compare saved OFT declarations, exact edges and source-change categories. The [granularity guide](docs/requirement-granularity.md) and [bounded retry example](examples/granular-retries) show stable IDs, independent policy evolution, revision-only maintenance and preserved stale-link rejection. Reports do not infer assertion adequacy or human review effort.
