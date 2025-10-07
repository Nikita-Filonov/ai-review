from ai_review.services.prompt.adapter import build_prompt_context_from_review_info
from ai_review.services.vcs.types import (
    ReviewInfoSchema,
    UserSchema,
    BranchRefSchema,
)


def test_build_prompt_context_from_full_review_info() -> None:
    review_info = ReviewInfoSchema(
        id=42,
        title="Fix API bug",
        description="Refactored endpoint",
        author=UserSchema(id=1, name="Alice", username="alice"),
        reviewers=[
            UserSchema(id=2, name="Bob", username="bob"),
            UserSchema(id=3, name="Charlie", username="charlie"),
        ],
        assignees=[UserSchema(id=4, name="Dave", username="dave")],
        source_branch=BranchRefSchema(ref="feature/fix-api", sha="123abc"),
        target_branch=BranchRefSchema(ref="main", sha="456def"),
        labels=["bug", "backend"],
        changed_files=["api/views.py", "api/tests.py"],
    )

    context = build_prompt_context_from_review_info(review_info)

    assert context.review_title == "Fix API bug"
    assert context.review_description == "Refactored endpoint"

    assert context.review_author_name == "Alice"
    assert context.review_author_username == "alice"

    assert context.review_reviewers == ["Bob", "Charlie"]
    assert context.review_reviewers_usernames == ["bob", "charlie"]
    assert context.review_reviewer == "Bob"  # первый ревьюер выбран корректно

    assert context.review_assignees == ["Dave"]
    assert context.review_assignees_usernames == ["dave"]

    assert context.source_branch == "feature/fix-api"
    assert context.target_branch == "main"

    assert context.labels == ["bug", "backend"]
    assert context.changed_files == ["api/views.py", "api/tests.py"]


def test_build_prompt_context_handles_no_reviewers() -> None:
    review_info = ReviewInfoSchema(
        title="Empty reviewers test",
        author=UserSchema(name="Alice", username="alice"),
        reviewers=[],
    )

    context = build_prompt_context_from_review_info(review_info)

    assert context.review_reviewer == ""
    assert context.review_reviewers == []
    assert context.review_reviewers_usernames == []
