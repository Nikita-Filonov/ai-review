from ai_review.clients.bitbucket.pr.schema.comments import (
    BitbucketPRCommentSchema,
    BitbucketCommentContentSchema,
    BitbucketCommentInlineSchema,
    BitbucketCommentParentSchema,
)
from ai_review.clients.bitbucket.pr.schema.user import BitbucketUserSchema
from ai_review.services.vcs.bitbucket.adapter import get_review_comment_from_bitbucket_pr_comment
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def test_maps_all_fields_correctly():
    """Should map Bitbucket PR comment with all fields correctly."""
    comment = BitbucketPRCommentSchema(
        id=101,
        user=BitbucketUserSchema(uuid="u-123", display_name="Alice", nickname="alice"),
        parent=None,
        inline=BitbucketCommentInlineSchema(path="src/utils.py", to_line=10),
        content=BitbucketCommentContentSchema(raw="Looks good"),
    )

    result = get_review_comment_from_bitbucket_pr_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.id == 101
    assert result.body == "Looks good"
    assert result.file == "src/utils.py"
    assert result.line == 10
    assert result.parent_id is None
    assert result.thread_id == 101

    assert isinstance(result.author, UserSchema)
    assert result.author.id == "u-123"
    assert result.author.name == "Alice"
    assert result.author.username == "alice"


def test_maps_with_parent_comment():
    """Should set parent_id and use it as thread_id."""
    comment = BitbucketPRCommentSchema(
        id=202,
        user=BitbucketUserSchema(uuid="u-456", display_name="Bob", nickname="bob"),
        parent=BitbucketCommentParentSchema(id=101),
        inline=BitbucketCommentInlineSchema(path="src/main.py", to_line=20),
        content=BitbucketCommentContentSchema(raw="I agree"),
    )

    result = get_review_comment_from_bitbucket_pr_comment(comment)

    assert result.parent_id == 101
    assert result.thread_id == 101
    assert result.id == 202
    assert result.file == "src/main.py"
    assert result.line == 20


def test_maps_without_user():
    """Should handle missing user gracefully."""
    comment = BitbucketPRCommentSchema(
        id=303,
        user=None,
        parent=None,
        inline=BitbucketCommentInlineSchema(path="src/app.py", to_line=5),
        content=BitbucketCommentContentSchema(raw="Anonymous feedback"),
    )

    result = get_review_comment_from_bitbucket_pr_comment(comment)

    assert isinstance(result.author, UserSchema)
    assert result.author.id is None
    assert result.author.name == ""
    assert result.author.username == ""


def test_maps_without_inline():
    """Should handle missing inline gracefully (file and line None)."""
    comment = BitbucketPRCommentSchema(
        id=404,
        user=BitbucketUserSchema(uuid="u-789", display_name="Charlie", nickname="charlie"),
        parent=None,
        inline=None,
        content=BitbucketCommentContentSchema(raw="General comment"),
    )

    result = get_review_comment_from_bitbucket_pr_comment(comment)

    assert result.file is None
    assert result.line is None
    assert result.thread_id == 404


def test_maps_with_empty_body_and_defaults():
    """Should default body to empty string if content.raw is empty or None."""
    comment = BitbucketPRCommentSchema(
        id=505,
        user=None,
        parent=None,
        inline=None,
        content=BitbucketCommentContentSchema(raw="", html=None, markup=None),
    )

    result = get_review_comment_from_bitbucket_pr_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.body == ""
    assert result.file is None
    assert result.line is None
    assert result.thread_id == 505
    assert isinstance(result.author, UserSchema)
