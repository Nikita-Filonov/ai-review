from ai_review.clients.azure_devops.pr.schema.files import AzureDevOpsFilePositionSchema
from ai_review.clients.azure_devops.pr.schema.threads import (
    AzureDevOpsPRThreadSchema,
    AzureDevOpsPRCommentSchema,
    AzureDevOpsThreadContextSchema,
)
from ai_review.clients.azure_devops.pr.schema.user import AzureDevOpsUserSchema
from ai_review.services.vcs.azure_devops.adapter import (
    get_user_from_azure_devops_user,
    get_review_comment_from_azure_devops_comment,
)
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def test_maps_user_all_fields():
    """Should map Azure DevOps user to internal UserSchema correctly."""
    user = AzureDevOpsUserSchema(
        id="42",
        display_name="John Doe",
        unique_name="john.doe@corp.local",
    )

    result = get_user_from_azure_devops_user(user)

    assert isinstance(result, UserSchema)
    assert result.id == "42"
    assert result.name == "John Doe"
    assert result.username == "john.doe@corp.local"


def test_maps_none_user_to_empty_user_schema():
    """Should handle None user gracefully and fill defaults."""
    result = get_user_from_azure_devops_user(None)

    assert isinstance(result, UserSchema)
    assert result.id is None
    assert result.name == ""
    assert result.username == ""


def test_maps_all_fields_correctly_for_inline_comment():
    """Should map Azure DevOps comment and thread context to ReviewCommentSchema."""
    user = AzureDevOpsUserSchema(
        id="1",
        display_name="Reviewer",
        unique_name="reviewer@company.com",
    )
    comment = AzureDevOpsPRCommentSchema(id=101, content="Looks fine", author=user)
    thread = AzureDevOpsPRThreadSchema(
        id=55,
        comments=[comment],
        thread_context=AzureDevOpsThreadContextSchema(file_path="src/app.py"),
    )

    result = get_review_comment_from_azure_devops_comment(comment, thread)

    assert isinstance(result, ReviewCommentSchema)
    assert result.id == 101
    assert result.body == "Looks fine"
    assert result.file == "src/app.py"
    assert result.thread_id == 55
    assert isinstance(result.author, UserSchema)
    assert result.author.name == "Reviewer"


def test_handles_missing_thread_context():
    """Should handle threads without file context gracefully."""
    user = AzureDevOpsUserSchema(id="2", display_name="QA", unique_name="qa@company.com")
    comment = AzureDevOpsPRCommentSchema(id=202, content="General note", author=user)
    thread = AzureDevOpsPRThreadSchema(
        id=99,
        comments=[comment],
        thread_context=None,
    )

    result = get_review_comment_from_azure_devops_comment(comment, thread)

    assert result.file is None
    assert result.line is None
    assert result.thread_id == 99
    assert result.body == "General note"


def test_handles_missing_user():
    """Should create empty author when comment.author is None."""
    comment = AzureDevOpsPRCommentSchema(id=303, content="Anonymous comment", author=None)
    thread = AzureDevOpsPRThreadSchema(
        id=10,
        comments=[comment],
        thread_context=AzureDevOpsThreadContextSchema(file_path="src/main.py"),
    )

    result = get_review_comment_from_azure_devops_comment(comment, thread)

    assert isinstance(result.author, UserSchema)
    assert result.author.name == ""
    assert result.author.username == ""
    assert result.body == "Anonymous comment"
    assert result.thread_id == 10


def test_defaults_body_to_empty_string():
    """Should default comment body to empty string when content is None or empty."""
    user = AzureDevOpsUserSchema(id="3", display_name="Dev", unique_name="dev@corp.local")
    comment = AzureDevOpsPRCommentSchema(id=404, content="", author=user)
    thread = AzureDevOpsPRThreadSchema(
        id=11,
        comments=[comment],
        thread_context=AzureDevOpsThreadContextSchema(file_path="src/utils/helper.py"),
    )

    result = get_review_comment_from_azure_devops_comment(comment, thread)

    assert result.body == ""
    assert result.thread_id == 11
    assert result.file == "src/utils/helper.py"
    assert result.line is None


def test_maps_line_from_right_file_start_if_present():
    """Should extract line number correctly from thread context."""
    context = AzureDevOpsThreadContextSchema(
        file_path="src/module.py",
        right_file_start=AzureDevOpsFilePositionSchema(line=42),
    )
    comment = AzureDevOpsPRCommentSchema(
        id=505,
        content="Please check this line",
        author=AzureDevOpsUserSchema(id="99", display_name="Bot"),
    )
    thread = AzureDevOpsPRThreadSchema(
        id=777,
        comments=[comment],
        thread_context=context,
    )

    result = get_review_comment_from_azure_devops_comment(comment, thread)

    assert result.file == "src/module.py"
    assert result.line == 42
    assert result.thread_id == 777
    assert result.author.name == "Bot"
