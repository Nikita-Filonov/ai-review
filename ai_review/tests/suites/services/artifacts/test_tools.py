import hashlib
import re

import pytest

from ai_review.services.artifacts.tools import make_artifact_id


@pytest.mark.parametrize("text", ["hello", "some longer text", ""])
def test_make_artifact_id_format_and_sha(text: str):
    """Checks that the function returns a valid artifact ID format and correct SHA prefix."""
    artifact_id = make_artifact_id(text)

    pattern = r"^\d{4}\.\d{2}\.\d{2}_\d{2}-\d{2}-\d{2}_[0-9a-f]{8}$"
    assert re.match(pattern, artifact_id), f"Invalid format: {artifact_id}"

    expected_sha = hashlib.sha1(text.encode()).hexdigest()[:8]
    assert artifact_id.endswith(expected_sha)


def test_make_artifact_id_is_deterministic_for_same_input():
    """Checks that the SHA part is deterministic (identical for the same input)."""
    sha1 = hashlib.sha1("repeatable".encode()).hexdigest()[:8]
    artifact_id1 = make_artifact_id("repeatable")
    artifact_id2 = make_artifact_id("repeatable")

    assert artifact_id1.split("_")[2] == sha1
    assert artifact_id2.split("_")[2] == sha1
