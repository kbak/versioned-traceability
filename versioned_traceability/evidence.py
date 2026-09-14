"""Unsigned in-toto statements; no signing, transport, or approval framework."""

from .common import CheckError

EXIT_CODES = {"passed": 0, "rejected": 1, "error": 2, "empty": 3, "review_required": 4}

STATEMENT = "https://in-toto.io/Statement/v1"
CHECK_TYPE = "https://github.com/kbak/versioned-traceability/check/v0.2"
TEST_TYPE = "https://in-toto.io/attestation/test-result/v0.1"


def statement(predicate, predicate_type=CHECK_TYPE):
    candidate = predicate.get("candidate")
    return {
        "_type": STATEMENT,
        "subject": (
            [{"name": "candidate-manifest.json", "digest": {"sha256": candidate["sha256"]}}]
            if candidate
            else []
        ),
        "predicateType": predicate_type,
        "predicate": predicate,
    }


def read_statement(value):
    if (
        not isinstance(value, dict)
        or value.get("_type") != STATEMENT
        or value.get("predicateType") != CHECK_TYPE
        or not isinstance(value.get("predicate"), dict)
    ):
        raise CheckError("Unsupported traceability statement")
    evidence = value["predicate"]
    if value.get("subject") != statement(evidence)["subject"]:
        raise CheckError("Statement subject differs from checked candidate")
    return evidence


def test_statement(evidence, scope_digest):
    if evidence["tests"].get("source_status") != "matched":
        raise CheckError("Cannot attest a test result without matching stable source")
    value = statement(evidence, TEST_TYPE)
    value["predicate"] = {
        "result": "PASSED" if evidence["tests"]["status"] == "passed" else "FAILED",
        "configuration": [{"name": "scope.json", "digest": {"sha256": scope_digest}}],
    }
    return value
