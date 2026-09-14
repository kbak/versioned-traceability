import os
import shutil

from junitparser import Attr, JUnitXml, TestCase

from .common import CheckError, run, xml_tree


class ReportCase(TestCase):
    # Existing fixtures use the common disabled/notrun attribute dialect.
    status = Attr("status")


def report_cases(root):
    return [ReportCase.fromelem(case) for suite in JUnitXml.fromroot(root) for case in suite]


def skipped(case):
    return case.is_skipped or case.status in {"skipped", "disabled", "notrun"}


def junit_counts(path):
    root = xml_tree(path)
    if root.tag not in {"testsuite", "testsuites"}:
        raise CheckError("Test report must be JUnit testsuite/testsuites XML")
    cases = report_cases(root)
    counts = {"total": len(cases), "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    for case in cases:
        if case.is_error:
            counts["errors"] += 1
        elif case.is_failure:
            counts["failed"] += 1
        elif skipped(case):
            counts["skipped"] += 1
        else:
            counts["passed"] += 1
    # junitparser intentionally does not validate report completeness. Preserve
    # suite-level failures and omitted cases without imposing completion policy.
    for suite in root.iter():
        if suite.tag in {"testsuite", "testsuites"}:
            if suite.find("error") is not None or suite.find("failure") is not None:
                counts["suite_failed"] = True
            if "tests" in suite.attrib:
                try:
                    declared = int(suite.attrib["tests"])
                except ValueError as exc:
                    raise CheckError("Invalid JUnit tests count") from exc
                if declared != len(list(suite.iter("testcase"))):
                    raise CheckError("JUnit declared test count differs from reported test cases")
            for field in ("failures", "errors", "skipped", "disabled"):
                try:
                    value = int(suite.get(field, "0"))
                except ValueError as exc:
                    raise CheckError(f"Invalid JUnit {field} count") from exc
                if value < 0:
                    raise CheckError(f"Invalid JUnit {field} count")
                if value and field in {"failures", "errors"}:
                    counts["suite_failed"] = True
                if value and field in {"skipped", "disabled"}:
                    if value > sum(skipped(case) for case in report_cases(suite)):
                        raise CheckError("JUnit skip count lacks corresponding case outcomes")
                    counts["suite_skipped"] = True
    return counts


def counts_pass(counts, scope):
    return bool(
        counts["passed"]
        and not (counts["failed"] or counts["errors"] or counts.get("suite_failed"))
        and (
            scope.get("policy", {}).get("allow_skipped_tests", True)
            or not (counts["skipped"] or counts.get("suite_skipped"))
        )
    )


def execute_tests(snap, scope, out):
    config = scope["tests"]
    report = snap.root / config["report"] if config.get("format", "junit") == "junit" else None
    if report and report.exists():
        raise CheckError(
            "Configured JUnit report already exists in candidate; require a fresh generated report"
        )
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Commands using PROJECT_DIR must target the captured candidate.
    env["PROJECT_DIR"] = str(snap.root)
    result = run(config["command"], snap.root, out / "tests.log", config["timeout_seconds"], env)
    result["format"] = config.get("format", "junit")
    result["level"] = "suite" if report else "command"
    if report is None:
        return result
    if (
        not report.is_file()
        or report.is_symlink()
        or not report.resolve().is_relative_to(snap.root)
    ):
        result["status"] = "error"
        result["error"] = "Test command did not produce a fresh regular JUnit report"
        return result
    target = out / "tests.xml"
    shutil.copyfile(report, target)
    result["report"] = target.name
    try:
        counts = junit_counts(target)
        result["counts"] = counts
        if not counts_pass(counts, scope):
            result["status"] = "failed"
            result["error"] = "Report does not satisfy the configured test completion policy"
    except CheckError as exc:
        result["status"] = "error"
        result["error"] = str(exc)
    return result
