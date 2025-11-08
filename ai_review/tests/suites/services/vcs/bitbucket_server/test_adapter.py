from ai_review.clients.bitbucket_server.pr.schema.comments import (
    BitbucketServerCommentSchema,
    BitbucketServerCommentAnchorSchema,
)
from ai_review.clients.bitbucket_server.pr.schema.user import BitbucketServerUserSchema
from ai_review.services.vcs.bitbucket_server.adapter import get_review_comment_from_bitbucket_server_comment
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def test_maps_all_fields_correctly():
    """Should map Bitbucket Server comment with all fields correctly."""
    comment = BitbucketServerCommentSchema(
        id=101,
        text="Looks good",
        author=BitbucketServerUserSchema(
            id=1,
            name="alice",
            slug="alice",
            display_name="Alice",
        ),
        anchor=BitbucketServerCommentAnchorSchema(path="src/utils.py", line=10, line_type="ADDED"),
        comments=[],
        created_date=1690000000,
        updated_date=1690000001,
    )

    result = get_review_comment_from_bitbucket_server_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.id == 101
    assert result.body == "Looks good"
    assert result.file == "src/utils.py"
    assert result.line == 10
    assert result.parent_id is None
    assert result.thread_id == 101

    assert isinstance(result.author, UserSchema)
    assert result.author.id == 1
    assert result.author.name == "Alice"
    assert result.author.username == "alice"


def test_maps_author_with_missing_fields():
    """Should handle partially filled author fields gracefully."""
    comment = BitbucketServerCommentSchema(
        id=202,
        text="Anonymous-like comment",
        author=BitbucketServerUserSchema(
            id=None,
            name="",
            slug=None,
            display_name="",
        ),
        anchor=BitbucketServerCommentAnchorSchema(path="src/app.py", line=15, line_type="ADDED"),
        comments=[],
        created_date=1690000004,
        updated_date=1690000005,
    )

    result = get_review_comment_from_bitbucket_server_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.author.id is None
    assert result.author.name == ""
    assert result.author.username == ""


def test_maps_without_anchor():
    """Should handle missing anchor gracefully."""
    comment = BitbucketServerCommentSchema(
        id=303,
        text="General feedback",
        author=BitbucketServerUserSchema(
            id=4,
            name="dave",
            slug="dave",
            display_name="Dave",
        ),
        anchor=None,
        comments=[],
        created_date=1690000006,
        updated_date=1690000007,
    )

    result = get_review_comment_from_bitbucket_server_comment(comment)

    assert result.file is None
    assert result.line is None
    assert result.thread_id == 303


def test_maps_empty_text_defaults_to_empty_body():
    """Should default empty text to empty body."""
    comment = BitbucketServerCommentSchema(
        id=404,
        text="",
        author=BitbucketServerUserSchema(
            id=7,
            name="ghost",
            slug="ghost",
            display_name="Ghost",
        ),
        anchor=None,
        comments=[],
        created_date=1690000008,
        updated_date=1690000009,
    )

    result = get_review_comment_from_bitbucket_server_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.body == ""
    assert result.file is None
    assert result.line is None
    assert result.thread_id == 404
