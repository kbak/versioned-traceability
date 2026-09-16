# Versioned Traceability

Versioned Traceability adds Git change tracking and test evidence to
[OpenFastTrace (OFT)](https://github.com/itsallcode/openfasttrace). OFT defines how
requirements and other artifacts are written, versioned, and linked, and checks
whether their declared coverage is satisfied.

This tool compares requirements and tests with a starting commit, runs your test
command, and saves a report identifying the source contents checked.

## What you put in the repository

Use OFT's syntax to write requirements and link them to supporting artifacts.
For example, a Markdown requirement can declare implementation and unit-test
coverage:

```markdown
### Session expiration
`req~session-expiration~1`

Sessions expire after 30 minutes of inactivity.

Needs: impl, utest
```

Here, `1` is the requirement's revision, and `Needs` asks for implementation and
unit-test coverage. Add references beside the relevant code and test assertions:

```python
# [impl->req~session-expiration~1]  # In the implementation
# [utest->req~session-expiration~1] # In its test
```

OFT checks that the required references exist and use the right revision.
Your test command checks behavior. Review determines whether the requirements
and assertions are adequate. Other artifact types and coverage chains are
supported; see the [session example](examples/session) for complete files.

Read the [semantic contract](versioned_traceability/skills/versioned-traceability/references/semantics.md)
for the shared human and agent meanings of coverage, artifact identity, claim
origin, authorization, and execution evidence. It includes an example of
explaining what a passing check establishes and what remains unverified.

## Install

Requires Python 3.11+, Git, and Java 17+ on Linux or macOS. In a Python virtual
environment, from this tool's checkout:

```sh
python3 -m pip install .
vt install-oft
```

The OFT installer downloads and checksum-verifies the configured release.
For an existing JAR, set `VT_OFT_JAR` or pass `--oft-jar` to `vt check`.

## Recover an existing project

Give your coding agent the [recovery skill](versioned_traceability/skills/recover-baseline/SKILL.md)
and ask: **"Recover this repository's baseline and guide me through it."** The
agent inspects the project, helps choose scope, prepares the draft and runs checks.
It presents proposed document/annotation changes, evidence and gaps for review.
The skill also handles setup: an agent starting from its GitHub link fetches the
matching tool revision when needed and installs it outside the target project.
Existing matching local or packaged tooling can be reused. The agent needs shell
access and network access for any missing downloads; no OpenHands installation is
required for this standalone workflow.

For manual preparation, start with a bounded recovery:

```sh
vt recover --repo /path/to/project
```

The default requires a clean checkout at HEAD. It preserves an original snapshot
in tool-managed Git storage and creates source/claims records under
`.traceability/recovery/`. The author adds native OFT requirements and coverage
comments directly to the checkout, proposes scope.json and records citations
and open questions in the indicated claims.json. Changes are visible in Git and
remain uncommitted. The original snapshot is retained throughout recovery.

The skill aims for a bounded first session: one extraction pass, one short
omissions pass, and a capability table with deferred work. Run
`vt recover-check --preflight` for feedback without executing tests; exit 5 means
tests remain unrun. Each check writes `recovery-review.md` with the current gaps,
diagnostics and artifact links. Both recovery modes retain their defaults under
Git metadata; preserve those local bundles when sharing the review.

Use `--isolated` to author in a separate draft and leave the original checkout
unchanged. The tool prepares and validates the workflow; it does not call a model.
The OpenHands adapter provides an agent example.

Then validate the proposal:

```sh
vt recover-check --repo /path/to/project
```

This checks original source citations, permits reviewed documentation restructuring
and coverage comments, and runs OFT plus the proposed test command. Exit 4 means
the proposal passed automation and still needs baseline review. It never
approves intent or commits the proposal. Inspect the Git changes, provenance,
open questions and test results before adopting the proposed scope. See the
[recovery guide](docs/recovery.md) for the complete experiment and adoption steps.

## Ongoing work with an agent

After reviewing and committing the initial baseline, give your agent the
[development skill](versioned_traceability/skills/versioned-traceability/SKILL.md)
and the next task: **"Implement this change following the traceability skill."**
It can fetch and install matching tooling when needed, use the project's committed
scope and normal baseline defaults, follow requirement IDs through code/tests,
and run checks. Review or discussion tasks can use the same skill without
authorizing implementation. Ordinary feature work does not repeat baseline recovery.

For future sessions, reference this skill in the target project's agent instructions
(for example AGENTS.md), or supply the link with each task. Giving a link in one
conversation does not automatically configure other agents or CI. A standalone
workflow needs no factory; shared CI checks can be added separately for PR enforcement.

## Check a change

You work in **one checkout**. The tool reads commits from Git and makes temporary
source snapshots automatically. Your working branch stays unchanged.

`vt check` works without arguments once the project has a committed scope:

| Argument | Default |
| --- | --- |
| `--repo` | The repository containing the current directory. |
| `--base` | The common ancestor of your branch and the repository's default branch. |
| `--candidate` | `worktree`: current files, including uncommitted changes. |
| `--scope` | `scope.json` from the baseline commit. |
| `--out` | A fresh temporary directory; the command prints the evidence path. |

On a feature branch, the comparison includes your commits and local edits. On
the default branch itself, the baseline is `HEAD`, so it checks local edits.
Pass `--base COMMIT` to choose a different starting point, including when working
from another feature or release branch. Default-branch detection uses local Git
refs; see the [reference](docs/contract.md#commands) for details.

### 1. Set up the scope

Copy [scope.json](examples/session/scope.json) and adapt its paths and test
command to your project. Set `tests.format` to `junit` for JUnit XML, or
`command` to use the command's exit status and log; omit `report` for the latter.

Choose where to maintain the scope:

- **In the project:** commit the reviewed `scope.json` at the repository root
  with the starting requirements, references, and tests. Checks read it from the
  baseline commit, so working-copy edits cannot change their own checking rules.
- **In separate configuration:** pass `--scope /path/to/trusted-scope.json`.
  This suits callers that maintain checking policy separately from the project.
  The file is read as-is; keep that approved copy outside the candidate's control.

Both setups support standalone checks. The test command's dependencies and
environment must be available wherever the check runs. The examples below use
the committed scope; add `--scope` to each command for a separate scope.

### 2. Validate the starting commit once

From your project's checkout:

```sh
vt check --base HEAD --candidate HEAD
```

Using the **same commit** for both flags checks that the starting requirements,
references, and tests pass. Later checks trace both versions and run the
candidate's tests.

### 3. Check your edits

Edit your files normally, then run:

```sh
vt check
```

Each run gets a new output directory. Use `--out ../check-1` to retain evidence
outside temporary storage; the directory must be outside the repository and
must not already exist. Recheck after edits: a previous report describes the
earlier contents. The command prints the selected baseline commit as well as the
evidence path.

## Read the result

To explain one artifact from a saved check, use its complete OFT ID:

```sh
vt explain 'req~session-expiration~1' --evidence /path/to/check/evidence.json
```

This shows OFT coverage and immediate links, the recorded test outcome, source
and scope identity, and pending review. Add `--format json` for tools or agents,
or `--snapshot base` for the baseline. It uses OFT's native XML graph report over
the retained export; it does not need the original checkout or rerun tests.
Exit 0 means the explanation was produced, even when the recorded check failed.
See the [explanation reference](docs/contract.md#explain-saved-evidence) for limits.

To associate individual reported test outcomes with OFT artifacts, enable the
optional [execution-link profile](versioned_traceability/skills/versioned-traceability/references/execution-links.md).
The [pytest example](examples/pytest-session) demonstrates explicit IDs,
parameterized tests, and a collection hook. The existing JUnit parser is reused;
pytest is a dependency of that example, not of the vt runtime.

For `vt check`, the exit codes mean:

| Exit | Meaning |
| --- | --- |
| 0 | Automated checks passed; no specification or test files changed. |
| 4 | Automated checks passed; requirement or test changes need review. |
| 1, 2, 3 | Validation failed, could not run, or had an empty scope. |

The output contains `evidence.json` with the outcome, trace and test logs,
`review.patch` with requirement/test changes, and source manifests. Handle
pending review in your existing review workflow; a check does not approve edits.

To confirm that a later commit contains exactly the files already checked, use
the evidence path printed by the check:

```sh
vt verify --candidate HEAD --evidence /path/to/check/evidence.json
```

Verification uses the same defaults and matches contents without rerunning
tests. If the baseline has moved, or you supplied `--base` or `--scope` for the
check, supply the same baseline and scope here. For exit-4 evidence,
`--allow-pending-review` permits matching while leaving review pending.

Tests run in a snapshot that omits Git metadata and ignored local environments,
preserves relative symlinks within the captured source, and rejects submodules.
Use actual source paths for tracing and citations; link aliases are not imported
again. Arrange test dependencies accordingly.
See the [reference](docs/contract.md) for configuration, evidence, and limits;
[test instructions](docs/validation.md); and the packaged
[skill](versioned_traceability/skills/versioned-traceability/SKILL.md) for agents.
