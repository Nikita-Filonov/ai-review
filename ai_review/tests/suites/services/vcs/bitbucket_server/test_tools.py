from ai_review.clients.bitbucket_server.pr.schema.activities import BitbucketServerActivitySchema
from ai_review.clients.bitbucket_server.pr.schema.comments import (
    BitbucketServerCommentSchema,
    BitbucketServerCommentAnchorSchema,
)
from ai_review.clients.bitbucket_server.pr.schema.user import BitbucketServerUserSchema
from ai_review.services.vcs.bitbucket_server.tools import get_comments_from_activities


def _make_comment(
        comment_id: int = 1,
        text: str = "comment",
        anchor: BitbucketServerCommentAnchorSchema | None = None,
) -> BitbucketServerCommentSchema:
    return BitbucketServerCommentSchema(
        id=comment_id,
        text=text,
        author=BitbucketServerUserSchema(id=1, name="user", slug="user", display_name="User"),
        anchor=anchor,
        comments=[],
        created_date=1690000000,
        updated_date=1690000000,
    )


def _make_activity(
        activity_id: int = 1,
        action: str = "COMMENTED",
        comment: BitbucketServerCommentSchema | None = None,
) -> BitbucketServerActivitySchema:
    return BitbucketServerActivitySchema(id=activity_id, action=action, comment=comment)


def test_extracts_comments_from_commented_activities():
    """Should return comments from activities with action=COMMENTED."""
    comment = _make_comment(comment_id=10, text="Hello")
    activities = [_make_activity(activity_id=1, action="COMMENTED", comment=comment)]

    result = get_comments_from_activities(activities)

    assert len(result) == 1
    assert result[0].id == 10
    assert result[0].text == "Hello"


def test_skips_non_commented_activities():
    """Should ignore activities with action other than COMMENTED."""
    comment = _make_comment()
    activities = [
        _make_activity(activity_id=1, action="APPROVED", comment=None),
        _make_activity(activity_id=2, action="RESCOPED", comment=None),
        _make_activity(activity_id=3, action="COMMENTED", comment=comment),
    ]

    result = get_comments_from_activities(activities)

    assert len(result) == 1
    assert result[0].id == comment.id


def test_skips_commented_activity_with_none_comment():
    """Should skip COMMENTED activities where comment is None."""
    activities = [_make_activity(activity_id=1, action="COMMENTED", comment=None)]

    result = get_comments_from_activities(activities)

    assert result == []


def test_returns_empty_list_for_empty_activities():
    """Should return an empty list when there are no activities."""
    result = get_comments_from_activities([])

    assert result == []


def test_preserves_inline_and_general_comments():
    """Should return both inline (with anchor) and general (without anchor) comments."""
    general = _make_comment(comment_id=1, text="General")
    inline = _make_comment(
        comment_id=2,
        text="Inline",
        anchor=BitbucketServerCommentAnchorSchema(path="src/main.py", line=5, line_type="ADDED"),
    )
    activities = [
        _make_activity(activity_id=1, action="COMMENTED", comment=general),
        _make_activity(activity_id=2, action="COMMENTED", comment=inline),
    ]

    result = get_comments_from_activities(activities)

    assert len(result) == 2
    assert result[0].anchor is None
    assert result[1].anchor is not None
    assert result[1].anchor.path == "src/main.py"


def test_mixed_activity_types():
    """Should only extract comments from COMMENTED activities in a mixed list."""
    comment = _make_comment(comment_id=42, text="Review note")
    activities = [
        _make_activity(activity_id=1, action="OPENED", comment=None),
        _make_activity(activity_id=2, action="COMMENTED", comment=comment),
        _make_activity(activity_id=3, action="APPROVED", comment=None),
        _make_activity(activity_id=4, action="MERGED", comment=None),
    ]

    result = get_comments_from_activities(activities)

    assert len(result) == 1
    assert result[0].id == 42
