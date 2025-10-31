from ai_review.clients.bitbucket_cloud.pr.schema.comments import (
    BitbucketCloudPRCommentSchema,
    BitbucketCloudCommentContentSchema,
    BitbucketCloudCommentInlineSchema,
    BitbucketCloudCommentParentSchema,
)
from ai_review.clients.bitbucket_cloud.pr.schema.user import BitbucketCloudUserSchema
from ai_review.services.vcs.bitbucket_cloud.adapter import get_review_comment_from_bitbucket_pr_comment
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def test_maps_all_fields_correctly():
    """Should map Bitbucket PR comment with all fields correctly."""
    comment = BitbucketCloudPRCommentSchema(
        id=101,
        user=BitbucketCloudUserSchema(uuid="u-123", display_name="Alice", nickname="alice"),
        parent=None,
        inline=BitbucketCloudCommentInlineSchema(path="src/utils.py", to_line=10),
        content=BitbucketCloudCommentContentSchema(raw="Looks good"),
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
    comment = BitbucketCloudPRCommentSchema(
        id=202,
        user=BitbucketCloudUserSchema(uuid="u-456", display_name="Bob", nickname="bob"),
        parent=BitbucketCloudCommentParentSchema(id=101),
        inline=BitbucketCloudCommentInlineSchema(path="src/main.py", to_line=20),
        content=BitbucketCloudCommentContentSchema(raw="I agree"),
    )

    result = get_review_comment_from_bitbucket_pr_comment(comment)

    assert result.parent_id == 101
    assert result.thread_id == 101
    assert result.id == 202
    assert result.file == "src/main.py"
    assert result.line == 20


def test_maps_without_user():
    """Should handle missing user gracefully."""
    comment = BitbucketCloudPRCommentSchema(
        id=303,
        user=None,
        parent=None,
        inline=BitbucketCloudCommentInlineSchema(path="src/app.py", to_line=5),
        content=BitbucketCloudCommentContentSchema(raw="Anonymous feedback"),
    )

    result = get_review_comment_from_bitbucket_pr_comment(comment)

    assert isinstance(result.author, UserSchema)
    assert result.author.id is None
    assert result.author.name == ""
    assert result.author.username == ""


def test_maps_without_inline():
    """Should handle missing inline gracefully (file and line None)."""
    comment = BitbucketCloudPRCommentSchema(
        id=404,
        user=BitbucketCloudUserSchema(uuid="u-789", display_name="Charlie", nickname="charlie"),
        parent=None,
        inline=None,
        content=BitbucketCloudCommentContentSchema(raw="General comment"),
    )

    result = get_review_comment_from_bitbucket_pr_comment(comment)

    assert result.file is None
    assert result.line is None
    assert result.thread_id == 404


def test_maps_with_empty_body_and_defaults():
    """Should default body to empty string if content.raw is empty or None."""
    comment = BitbucketCloudPRCommentSchema(
        id=505,
        user=None,
        parent=None,
        inline=None,
        content=BitbucketCloudCommentContentSchema(raw="", html=None, markup=None),
    )

    result = get_review_comment_from_bitbucket_pr_comment(comment)

    assert isinstance(result, ReviewCommentSchema)
    assert result.body == ""
    assert result.file is None
    assert result.line is None
    assert result.thread_id == 505
    assert isinstance(result.author, UserSchema)
