from ai_review.services.review.inline.schema import InlineCommentListSchema
from ai_review.services.review.inline.service import InlineCommentService


def test_empty_output_returns_empty_list():
    result = InlineCommentService.parse_model_output("")
    assert isinstance(result, InlineCommentListSchema)
    assert result.root == []


def test_valid_json_array_parsed():
    json_output = '[{"file": "a.py", "line": 1, "message": "use f-string"}]'
    result = InlineCommentService.parse_model_output(json_output)
    assert len(result.root) == 1
    assert result.root[0].file == "a.py"
    assert result.root[0].line == 1
    assert result.root[0].message == "use f-string"


def test_json_inside_code_block_parsed():
    output = """```json
    [
      {"file": "b.py", "line": 42, "message": "check for None"}
    ]
    ```"""
    result = InlineCommentService.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].file == "b.py"
    assert result.root[0].line == 42


def test_non_json_but_array_inside_text():
    output = "some explanation...\n[ {\"file\": \"c.py\", \"line\": 7, \"message\": \"fix this\"} ]\nend"
    result = InlineCommentService.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].file == "c.py"
    assert result.root[0].line == 7


def test_invalid_json_array_logs_and_returns_empty():
    output = '[{"file": "d.py", "line": "oops", "message": "bad"}]'
    result = InlineCommentService.parse_model_output(output)
    assert result.root == []


def test_no_json_array_found_logs_and_returns_empty():
    output = "this is not json at all"
    result = InlineCommentService.parse_model_output(output)
    assert result.root == []


def test_json_with_raw_newline_sanitized():
    output = '[{"file": "e.py", "line": 3, "message": "line1\nline2"}]'
    result = InlineCommentService.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].file == "e.py"
    assert result.root[0].line == 3
    assert result.root[0].message == "line1\nline2"


def test_json_with_tab_character_sanitized():
    output = '[{"file": "f.py", "line": 4, "message": "a\tb"}]'
    result = InlineCommentService.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].message == "a\tb"


def test_json_with_null_byte_sanitized():
    raw = "abc\0def"
    output = f'[{{"file": "g.py", "line": 5, "message": "{raw}"}}]'
    result = InlineCommentService.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].message == "abc\0def"


def test_json_with_multiple_control_chars():
    raw = "x\n\ry\t\0z"
    output = f'[{{"file": "h.py", "line": 6, "message": "{raw}"}}]'
    result = InlineCommentService.parse_model_output(output)
    assert len(result.root) == 1
    assert result.root[0].message == "x\n\ry\t\0z"


def test_try_parse_valid_json():
    raw = '[{"file": "ok.py", "line": 1, "message": "all good"}]'
    result = InlineCommentService.try_parse_model_output(raw)
    assert isinstance(result, InlineCommentListSchema)
    assert len(result.root) == 1
    assert result.root[0].file == "ok.py"
    assert result.root[0].line == 1
    assert result.root[0].message == "all good"


def test_try_parse_needs_sanitization():
    raw = '[{"file": "bad.py", "line": 2, "message": "line1\nline2"}]'
    result = InlineCommentService.try_parse_model_output(raw)
    assert result is not None
    assert result.root[0].file == "bad.py"
    assert result.root[0].line == 2
    assert result.root[0].message == "line1\nline2"
    assert "line1" in result.root[0].message


def test_try_parse_totally_invalid_returns_none():
    raw = "this is not json at all"
    result = InlineCommentService.try_parse_model_output(raw)
    assert result is None
