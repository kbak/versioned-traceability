"""Explain saved evidence using OFT's augmented SpecObject graph report."""

import tempfile
from pathlib import Path

from .common import CheckError, canonical, digest, read_json, run, xml_tree
from .config import load_scope
from .evidence import check_artifacts, read_statement
from .execution import explain_execution, retained_execution_links
from .oft import OFT_SHA256, OFT_VERSION, validate_jar


def report_items(path):
    """Read OFT-computed coverage and edges; do not implement tracing rules."""
    root = xml_tree(path)
    if root.tag != "specdocument":
        raise CheckError("Unexpected OFT aspec root")

    def identifier(element, kind=None):
        return "~".join(
            (
                kind or element.findtext("doctype"),
                element.findtext("id"),
                element.findtext("version"),
            )
        )

    items = {}
    for group in root.findall("specobjects"):
        for element in group.findall("specobject"):
            key = identifier(element, group.get("doctype"))
            if key in items:
                raise CheckError(f"Ambiguous OFT item: {key}")
            items[key] = {
                "id": key,
                "title": element.findtext("shortdesc", ""),
                "description": element.findtext("description", ""),
                "path": element.findtext("sourcefile", ""),
                "line": int(element.findtext("sourceline", "0")),
                "oft_status": element.findtext("status"),
                "needs": sorted(n.text for n in element.findall("coverage/needscoverage/needsobj")),
                "coverage": {
                    "shallow": element.findtext("coverage/shallowCoverageStatus"),
                    "deep": element.findtext("coverage/deepCoverageStatus"),
                    "uncovered_types": sorted(
                        n.text for n in element.findall("coverage/uncoveredTypes/uncoveredType")
                    ),
                },
                "covers": sorted(identifier(n) for n in element.findall("covering/coveredType")),
                "covered_by": sorted(
                    identifier(n)
                    for n in element.findall("coverage/coveringSpecObjects/coveringSpecObject")
                ),
            }
    return items


def explain(identifier, evidence_path, jar, snapshot="candidate", java="java"):
    if snapshot not in {"base", "candidate"}:
        raise CheckError("Select the base or candidate snapshot")
    evidence_path = evidence_path.resolve()
    directory = evidence_path.parent
    evidence = read_statement(read_json(evidence_path))
    if evidence.get("schema_version") != 2:
        raise CheckError("Unsupported evidence schema")
    if evidence.get("oft") != {"version": OFT_VERSION, "sha256": OFT_SHA256}:
        raise CheckError("Evidence requires a different OFT version")
    required = {
        "scope.json",
        f"{snapshot}-items.xml",
        "base-manifest.json",
        "candidate-manifest.json",
    }
    check_artifacts(evidence, directory, required)
    scope = load_scope(directory / "scope.json")
    if (
        scope != evidence["scope"]["configuration"]
        or digest(canonical(scope)) != evidence["scope"]["sha256"]
    ):
        raise CheckError("Scope differs from recorded policy")
    for label in ("base", "candidate"):
        if (
            digest(canonical(read_json(directory / f"{label}-manifest.json")))
            != evidence[label]["sha256"]
        ):
            raise CheckError(f"{label} manifest does not match evidence identity")
    jar = jar.resolve()
    validate_jar(jar)
    with tempfile.TemporaryDirectory(prefix="vt-explain-") as temporary:
        output = Path(temporary)
        report = output / "trace.xml"
        traced = run(
            [
                java,
                "-jar",
                str(jar),
                "trace",
                "-o",
                "aspec",
                "-f",
                str(report),
                str(directory / f"{snapshot}-items.xml"),
            ],
            output,
            output / "trace.log",
        )
        if traced["exit_code"] not in (0, 1) or not report.is_file():
            raise CheckError(
                "OFT could not report retained artifacts: "
                + (output / "trace.log").read_text(errors="replace")
            )
        items = report_items(report)
    if identifier not in items:
        raise CheckError(
            f"Unknown OFT item in {snapshot}: {identifier}; use the complete ID and revision"
        )
    item = items[identifier]
    related = sorted(set(item["covers"] + item["covered_by"]))
    tests = (
        evidence["tests"] if snapshot == "candidate" else {"status": "not_recorded_for_baseline"}
    )
    links = (
        retained_execution_links(evidence, directory, scope) if snapshot == "candidate" else None
    )
    execution_status, linked_tests, execution_diagnostics = explain_execution(
        identifier, items, links, tests
    )
    return {
        "schema_version": 1,
        "evidence": str(evidence_path),
        "snapshot": snapshot,
        "source": evidence[snapshot],
        "scope": {"name": scope["name"], "sha256": evidence["scope"]["sha256"]},
        "artifact": item,
        "related": [
            {key: items[ref][key] for key in ("id", "title", "path", "line")}
            if ref in items
            else {"id": ref, "missing": True}
            for ref in related
        ],
        "recorded_check_status": evidence["status"],
        "recorded_diagnostics": evidence.get("diagnostics", []),
        "oft_trace_status": traced["status"],
        "tests": {
            key: tests[key]
            for key in ("status", "level", "source_status", "counts")
            if key in tests
        },
        "linked_test_execution": execution_status,
        "linked_tests": linked_tests,
        "execution_link_diagnostics": execution_diagnostics,
        "review": evidence.get("review", {"status": "not_recorded"}),
        "limitations": [
            "Describes the saved bundle; use vt verify to match current source. Artifact hashes do not authenticate the unsigned producer.",
            "OFT coverage is structural. Linked execution outcomes describe only reported cases, not assertion adequacy, all required scenarios, or requirement satisfaction.",
            "Review is the recorded check gate, not an approval decision. Claim origin is not recorded in ordinary check bundles.",
        ],
    }


def render_explanation(result):
    item = result["artifact"]
    lines = [
        f"{item['id']}: {item['title']}",
        f"Location ({result['snapshot']}): {item['path']}:{item['line']}",
        item["description"],
        f"Needs: {', '.join(item['needs']) or '(none)'}",
        f"OFT coverage: shallow={item['coverage']['shallow']}, deep={item['coverage']['deep']}",
        f"Covers: {', '.join(item['covers']) or '(none)'}",
        f"Covered by: {', '.join(item['covered_by']) or '(none)'}",
    ]
    lines.extend(
        f"  {ref['id']}: {ref.get('path', '(missing)')}:{ref.get('line', '')}"
        for ref in result["related"]
    )
    tests = result["tests"]
    lines.extend(
        [
            f"Recorded check: {result['recorded_check_status']}",
            f"Tests: {tests['status']} ({tests.get('level', 'no baseline execution recorded')}); source={tests.get('source_status', 'not recorded')}",
            "Execution of linked tests: " + result["linked_test_execution"].replace("_", " "),
            f"Recorded review gate: {result['review']['status']}",
            f"Source: {result['source']['sha256']}",
            f"Scope: {result['scope']['name']} ({result['scope']['sha256']})",
            f"Evidence: {result['evidence']}",
        ]
    )
    for linked in result["linked_tests"]:
        lines.append(f"  {linked['id']}: {linked['status'].replace('_', ' ')}")
        for case in linked["cases"]:
            name = " / ".join(
                part for part in [*case["suite"], case["classname"], case["name"]] if part
            )
            lines.append(f"    {name}: {case['status']}")
            lines.extend(f"      {message}" for message in case["diagnostics"])
            for detail in case["details"]:
                lines.append("      " + ": ".join(value for value in detail.values() if value))
    lines.extend(f"Execution link: {message}" for message in result["execution_link_diagnostics"])
    lines.extend(f"Diagnostic: {message}" for message in result["recorded_diagnostics"])
    lines.extend(result["limitations"])
    return "\n".join(lines)
