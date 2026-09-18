"""Check a packaged example, its deliberate boundary defect, and restoration.

Run with an installed vt wheel and the selected language's dependencies. Copies
come from this source tree (also included in the sdist); no original is modified.
Native failures and version-bound evidence are retained in a new output directory.
"""

import argparse
import importlib.metadata
import json
import shutil
import subprocess
import sys
from pathlib import Path

from versioned_traceability.oft import default_jar
from versioned_traceability.runner import check, verify

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
    "python": ("session.py", "return now >= last_activity + timeout", "AssertionError"),
    "typescript": ("session.js", "return now >= lastActivity + timeout", "Counterexample:"),
    "haskell": (
        "Main.hs",
        "expired lastActivity now ttl = now >= lastActivity + ttl",
        "*** Failed!",
    ),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("language", choices=EXAMPLES)
    parser.add_argument(
        "--out", type=Path, required=True, help="New directory for retained evidence"
    )
    parser.add_argument("--oft-jar", type=Path, default=default_jar())
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    repo = output / "repo"
    shutil.copytree(
        ROOT / "examples/property-testing" / args.language,
        repo,
        ignore=shutil.ignore_patterns(
            "__pycache__", ".hypothesis", "node_modules", "test-results.xml"
        ),
    )
    (repo / ".gitignore").write_text(
        "__pycache__/\n.pytest_cache/\n.hypothesis/\nnode_modules/\ntest-results.xml\n"
    )
    scope = json.loads((repo / "scope.json").read_text())
    if args.language == "python":
        scope["tests"]["command"][0] = sys.executable
    # The same trusted policy is used for every variant, outside the candidate.
    scope_path = output / "trusted-scope.json"
    scope_path.write_text(json.dumps(scope, indent=2) + "\n")
    for command in (
        ["init", "-q"],
        ["add", "."],
        [
            "-c",
            "user.name=Example validation",
            "-c",
            "user.email=example@invalid",
            "commit",
            "-qm",
            "Example baseline",
        ],
    ):
        subprocess.run(["git", "-C", str(repo), *command], check=True, capture_output=True)
    filename, fragment, failure_marker = EXAMPLES[args.language]
    target = repo / filename
    original = target.read_text()
    if original.count(fragment) != 1:
        raise RuntimeError("Example changed; update its deliberate boundary mutation")
    summary = {
        "language": args.language,
        "vt_version": importlib.metadata.version("versioned-traceability"),
        "variants": {},
    }
    try:
        for variant in ("correct", "mutant", "restored"):
            target.write_text(
                original.replace(fragment, fragment.replace(">=", ">"))
                if variant == "mutant"
                else original
            )
            artifacts = output / variant
            result = check(repo, scope_path, "HEAD", "worktree", artifacts, args.oft_jar)
            expected = "rejected" if variant == "mutant" else "passed"
            tests = result["tests"]
            valid = (
                result["status"] == expected
                and tests["status"] == ("failed" if variant == "mutant" else "passed")
                and tests["exit_code"] == (1 if variant == "mutant" else 0)
                and tests["source_status"] == "matched"
                and all(
                    result["trace"][label]["status"] == "passed" for label in ("base", "candidate")
                )
            )
            if variant == "mutant":
                valid = valid and failure_marker in (artifacts / "tests.log").read_text()
            if args.language == "python" and valid:
                boundary = next(
                    item
                    for item in tests["execution_links"]["artifacts"]
                    if item["id"] == "utest~expiration-boundary~1"
                )
                valid = boundary["status"] == ("failed" if variant == "mutant" else "passed")
            if variant != "mutant" and valid:
                verify(repo, scope_path, "HEAD", "worktree", artifacts / "evidence.json")
            summary["variants"][variant] = {
                "expected_outcome": valid,
                **{key: result[key] for key in ("status", "diagnostics", "tests")},
            }
            (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
            print(f"{args.language} {variant}: {result['status']} (expected={valid})", flush=True)
            if not valid:
                return 1
    finally:
        target.write_text(original)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
