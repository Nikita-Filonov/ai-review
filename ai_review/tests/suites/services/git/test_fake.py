from ai_review.tests.fixtures.services.git import FakeGitService


def test_fake_git_returns_configured_results() -> None:
    git = FakeGitService(
        responses={
            "get_diff": "all diff",
            "get_diff_for_file": "file diff",
            "get_changed_files": ["file.py"],
            "get_renamed_files": ["renamed.py"],
            "get_file_at_commit": "contents",
        }
    )
    assert git.get_diff("a", "b") == "all diff"
    assert git.get_diff_for_file("a", "b", "file.py") == "file diff"
    assert git.get_changed_files("a", "b") == ["file.py"]
    assert git.get_renamed_files("a", "b") == ["renamed.py"]
    assert git.get_file_at_commit("file.py", "b") == "contents"
    assert [name for name, _ in git.calls] == [
        "get_diff",
        "get_diff_for_file",
        "get_changed_files",
        "get_renamed_files",
        "get_file_at_commit",
    ]
