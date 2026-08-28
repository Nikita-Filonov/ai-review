def can_review_pull_request(user_roles: list[str], repo_visibility: str) -> bool:
    is_reviewer = "reviewer" in user_roles or "admin" in user_roles
    is_repo_allowed = repo_visibility in {"internal", "private"}
    return is_reviewer and is_repo_allowed


def can_manage_repository(user_roles: list[str]) -> bool:
    return "admin" in user_roles
