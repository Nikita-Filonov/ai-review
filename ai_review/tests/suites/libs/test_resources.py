import io
import importlib.metadata
from pathlib import Path

import pytest

from ai_review.libs.resources import load_resource


def test_load_resource_returns_path_for_filesystem_package(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resource = tmp_path / "prompt.md"
    resource.write_text("prompt", encoding="utf-8")
    monkeypatch.setattr("ai_review.libs.resources.importlib.resources.files", lambda _: tmp_path)

    assert load_resource("example", "prompt.md") == resource


def test_load_resource_copies_non_filesystem_resource(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class VirtualResource:
        def __truediv__(self, name: str) -> "VirtualResource":
            assert name == "prompt.md"
            return self

        def open(self, mode: str) -> io.BytesIO:
            assert mode == "rb"
            return io.BytesIO(b"virtual prompt")

    monkeypatch.setattr("ai_review.libs.resources.importlib.resources.files", lambda _: VirtualResource())
    monkeypatch.setattr("ai_review.libs.resources.tempfile.gettempdir", lambda: str(tmp_path))

    path = load_resource("example", "prompt.md")
    assert path == tmp_path / "prompt.md"
    assert path.read_bytes() == b"virtual prompt"


@pytest.mark.parametrize("fallback", ["docs/prompt.md", None])
def test_load_resource_handles_missing_package(
    fallback: str | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing(_: str) -> None:
        raise importlib.metadata.PackageNotFoundError("example")

    monkeypatch.setattr("ai_review.libs.resources.importlib.resources.files", missing)
    if fallback is None:
        with pytest.raises(importlib.metadata.PackageNotFoundError):
            load_resource("example", "prompt.md")
    else:
        assert load_resource("example", "prompt.md", fallback) == Path.cwd() / fallback
