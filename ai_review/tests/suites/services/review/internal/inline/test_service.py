from ai_review.services.review.internal.inline.schema import InlineCommentListSchema
from ai_review.services.review.internal.inline.service import InlineCommentService


def test_empty_output_returns_empty_list(inline_comment_service: InlineCommentService):
    result = inline_comment_service.parse_model_output("")
    assert isinstance(result, InlineCommentListSchema)
    assert result.root == []


def test_valid_json_array_parsed(inline_comment_service: InlineCommentService):
    json_output = '[{"file": "a.py", "line": 1, "message": "use f-string"}]'
    result = inline_comment_service.parse_model_output(json_output)
    assert len(result.root) == 1
    assert result.root[0].file == "a.py"
    assert result.root[0].line == 1
    assert result.root[0].message == "use f-string"


def test_json_inside_code_block_parsed(inline_comment_service: InlineCommentService):
    output = """```json
    [
      {"file": "b.py", "line": 42, "message": "check for None"}
    ]
    ```"""
    result = inline_comment_service.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].file == "b.py"
    assert result.root[0].line == 42


def test_non_json_but_array_inside_text(inline_comment_service: InlineCommentService):
    output = "some explanation...\n[ {\"file\": \"c.py\", \"line\": 7, \"message\": \"fix this\"} ]\nend"
    result = inline_comment_service.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].file == "c.py"
    assert result.root[0].line == 7


def test_invalid_json_array_logs_and_returns_empty(inline_comment_service: InlineCommentService):
    output = '[{"file": "d.py", "line": "oops", "message": "bad"}]'
    result = inline_comment_service.parse_model_output(output)
    assert result.root == []


def test_no_json_array_found_logs_and_returns_empty(inline_comment_service: InlineCommentService):
    output = "this is not json at all"
    result = inline_comment_service.parse_model_output(output)
    assert result.root == []


def test_json_with_raw_newline_sanitized(inline_comment_service: InlineCommentService):
    output = '[{"file": "e.py", "line": 3, "message": "line1\nline2"}]'
    result = inline_comment_service.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].file == "e.py"
    assert result.root[0].line == 3
    assert result.root[0].message == "line1\nline2"


def test_json_with_tab_character_sanitized(inline_comment_service: InlineCommentService):
    output = '[{"file": "f.py", "line": 4, "message": "a\tb"}]'
    result = inline_comment_service.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].message == "a\tb"


def test_json_with_null_byte_sanitized(inline_comment_service: InlineCommentService):
    raw = "abc\0def"
    output = f'[{{"file": "g.py", "line": 5, "message": "{raw}"}}]'
    result = inline_comment_service.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].message == "abc\0def"


def test_json_with_multiple_control_chars(inline_comment_service: InlineCommentService):
    raw = "x\n\ry\t\0z"
    output = f'[{{"file": "h.py", "line": 6, "message": "{raw}"}}]'
    result = inline_comment_service.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].message == "x\n\ry\t\0z"
