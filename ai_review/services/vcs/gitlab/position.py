from ai_review.clients.gitlab.mr.schema.changes import GitLabDiffRefsSchema, GitLabMRChangeSchema
from ai_review.clients.gitlab.mr.schema.position import GitLabPositionSchema
from ai_review.libs.diff.parser import DiffParser
from ai_review.libs.logger import get_logger
from ai_review.services.diff.tools import normalize_file_path

logger = get_logger("GITLAB_POSITION")


def find_change(changes: list[GitLabMRChangeSchema], file: str) -> GitLabMRChangeSchema | None:
    """Find the MR change entry describing a file, matching either side of a rename."""
    target = normalize_file_path(file)

    for change in changes:
        if normalize_file_path(change.new_path or "") == target:
            return change
        if normalize_file_path(change.old_path or "") == target:
            return change

    return None


def build_inline_position(
        *,
        file: str,
        line: int,
        diff_refs: GitLabDiffRefsSchema,
        changes: list[GitLabMRChangeSchema],
) -> GitLabPositionSchema:
    """
    Build the diff position of an inline comment.

    GitLab turns a text position into a line code by looking for the diff line
    carrying exactly the given `old_line` and `new_line`. An added line has no
    counterpart in the old file, so `new_line` alone identifies it. An unchanged
    line carries both numbers, so `new_line` alone matches nothing and the note
    is rejected with `line_code can't be blank, must be a valid line code`.
    Resolving the line against the diff GitLab itself reported lets us send both
    numbers, and lets us address a removed line by its old number.

    When the line cannot be resolved — the file is absent from the changes
    payload, GitLab omitted the diff body, or the body does not parse — the
    position keeps `new_path` and `new_line` only. That is what the caller sent
    before, so such comments keep taking the same path through the inline
    fallback as they do today.
    """
    position = GitLabPositionSchema(
        position_type="text",
        base_sha=diff_refs.base_sha,
        head_sha=diff_refs.head_sha,
        start_sha=diff_refs.start_sha,
        new_path=file,
        new_line=line,
    )

    change = find_change(changes, file)
    if change is None or not change.diff:
        logger.warning(f"No MR diff available for {file}, cannot resolve the old line of {file}:{line}")
        return position

    try:
        # Resolution is best effort: a diff we cannot parse must never keep a
        # comment from being created.
        diff = DiffParser.parse(change.diff)
    except Exception as error:
        logger.warning(f"Failed to parse the MR diff of {file}: {error}")
        return position

    if not diff.files:
        logger.warning(f"MR diff of {file} contains no hunks, cannot resolve the old line of {file}:{line}")
        return position

    line_position = diff.files[0].find_line_position(line)
    if line_position is None:
        logger.warning(f"Line {line} is not part of the MR diff of {file}")
        return position

    return position.model_copy(
        update={
            "old_path": change.old_path or file,
            "new_path": change.new_path or file,
            "old_line": line_position.old_line,
            "new_line": line_position.new_line,
        }
    )
