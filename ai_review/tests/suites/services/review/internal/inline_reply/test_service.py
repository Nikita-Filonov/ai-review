from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.inline_reply.service import InlineCommentReplyService


def test_empty_output_returns_none(inline_comment_reply_service: InlineCommentReplyService):
    """Empty LLM output should return None."""
    result = inline_comment_reply_service.parse_model_output("")
    assert result is None


def test_valid_json_object_parsed(inline_comment_reply_service: InlineCommentReplyService):
    """A valid JSON object should be parsed successfully."""
    output = '{"message": "Looks good!"}'
    result = inline_comment_reply_service.parse_model_output(output)

    assert isinstance(result, InlineCommentReplySchema)
    assert result.message == "Looks good!"
    assert result.suggestion is None


def test_valid_json_with_suggestion(inline_comment_reply_service: InlineCommentReplyService):
    """Parser should correctly handle JSON with both message and suggestion."""
    output = '{"message": "Consider refactoring", "suggestion": "use helper()"}'
    result = inline_comment_reply_service.parse_model_output(output)

    assert isinstance(result, InlineCommentReplySchema)
    assert result.message == "Consider refactoring"
    assert result.suggestion == "use helper()"
    assert "```suggestion" in result.body
    assert result.message in result.body


def test_json_inside_code_block_parsed(inline_comment_reply_service: InlineCommentReplyService):
    """JSON inside a ```json code block should be extracted successfully."""
    output = """```json
    {"message": "Please add docstring"}
    ```"""
    result = inline_comment_reply_service.parse_model_output(output)

    assert isinstance(result, InlineCommentReplySchema)
    assert result.message == "Please add docstring"
    assert result.suggestion is None


def test_invalid_json_returns_none(inline_comment_reply_service: InlineCommentReplyService):
    """Invalid JSON (wrong field type) should return None."""
    output = '{"message": 12345}'
    result = inline_comment_reply_service.parse_model_output(output)
    assert result is None


def test_non_json_text_returns_none(inline_comment_reply_service: InlineCommentReplyService):
    """Non-JSON text should return None."""
    output = "some random text output"
    result = inline_comment_reply_service.parse_model_output(output)
    assert result is None


def test_json_with_empty_message_returns_none(inline_comment_reply_service: InlineCommentReplyService):
    """JSON with an empty message field should return None (violates min_length)."""
    output = '{"message": ""}'
    result = inline_comment_reply_service.parse_model_output(output)
    assert result is None


def test_message_is_trimmed(inline_comment_reply_service: InlineCommentReplyService):
    """Message should be trimmed — leading and trailing spaces removed."""
    output = '{"message": "   spaced out   "}'
    result = inline_comment_reply_service.parse_model_output(output)

    assert isinstance(result, InlineCommentReplySchema)
    assert result.message == "spaced out"
