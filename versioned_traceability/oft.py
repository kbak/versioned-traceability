import os
import urllib.request
from pathlib import Path

from .common import CheckError, digest, run, within, xml_tree

OFT_VERSION = "4.9.0"
OFT_SHA256 = "d4ed42503ae066f51d55c3aad7c6e4b16acb80365921951ef5a065a4dc3d94f3"
OFT_URL = f"https://github.com/itsallcode/openfasttrace/releases/download/{OFT_VERSION}/openfasttrace-{OFT_VERSION}.jar"


def default_jar():
    return Path(
        os.environ.get(
            "VT_OFT_JAR",
            Path.home() / ".cache" / "versioned-traceability" / f"openfasttrace-{OFT_VERSION}.jar",
        )
    )


def validate_jar(path):
    try:
        if digest(path.read_bytes()) != OFT_SHA256:
            raise CheckError(f"OFT checksum mismatch: expected {OFT_SHA256}")
    except OSError as exc:
        raise CheckError(
            f"OFT {OFT_VERSION} is unavailable at {path}; run vt install-oft or pass --oft-jar"
        ) from exc


def install_jar(destination):
    destination.mkdir(parents=True, exist_ok=True)
    jar = destination / f"openfasttrace-{OFT_VERSION}.jar"
    if jar.exists():
        validate_jar(jar)
        return jar
    try:
        with urllib.request.urlopen(OFT_URL, timeout=60) as response:
            content = response.read()
    except OSError as exc:
        raise CheckError(f"OFT download failed: {exc}") from exc
    if digest(content) != OFT_SHA256:
        raise CheckError("Downloaded OFT checksum does not match pinned release")
    with jar.open("xb") as output:
        output.write(content)
    return jar


def element_value(element):
    """Normalize OFT-exported data, excluding location separately; no source parsing."""
    if not len(element):
        return element.text or ""
    return sorted([[child.tag, element_value(child)] for child in element], key=repr)


def import_items(path, root):
    tree = xml_tree(path)
    if tree.tag != "specdocument":
        raise CheckError("Unexpected OFT SpecObject root")
    items = []
    for group in tree.findall("specobjects"):
        kind = group.get("doctype")
        for element in group.findall("specobject"):
            name = element.findtext("id")
            version = element.findtext("version")
            source = element.findtext("sourcefile")
            if not kind or not name or version is None or not source:
                raise CheckError("Incomplete OFT SpecObject item")
            source_path = Path(source)
            if not source_path.is_absolute():
                source_path = root / source_path
            try:
                relative = source_path.relative_to(root).as_posix()
                revision = int(version)
            except ValueError as exc:
                raise CheckError("Invalid OFT source location or revision") from exc
            items.append(
                {
                    "key": f"{kind}~{name}",
                    "id": f"{kind}~{name}~{revision}",
                    "type": kind,
                    "revision": revision,
                    "path": relative,
                    "line": int(element.findtext("sourceline", "0")),
                    "needs": sorted(n.text for n in element.findall("needscoverage/needsobj")),
                    "content": {
                        child.tag: element_value(child)
                        for child in element
                        if child.tag not in {"id", "version", "sourcefile", "sourceline"}
                    },
                }
            )
    return items


def trace(snap, scope, jar, java, out, label):
    for path in scope["inputs"]:
        if not any(within(entry["path"], [path]) for entry in snap.manifest):
            raise CheckError(f"{label}: input path has no source files: {path}")
    # Relative inputs keep OFT's generated annotation IDs stable across snapshots.
    inputs = list(dict.fromkeys(scope["inputs"]))
    # Overlapping roots otherwise import the same requirement more than once.
    inputs = [p for p in inputs if not within(p, [q for q in inputs if p != q])]
    command = [java, "-jar", str(jar)]
    exported = out / f"{label}-items.xml"
    convert = run(
        command + ["convert", "-f", str(exported), *inputs], snap.root, out / f"{label}-import.log"
    )
    if convert["status"] != "passed":
        raise CheckError(f"{label}: OFT import failed; see {convert['log']}")
    # OFT may warn and skip malformed items while returning 0. Treat import diagnostics as errors.
    if (out / convert["log"]).read_text(errors="replace").strip():
        raise CheckError(f"{label}: OFT import emitted diagnostics; see {convert['log']}")
    items = import_items(exported, snap.root)
    result = run(
        command + ["trace", "-c", "BLACK_AND_WHITE", *inputs], snap.root, out / f"{label}-trace.log"
    )
    if result["status"] == "error" or result["exit_code"] not in (0, 1):
        raise CheckError(f"{label}: OFT could not execute tracing; see {result['log']}")
    return items, {
        "status": result["status"],
        "import": convert,
        "trace": result,
        "item_count": len(items),
    }


def policy_diagnostics(items, scope, label):
    diagnostics = []
    selected = [item for item in items if item["type"] in scope["required_coverage"]]
    keys = set()
    for item in selected:
        if item["key"] in keys:
            diagnostics.append(f"{label}: multiple active items for {item['key']}")
        keys.add(item["key"])
        missing = set(scope["required_coverage"][item["type"]]) - set(item["needs"])
        if missing:
            diagnostics.append(
                f"{label}: {item['id']} must retain Needs: {', '.join(sorted(missing))}"
            )
        if not within(item["path"], scope["specification_paths"]):
            diagnostics.append(f"{label}: {item['id']} is outside specification_paths")
    return selected, diagnostics
