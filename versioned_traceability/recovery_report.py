"""A small human handoff derived from the current recovery invocation."""


def render_review(result, checked, provenance):
    tests = checked.get("tests", {})
    trace = checked.get("trace", {}).get("candidate", {})
    items = provenance.get("items", [])
    lines = [
        "# Recovery review",
        "",
        f"Result: **{result['status']}**. Baseline acceptance remains a separate review decision.",
        "",
        "| Check | Result |",
        "| --- | --- |",
        f"| Source preservation, citations and original-ID accounting | {result['proposal_checks']} |",
        f"| Candidate OFT graph | {trace.get('status', 'not_run')} |",
        f"| Tests | {tests.get('status', 'not_run')} |",
        f"| Test source stability | {tests.get('source_status', 'unchecked')} |",
        "",
        f"Validated provenance: {len(items)} items, "
        f"{sum(i['origin'] == 'inferred' for i in items)} inferred. "
        "These counts do not measure extraction completeness or requirement satisfaction.",
    ]
    if "counts" in tests:
        c = tests["counts"]
        lines += [
            "",
            f"Tests: {c['passed']} passed, {c['failed']} failed, "
            f"{c['errors']} errors, {c['skipped']} skipped ({tests['level']} evidence).",
        ]
    if "source" in result:
        lines += ["", f"Original commit: `{result['source']['commit']}`."]
    if "candidate" in result:
        lines += [f"Proposed source digest: `{result['candidate']['sha256']}`."]
    lines += ["", "## Decisions and gaps", ""]
    issues = provenance.get("open_issues", [])
    for issue in issues:
        lines.append("- " + issue["description"].replace("\n", " "))
    if not issues:
        lines.append("No validated open-issue entries. This does not establish completeness.")
    for title, messages in (
        ("Diagnostics", result["diagnostics"]),
        ("Storage", result.get("warnings", [])),
    ):
        if messages:
            lines += ["", f"## {title}", ""]
            lines += ["- " + message.replace("\n", " ") for message in messages]
    lines += ["", "## Review artifacts", ""]
    for name in result["review_artifacts"]:
        lines.append(f"- [{name}]({name})")
    lines += ["", "## Next step", ""]
    if result["proposal_checks"] != "passed":
        lines.append(
            "Resolve the proposal diagnostics before relying on its provenance or permitted-edit checks."
        )
    elif result["status"] == "incomplete":
        lines.append(
            "Preflight completed without running tests. Run a full recover-check when the test environment is ready."
        )
    elif result["status"] != "review_required":
        lines.append(
            "The proposal checks passed, but the selected validation policy is not satisfied. "
            "Review the partial proposal and assign missing behavior/tests as follow-up work. "
            "Do not remove obligations merely to obtain a pass."
        )
    else:
        lines.append(
            "Review the requirements, scope, inferred intent and open issues before accepting the baseline."
        )
    lines += [
        "",
        "Review the capability/deferred-work table in the proposed documentation. "
        "Trace links and suite success do not establish every assertion or real-device/provider behavior.",
        "",
        "In-place edits already exist; do not reapply proposal.patch. For isolated recovery, "
        "transfer only reviewed edits. Retain this complete result directory and the original recovery "
        "bundle, then validate the actual adopted commit. A partial proposal does not enable or bypass "
        "the ordinary development gate.",
        "",
    ]
    return "\n".join(lines)
