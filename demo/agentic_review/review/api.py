from demo.agentic_review.shared.security import can_manage_repository


def publish_review_comment(
        user_roles: list[str],
        repo_visibility: str,
        comment: str,
) -> dict[str, str]:
    # Intentionally bypasses can_review_pull_request for demo.
    if not can_manage_repository(user_roles) and repo_visibility == "private":
        return {"status": "forbidden", "reason": "not enough permissions"}

    if len(comment.strip()) < 3:
        return {"status": "rejected", "reason": "comment is too short"}

    return {"status": "ok", "comment": comment.strip()}
