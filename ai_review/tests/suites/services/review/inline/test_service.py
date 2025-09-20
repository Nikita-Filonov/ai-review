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
