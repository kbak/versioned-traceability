"""Human reports must preserve evidence limits without additional execution."""

import copy
import unittest
from unittest.mock import patch

from test_workflow import WorkflowFixture

from versioned_traceability import runner
from versioned_traceability.common import CheckError, read_json
from versioned_traceability.runner import verify
from versioned_traceability.summary import render_summary


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {
            "status": "passed",
            "diagnostics": [],
            "tests": {"status": "passed", "level": "command", "source_status": "matched"},
            "review": {"status": "not_needed"},
        }

    def test_command_success_does_not_invent_case_execution_or_approval(self):
        original = copy.deepcopy(self.evidence)
        text = render_summary(self.evidence, [], {"review.json", "review.patch", "tests.log"})
        self.assertIn("Individual linked-test execution is not established", text)
        self.assertIn("does not record approval", text)
        self.assertNotIn("Reported cases:", text)
        self.assertNotIn("[tests.xml]", text)
        self.assertEqual(self.evidence, original)

    def test_missing_comparison_is_not_reported_as_zero_changes(self):
        self.evidence.update(status="error", diagnostics=["OFT unavailable"])
        self.evidence["tests"].update(status="not_run", source_status="unchecked")
        self.evidence.pop("review")
        text = render_summary(self.evidence, None, set())
        self.assertIn("comparison did not complete", text)
        self.assertIn("matching stable source was not established", text)
        self.assertNotIn("Changed specification items: 0", text)
        self.assertNotIn("[review.json]", text)

    def test_skipped_missing_and_ambiguous_cases_remain_visible_on_passing_suite(self):
        self.evidence["tests"].update(
            level="suite",
            counts={"passed": 1, "failed": 0, "errors": 0, "skipped": 1},
            execution_links={
                "status": "recorded",
                "unlinked_cases": 1,
                "artifacts": [
                    {"id": f"utest~{status}~1", "status": status, "cases": []}
                    for status in ("passed", "skipped", "not_observed", "ambiguous")
                ],
            },
        )
        text = render_summary(self.evidence, [], {"tests.xml"})
        for status in ("skipped", "not_observed", "ambiguous"):
            self.assertIn(f"utest~{status}~1", text)
            self.assertLess(text.index(f"utest~{status}~1"), text.index("utest~passed~1"))
        self.assertIn("1 skipped", text)
        self.assertIn("reported cases without a resolved execution link: 1", text)
        self.evidence["tests"]["source_status"] = "changed"
        text = render_summary(self.evidence, [], {"tests.xml"})
        self.assertIn("Test results are diagnostic", text)


class SummaryWorkflowTests(WorkflowFixture):
    def test_report_retains_same_revision_change_and_runs_existing_checks_once(self):
        self.replace("requirements.md", "30 minutes", "60 minutes")
        with (
            patch.object(runner, "trace", wraps=runner.trace) as trace,
            patch.object(runner, "execute_tests", wraps=runner.execute_tests) as tests,
        ):
            result = self.run_check()
        self.assertEqual(result["status"], "review_required")
        self.assertEqual(trace.call_count, 2)  # The existing baseline and candidate traces.
        tests.assert_called_once()
        text = (self.out / "summary.md").read_text()
        self.assertIn("Changed specification items: 1", text)
        self.assertIn("Changed specification/test files: 1", text)
        self.assertEqual(text.count("req~session-expiration~1"), 2)
        self.assertIn("| Modified |", text)
        self.assertIn(result["candidate"]["sha256"], text)
        self.assertIn("Candidate: worktree based on commit", text)
        self.assertIn(result["scope"]["sha256"], text)
        self.assertIn("summary.md", result["artifacts"])
        self.assertEqual(read_json(self.out / "evidence.json")["predicate"], result)
        verify(
            self.repo,
            self.scope,
            self.base,
            "worktree",
            self.out / "evidence.json",
            allow_pending_review=True,
        )
        (self.out / "summary.md").write_text("Approved and fully verified.\n")
        with self.assertRaisesRegex(CheckError, "summary.md"):
            verify(
                self.repo,
                self.scope,
                self.base,
                "worktree",
                self.out / "evidence.json",
                allow_pending_review=True,
            )


if __name__ == "__main__":
    unittest.main()
