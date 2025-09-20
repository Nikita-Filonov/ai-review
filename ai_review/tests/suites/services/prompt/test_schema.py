from ai_review.services.prompt.schema import PromptContextSchema


def test_apply_format_inserts_variables() -> None:
    context = PromptContextSchema(
        merge_request_title="My MR",
        merge_request_author_username="nikita"
    )
    template = "Title: {merge_request_title}, Author: @{merge_request_author_username}"
    result = context.apply_format(template)
    assert result == "Title: My MR, Author: @nikita"


def test_apply_format_with_lists() -> None:
    context = PromptContextSchema(
        merge_request_reviewers=["Alice", "Bob"],
        merge_request_reviewers_usernames=["alice", "bob"],
        labels=["bug", "feature"],
        changed_files=["a.py", "b.py"],
    )
    template = (
        "Reviewers: {merge_request_reviewers}\n"
        "Usernames: {merge_request_reviewers_usernames}\n"
        "Labels: {labels}\n"
        "Files: {changed_files}"
    )
    result = context.apply_format(template)
    assert "Alice, Bob" in result
    assert "alice, bob" in result
    assert "bug, feature" in result
    assert "a.py, b.py" in result


def test_apply_format_handles_missing_fields() -> None:
    context = PromptContextSchema()
    template = "Title: {merge_request_title}, Reviewer: {merge_request_reviewer}"
    result = context.apply_format(template)
    assert result == "Title: , Reviewer: "
