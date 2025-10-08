from ai_review.clients.gitlab.mr.schema.discussions import GitLabDiscussionSchema
from ai_review.clients.gitlab.mr.schema.notes import GitLabNoteSchema
from ai_review.clients.gitlab.mr.schema.position import GitLabPositionSchema
from ai_review.clients.gitlab.mr.schema.user import GitLabUserSchema
from ai_review.services.vcs.gitlab.adapter import get_review_comment_from_gitlab_note
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def test_maps_all_fields_correctly():
    """Should map GitLab note and discussion into ReviewCommentSchema."""
    note = GitLabNoteSchema(
        id=123,
        body="Looks good!",
        author=GitLabUserSchema(id=10, name="Alice", username="alice"),
    )
    discussion = GitLabDiscussionSchema(
        id="42",
        notes=[note],
        position=GitLabPositionSchema(
            base_sha="AAA000",
            head_sha="BBB111",
            start_sha="CCC222",
            new_path="src/app.py",
            new_line=15,
        )
    )

    result = get_review_comment_from_gitlab_note(note, discussion)

    assert isinstance(result, ReviewCommentSchema)
    assert result.id == 123
    assert result.body == "Looks good!"
    assert result.file == "src/app.py"
    assert result.line == 15
    assert result.thread_id == "42"

    assert isinstance(result.author, UserSchema)
    assert result.author.id == 10
    assert result.author.name == "Alice"
    assert result.author.username == "alice"


def test_maps_with_missing_author():
    """Should handle note without author gracefully (default empty UserSchema)."""
    note = GitLabNoteSchema(id=1, body="Anonymous comment", author=None)
    discussion = GitLabDiscussionSchema(
        id="7",
        notes=[note],
        position=GitLabPositionSchema(
            base_sha="AAA000",
            head_sha="BBB111",
            start_sha="CCC222",
            new_path="main.py",
            new_line=3,
        ),
    )

    result = get_review_comment_from_gitlab_note(note, discussion)

    assert isinstance(result.author, UserSchema)
    assert result.author.id is None
    assert result.author.name == ""
    assert result.author.username == ""


def test_maps_with_missing_position():
    """Should handle discussion without position gracefully (file/line become None)."""
    note = GitLabNoteSchema(
        id=55,
        body="General comment",
        author=GitLabUserSchema(id=9, name="Bob", username="bob"),
    )
    discussion = GitLabDiscussionSchema(
        id="999",
        notes=[note],
        position=None,
    )

    result = get_review_comment_from_gitlab_note(note, discussion)

    assert isinstance(result, ReviewCommentSchema)
    assert result.file is None
    assert result.line is None
    assert result.thread_id == "999"


def test_maps_with_empty_body_and_defaults():
    """Should default body to empty string when note.body is empty string."""
    note = GitLabNoteSchema(id=12, body="", author=None)
    discussion = GitLabDiscussionSchema(
        id="100",
        notes=[note],
        position=None,
    )

    result = get_review_comment_from_gitlab_note(note, discussion)

    assert isinstance(result, ReviewCommentSchema)
    assert result.body == ""
    assert result.file is None
    assert result.line is None
    assert result.thread_id == "100"
    assert isinstance(result.author, UserSchema)


def test_maps_with_note_position_fallback():
    """Should use note.position when discussion.position is missing."""
    note = GitLabNoteSchema(
        id=77,
        body="Inline note with its own position",
        author=GitLabUserSchema(id=2, name="Carol", username="carol"),
        position=GitLabPositionSchema(
            base_sha="aaa",
            head_sha="bbb",
            start_sha="ccc",
            new_path="module/utils.py",
            new_line=42,
        ),
    )
    discussion = GitLabDiscussionSchema(
        id="200",
        notes=[note],
        position=None,
    )

    result = get_review_comment_from_gitlab_note(note, discussion)

    assert isinstance(result, ReviewCommentSchema)
    assert result.id == 77
    assert result.file == "module/utils.py"
    assert result.line == 42
    assert result.thread_id == "200"
    assert result.body == "Inline note with its own position"
    assert result.author.name == "Carol"
