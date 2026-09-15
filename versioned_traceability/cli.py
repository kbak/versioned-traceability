import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from . import __version__
from .common import CheckError
from .evidence import EXIT_CODES
from .oft import default_jar, install_jar
from .recovery import active_recovery, check_recovery, prepare
from .runner import check, verify
from .snapshot import git, resolve_commit


def default_base(repo):
    if git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip() == b"HEAD":
        return resolve_commit(repo, "HEAD")
    refs = dict(
        line.split(" ", 1)
        for line in git(
            repo,
            "for-each-ref",
            "--format=%(refname) %(symref)",
            "refs/heads",
            "refs/remotes/origin/HEAD",
        )
        .decode()
        .splitlines()
    )
    remote_default = refs.get("refs/remotes/origin/HEAD")
    if remote_default:
        local = "refs/heads/" + remote_default.removeprefix("refs/remotes/origin/")
        target = local if local in refs else remote_default
    elif "refs/heads/main" in refs:
        target = "refs/heads/main"
    elif "refs/heads/master" in refs:
        target = "refs/heads/master"
    else:
        raise CheckError(
            "Cannot identify the default branch; supply --base with the starting commit"
        )
    try:
        bases = git(repo, "merge-base", "--all", "HEAD", target).decode().splitlines()
    except CheckError as exc:
        raise CheckError(
            f"Cannot find a common ancestor with {target}; supply --base with the starting commit"
        ) from exc
    if len(bases) != 1:
        raise CheckError("No unique branch baseline; supply --base with the starting commit")
    return bases[0]


def parser():
    root = argparse.ArgumentParser(
        description="Portable OFT tracing, change review, and test evidence"
    )
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="action", required=True)
    install = commands.add_parser("install-oft", help="Download and checksum-verify OFT 4.9.0")
    install.add_argument("--destination", type=Path, default=default_jar().parent)
    recovery = commands.add_parser("recover", help="Prepare baseline recovery in a clean checkout")
    recovery.add_argument(
        "--isolated",
        action="store_true",
        help="Draft separately, leaving the original checkout unchanged",
    )
    recovery.add_argument(
        "--repo", type=Path, help="Source repository (default: current repository)"
    )
    recovery.add_argument(
        "--candidate",
        default="HEAD",
        help="Source version (default: HEAD); other versions require --isolated",
    )
    recovery.add_argument(
        "--input",
        action="append",
        dest="inputs",
        help="Inventoried path; repeat for multiple paths (default: .)",
    )
    recovery.add_argument(
        "--out",
        type=Path,
        help="New storage directory (default: Git recovery storage; temporary storage with --isolated)",
    )
    recovering = commands.add_parser(
        "recover-check", help="Validate a proposed baseline; always requires review"
    )
    target = recovering.add_mutually_exclusive_group()
    target.add_argument(
        "--recovery",
        type=Path,
        help="Directory produced by vt recover (required for isolated recovery)",
    )
    target.add_argument(
        "--repo",
        type=Path,
        help="Repository with an active in-place recovery (default: current repository)",
    )
    recovering.add_argument(
        "--scope", type=Path, help="Proposed scope (default: workspace/scope.json)"
    )
    recovering.add_argument(
        "--out", type=Path, help="New result directory (default: tool-managed storage)"
    )
    recovering.add_argument("--oft-jar", type=Path, default=default_jar())
    recovering.add_argument("--java", default="java")
    checking = commands.add_parser("check", help="Check changes against a Git baseline")
    verifying = commands.add_parser(
        "verify", help="Match saved passing evidence to current contents"
    )
    for command in (checking, verifying):
        command.add_argument(
            "--repo", type=Path, help="Repository root (default: current repository)"
        )
        command.add_argument(
            "--scope",
            type=Path,
            help="Trusted scope JSON (default: scope.json from the baseline commit)",
        )
        command.add_argument(
            "--base", help="Baseline commit/ref (default: merge base with the default branch)"
        )
        command.add_argument(
            "--candidate", default="worktree", help="Git commit/ref or worktree (default: worktree)"
        )
    checking.add_argument(
        "--out",
        type=Path,
        help="New evidence directory outside target repo (default: fresh temporary directory)",
    )
    checking.add_argument("--oft-jar", type=Path, default=default_jar())
    checking.add_argument("--java", default="java")
    verifying.add_argument(
        "--allow-pending-review",
        action="store_true",
        help="Match automated evidence before external review; does not authorize changes",
    )
    verifying.add_argument("--evidence", type=Path, required=True, help="Path to evidence.json")
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.action == "install-oft":
            print(install_jar(args.destination))
            return 0
        if args.action == "recover-check":
            if args.recovery is None:
                repo = args.repo or Path(
                    os.fsdecode(git(Path.cwd(), "rev-parse", "--show-toplevel")).strip()
                )
                args.recovery = active_recovery(repo)
            result = check_recovery(args.recovery, args.scope, args.out, args.oft_jar, args.java)
            print(f"{result['status']}: {Path(result['output']) / 'recovery-result.json'}")
            for message in result["diagnostics"]:
                print(f"- {message}")
            if result["status"] == "review_required":
                print(
                    f"Review the {'working-tree changes' if result['mode'] == 'in_place' else 'proposal.patch'}, claims, scope and open issues before accepting the baseline."
                )
            return EXIT_CODES[result["status"]]
        if args.repo is None:
            args.repo = Path(os.fsdecode(git(Path.cwd(), "rev-parse", "--show-toplevel")).strip())
        if args.action == "recover":
            result = prepare(
                args.repo, args.candidate, args.inputs or ["."], args.out, isolated=args.isolated
            )
            bundle = Path(result["bundle"])
            print(f"prepared: {bundle / 'recovery.json'} ({result['mode']})")
            print(f"source: {result['source']['commit']} ({result['source']['sha256']})")
            print(f"Read {bundle / 'instructions.md'}; work in {result['workspace']}")
            if not args.isolated:
                print(
                    f"Record citations in {Path(result['workspace']) / result['claims_path']}; review changes in Git before acceptance."
                )
            return 0
        if args.base is None:
            args.base = default_base(args.repo)
        if args.action == "verify":
            result = verify(
                args.repo,
                args.scope,
                args.base,
                args.candidate,
                args.evidence,
                args.allow_pending_review,
            )
            print(json.dumps(result, indent=2))
            return 0
        if args.out is None:
            if Path(tempfile.gettempdir()).resolve().is_relative_to(args.repo.resolve()):
                raise CheckError(
                    "Temporary directory is inside the repository; supply --out outside it"
                )
            args.out = Path(tempfile.mkdtemp(prefix="vt-evidence-")) / "check"
        result = check(
            args.repo,
            args.scope,
            args.base,
            args.candidate,
            args.out,
            args.oft_jar,
            args.java,
        )
        print(f"{result['status']}: {args.out.resolve() / 'evidence.json'}")
        if "base" in result:
            print(f"baseline: {result['base']['commit']}")
        for message in result["diagnostics"]:
            print(f"- {message}")
        if result["status"] == "review_required":
            print(
                "Automated checks passed; external review of review.json/review.patch is still required."
            )
        return EXIT_CODES[result["status"]]
    except (CheckError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
