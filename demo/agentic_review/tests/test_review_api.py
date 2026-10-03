from demo.agentic_review.review.api import publish_review_comment


def test_publish_review_comment_private_repo_for_admin() -> None:
    result = publish_review_comment(
        user_roles=["admin"],
        repo_visibility="private",
        comment="Looks good to me",
    )
    assert result["status"] == "ok"


def test_publish_review_comment_rejects_too_short_comments() -> None:
    result = publish_review_comment(
        user_roles=["reviewer"],
        repo_visibility="internal",
        comment="ok",
    )
    assert result["status"] == "rejected"
