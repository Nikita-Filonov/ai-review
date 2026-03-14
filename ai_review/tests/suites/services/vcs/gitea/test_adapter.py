from ai_review.clients.gitea.pr.schema.comments import GiteaPRCommentSchema
from ai_review.clients.gitea.pr.schema.reviews import GiteaReviewCommentSchema
from ai_review.clients.gitea.pr.schema.user import GiteaUserSchema
from ai_review.services.vcs.gitea.adapter import (
    get_review_comment_from_gitea_comment,
    get_review_comment_from_gitea_review_comment,
    get_user_from_gitea_user,
)
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def test_get_user_from_gitea_user_maps_fields_correctly():
    user = GiteaUserSchema(id=42, login="tester")
    result = get_user_from_gitea_user(user)

    assert isinstance(result, UserSchema)
    assert result.id == 42
    assert result.username == "tester"
    assert result.name == "tester"


def test_get_user_from_gitea_user_handles_none():
    result = get_user_from_gitea_user(None)
    assert result.id is None
    assert result.username == ""
    assert result.name == ""


def test_get_review_comment_from_gitea_comment_maps_all_fields():
    comment = GiteaPRCommentSchema(
        id=10,
        body="Inline comment",
        path="src/main.py",
        line=15,
        user=GiteaUserSchema(id=1, login="dev"),
    )

    result = get_review_comment_from_gitea_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.id == 10
    assert result.body == "Inline comment"
    assert result.file == "src/main.py"
    assert result.line == 15
    assert result.thread_id == 10
    assert isinstance(result.author, UserSchema)
    assert result.author.username == "dev"


def test_get_review_comment_handles_missing_user_and_body():
    comment = GiteaPRCommentSchema(id=11, body="", path=None, line=None, user=None)

    result = get_review_comment_from_gitea_comment(comment)
    assert result.body == ""
    assert result.author.username == ""
    assert result.file is None
    assert result.line is None


def test_get_review_comment_from_gitea_review_comment_maps_all_fields():
    comment = GiteaReviewCommentSchema(
        id=601,
        body="Review inline comment",
        path="src/utils.py",
        position=42,
        user=GiteaUserSchema(id=101, login="ai-bot"),
        pull_request_review_id=500,
    )

    result = get_review_comment_from_gitea_review_comment(comment, review_id=500)

    assert isinstance(result, ReviewCommentSchema)
    assert result.id == 500
    assert result.body == "Review inline comment"
    assert result.file == "src/utils.py"
    assert result.line == 42
    assert result.parent_id == 500
    assert result.thread_id == 601
    assert isinstance(result.author, UserSchema)
    assert result.author.username == "ai-bot"


def test_get_review_comment_from_gitea_review_comment_handles_missing_optional_fields():
    comment = GiteaReviewCommentSchema(
        id=602,
        body="",
        path=None,
        position=None,
        user=None,
        pull_request_review_id=None,
    )

    result = get_review_comment_from_gitea_review_comment(comment, review_id=501)

    assert result.id == 501
    assert result.body == ""
    assert result.file is None
    assert result.line is None
    assert result.parent_id == 501
    assert result.thread_id == 602
    assert result.author.username == ""
    assert result.author.name == ""


def test_get_review_comment_from_gitea_review_comment_uses_review_id_not_comment_id():
    comment = GiteaReviewCommentSchema(
        id=999,
        body="some comment",
        pull_request_review_id=200,
    )

    result = get_review_comment_from_gitea_review_comment(comment, review_id=200)

    assert result.id == 200
    assert result.thread_id == 999
