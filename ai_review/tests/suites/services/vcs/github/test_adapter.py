from ai_review.clients.github.pr.schema.comments import (
    GitHubPRCommentSchema,
    GitHubIssueCommentSchema,
)
from ai_review.clients.github.pr.schema.user import GitHubUserSchema
from ai_review.services.vcs.github.adapter import (
    get_review_comment_from_github_pr_comment,
    get_review_comment_from_github_issue_comment,
)
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def test_maps_all_fields_correctly_for_pr_comment():
    """Should map GitHub PR comment with all fields correctly."""
    comment = GitHubPRCommentSchema(
        id=101,
        body="Looks fine to me",
        path="src/utils.py",
        line=42,
        user=GitHubUserSchema(id=7, login="alice"),
        in_reply_to_id=None,
    )

    result = get_review_comment_from_github_pr_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.id == 101
    assert result.body == "Looks fine to me"
    assert result.file == "src/utils.py"
    assert result.line == 42
    assert result.parent_id is None
    assert result.thread_id == 101

    assert isinstance(result.author, UserSchema)
    assert result.author.id == 7
    assert result.author.name == "alice"
    assert result.author.username == "alice"


def test_maps_reply_comment_with_parent_id():
    """Should assign parent_id and use it as thread_id for replies."""
    comment = GitHubPRCommentSchema(
        id=202,
        body="Agreed with above",
        path="src/main.py",
        line=10,
        user=GitHubUserSchema(id=8, login="bob"),
        in_reply_to_id=101,
    )

    result = get_review_comment_from_github_pr_comment(comment)

    assert result.parent_id == 101
    assert result.thread_id == 101
    assert result.id == 202


def test_maps_comment_without_user():
    """Should handle missing user gracefully."""
    comment = GitHubPRCommentSchema(
        id=303,
        body="Anonymous feedback",
        path="src/app.py",
        line=20,
        user=None,
        in_reply_to_id=None,
    )

    result = get_review_comment_from_github_pr_comment(comment)

    assert isinstance(result.author, UserSchema)
    assert result.author.id is None
    assert result.author.name == ""
    assert result.author.username == ""


def test_maps_comment_with_empty_body():
    """Should default body to empty string if it's empty or None."""
    comment = GitHubPRCommentSchema(
        id=404,
        body="",
        path=None,
        line=None,
        user=GitHubUserSchema(id=1, login="bot"),
        in_reply_to_id=None,
    )

    result = get_review_comment_from_github_pr_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.body == ""
    assert result.file is None
    assert result.line is None
    assert result.thread_id == 404


def test_maps_issue_comment_all_fields():
    """Should map GitHub issue-level comment correctly."""
    comment = GitHubIssueCommentSchema(
        id=555,
        body="Top-level discussion",
        user=GitHubUserSchema(id=9, login="charlie"),
    )

    result = get_review_comment_from_github_issue_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.id == 555
    assert result.body == "Top-level discussion"
    assert result.thread_id == 555
    assert isinstance(result.author, UserSchema)


def test_maps_issue_comment_with_empty_body():
    """Should default empty body to empty string."""
    comment = GitHubIssueCommentSchema(id=666, body="", user=None)

    result = get_review_comment_from_github_issue_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.id == 666
    assert result.body == ""
    assert result.thread_id == 666


def test_issue_comment_without_user_is_handled():
    """Should create empty UserSchema when GitHub issue comment has no user."""
    comment = GitHubIssueCommentSchema(
        id=777,
        body="General feedback",
        user=None,
    )

    result = get_review_comment_from_github_issue_comment(comment)

    assert isinstance(result.author, UserSchema)
    assert result.author.id is None
    assert result.author.name == ""
    assert result.author.username == ""
    assert result.body == "General feedback"
    assert result.thread_id == 777


def test_pr_comment_with_parent_and_missing_file_line():
    """Should handle replies without path/line gracefully."""
    comment = GitHubPRCommentSchema(
        id=999,
        body="Follow-up question",
        path=None,
        line=None,
        user=GitHubUserSchema(id=10, login="eve"),
        in_reply_to_id=101,
    )

    result = get_review_comment_from_github_pr_comment(comment)

    assert result.parent_id == 101
    assert result.thread_id == 101
    assert result.file is None
    assert result.line is None
    assert result.body == "Follow-up question"
    assert result.author.username == "eve"
