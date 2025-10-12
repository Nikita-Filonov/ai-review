from ai_review.clients.gitea.pr.schema.comments import GiteaPRCommentSchema
from ai_review.clients.gitea.pr.schema.user import GiteaUserSchema
from ai_review.services.vcs.gitea.adapter import get_review_comment_from_gitea_comment, get_user_from_gitea_user
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
