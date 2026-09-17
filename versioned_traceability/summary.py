"""Human-readable check evidence, rendered without another check or agent pass."""

from html import escape


def code(value):
    return "<code>" + escape(" ".join(str(value).split())).replace("|", "&#124;") + "</code>"


def render_summary(evidence, changed, artifacts):
    tests = evidence["tests"]
    lines = [
        "# Traceability check",
        "",
        f"Recorded result: **{evidence['status'].replace('_', ' ').capitalize()}**.",
        "",
        "This report describes the captured source and checking policy. "
        "It does not record approval or establish requirement satisfaction.",
        "",
        "| Check | Recorded result |",
        "| --- | --- |",
    ]
    for label in ("base", "candidate"):
        status = evidence.get("trace", {}).get(label, {}).get("status", "not_run")
        lines.append(f"| {label.title()} OFT coverage | {code(status)} |")
    lines += [
        f"| Tests | {code(tests['status'])} ({code(tests['level'])} evidence) |",
        f"| Test source stability | {code(tests['source_status'])} |",
        f"| Specification/test review gate | {code(evidence.get('review', {}).get('status', 'not_recorded'))} |",
    ]
    if "counts" in tests:
        counts = tests["counts"]
        lines += [
            "",
            f"Reported cases: {counts['passed']} passed, {counts['failed']} failed, "
            f"{counts['errors']} errors, {counts['skipped']} skipped.",
        ]
    if tests["source_status"] != "matched":
        lines += ["", "Test results are diagnostic; matching stable source was not established."]
    if evidence["diagnostics"]:
        lines += ["", "## Diagnostics", ""]
        lines += ["- " + code(message) for message in evidence["diagnostics"][:20]]
        if len(evidence["diagnostics"]) > 20:
            lines += ["", "Additional diagnostics are retained in [evidence.json](evidence.json)."]

    lines += ["", "## Changed specifications", ""]
    if changed is None:
        lines.append("The specification/test comparison did not complete.")
    else:
        specifications = [item for item in changed if item["kind"] == "requirement"]
        files = [item for item in changed if item["kind"] == "file"]
        lines.append(
            f"Changed specification items: {len(specifications)}. "
            f"Changed specification/test files: {len(files)}. These counts can overlap."
        )
        if specifications:
            lines += [
                "",
                "| Change | Baseline item and location | Candidate item and location |",
                "| --- | --- | --- |",
            ]
            for change in specifications[:20]:
                before, after = change["before"], change["after"]
                action = "Added" if before is None else "Removed" if after is None else "Modified"
                locations = [
                    code(item["id"]) + " at " + code(f"{item['path']}:{item['line']}")
                    if item
                    else "—"
                    for item in (before, after)
                ]
                lines.append(f"| {action} | {' | '.join(locations)} |")
        if files:
            lines += ["", "Changed specification/test paths:", ""]
            lines += ["- " + code(item["path"]) for item in files[:20]]
        if len(specifications) > 20 or len(files) > 20:
            lines += [
                "",
                "Showing the first 20 entries in each list; the full comparison is retained.",
            ]
        lines += [
            "",
            "See [review.json](review.json) for exact changes and [review.patch](review.patch) "
            "for specification/test diffs. Source locations refer to their named snapshot. "
            "The implementation diff still needs review.",
        ]

    lines += ["", "## Test execution links", ""]
    links = tests.get("execution_links")
    if links is None:
        lines.append(
            "Individual linked-test execution is not established by this bundle. "
            "Command or suite success does not identify which requirement assertions ran."
        )
    else:
        lines.append(
            f"Execution-link record: {code(links['status'])}; "
            f"reported cases without a resolved execution link: {links['unlinked_cases']}."
        )
        # Surface missing/skipped/ambiguous observations before passing ones.
        ordered = sorted(links["artifacts"], key=lambda item: item["status"] == "passed")
        if ordered:
            lines += ["", "| Test artifact | Reported outcome | Cases |", "| --- | --- | --- |"]
            lines += [
                f"| {code(item['id'])} | {code(item['status'])} | {len(item['cases'])} |"
                for item in ordered[:20]
            ]
            if len(ordered) > 20:
                lines += [
                    "",
                    "Additional test artifacts and all case details are in evidence.json.",
                ]
        lines += [
            "",
            "These are recorded observations, including skips and tests not observed. "
            "They do not establish assertion adequacy or requirement satisfaction.",
        ]

    lines += ["", "## Source and evidence", ""]
    for label in ("base", "candidate"):
        source = evidence.get(label)
        if source:
            revision = "worktree based on commit" if source["kind"] == "worktree" else "commit"
            lines.append(
                f"- {label.title()}: {revision} {code(source['commit'])}; "
                f"source digest {code(source['sha256'])}."
            )
    if "scope" in evidence:
        lines.append(f"- Checking policy digest: {code(evidence['scope']['sha256'])}.")
    lines += ["", "Full records:", "", "- [evidence.json](evidence.json)"]
    lines += [
        f"- [{name}]({name})"
        for name in ("scope.json", "review.json", "review.patch", "tests.xml", "tests.log")
        if name in artifacts
    ]
    return "\n".join(lines) + "\n"
