import pytest

from ai_review.libs.diff.models import Diff
from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.diff.types import DiffServiceProtocol
from ai_review.services.git.types import GitServiceProtocol


class FakeDiffService(DiffServiceProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def parse(self, raw_diff: str) -> Diff:
        self.calls.append(("parse", {"raw_diff": raw_diff}))
        return Diff(files=[], raw=raw_diff)

    def render_file(
            self,
            file: str,
            raw_diff: str,
            base_sha: str | None = None,
            head_sha: str | None = None,
    ) -> DiffFileSchema:
        self.calls.append((
            "render_file",
            {"file": file, "raw_diff": raw_diff, "base_sha": base_sha, "head_sha": head_sha},
        ))
        return DiffFileSchema(file=file, diff=f"FAKE_DIFF_CONTENT for {file}")

    def render_files(
            self,
            git: GitServiceProtocol,
            files: list[str],
            base_sha: str,
            head_sha: str,
    ) -> list[DiffFileSchema]:
        self.calls.append((
            "render_files",
            {"git": git, "files": files, "base_sha": base_sha, "head_sha": head_sha},
        ))
        return [DiffFileSchema(file=file, diff=f"FAKE_DIFF for {file}") for file in files]


@pytest.fixture
def fake_diff_service() -> FakeDiffService:
    return FakeDiffService()
