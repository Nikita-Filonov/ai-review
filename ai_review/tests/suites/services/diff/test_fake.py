from ai_review.tests.fixtures.services.git import FakeGitService
from ai_review.tests.fixtures.services.diff import FakeDiffService


def test_fake_diff_records_parse_and_render_inputs() -> None:
    git = FakeGitService()
    diff = FakeDiffService()
    assert diff.parse("raw").raw == "raw"
    assert diff.render_file("file.py", "raw").file == "file.py"
    assert [item.file for item in diff.render_files(git, ["file.py"], "a", "b")] == ["file.py"]
    assert [name for name, _ in diff.calls] == ["parse", "render_file", "render_files"]
