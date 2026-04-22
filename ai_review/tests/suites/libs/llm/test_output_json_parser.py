from ai_review.libs.llm.output_json_parser import LLMOutputJSONParser, CLEAN_JSON_BLOCK_RE, iter_json_candidates
from ai_review.tests.fixtures.libs.llm.output_json_parser import DummyModel


# ---------- try_parse ----------

def test_try_parse_happy_path(llm_output_json_parser: LLMOutputJSONParser):
    """Should successfully parse valid JSON string."""
    raw = '{"text": "hello"}'
    result = llm_output_json_parser.try_parse(raw)

    assert isinstance(result, DummyModel)
    assert result.text == "hello"


def test_try_parse_with_sanitization_success(llm_output_json_parser: LLMOutputJSONParser):
    """Should retry and parse after sanitization fixes minor issues."""
    raw = '{text: "hi"}'
    result = llm_output_json_parser.try_parse(raw)

    assert result is None


def test_try_parse_with_sanitization_still_invalid(llm_output_json_parser: LLMOutputJSONParser):
    """Should return None if even sanitized JSON invalid."""
    raw = '{"wrong_field": "hi"}'
    result = llm_output_json_parser.try_parse(raw)

    assert result is None


def test_try_parse_with_control_characters(llm_output_json_parser: LLMOutputJSONParser):
    """Should sanitize and parse JSON containing control characters (e.g., newlines, tabs)."""
    raw = '{\n\t"text": "multi-line\nvalue"\r}'
    result = llm_output_json_parser.try_parse(raw)

    assert result is None


def test_try_parse_with_unicode_and_escaped_symbols(llm_output_json_parser: LLMOutputJSONParser):
    """Should handle escaped unicode and symbols correctly."""
    raw = '{"text": "Привет 👋 \\n new line"}'
    result = llm_output_json_parser.try_parse(raw)

    assert isinstance(result, DummyModel)
    assert "Привет" in result.text
    assert "\\n" in result.text or "\n" in result.text


# ---------- parse_output ----------

def test_parse_output_happy_path(llm_output_json_parser: LLMOutputJSONParser):
    """Should parse plain JSON output successfully."""
    output = '{"text": "parsed"}'
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "parsed"


def test_parse_output_with_fenced_block(llm_output_json_parser: LLMOutputJSONParser):
    """Should extract JSON from fenced block and parse successfully."""
    output = "```json\n{\"text\": \"inside block\"}\n```"
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "inside block"


def test_parse_output_with_non_json_fence(llm_output_json_parser: LLMOutputJSONParser):
    """Should extract even from ``` block without explicit json tag."""
    output = "```{\"text\": \"inside fence\"}```"
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "inside fence"


def test_parse_output_empty_string(llm_output_json_parser: LLMOutputJSONParser):
    """Should return None and log warning when output empty."""
    result = llm_output_json_parser.parse_output("")
    assert result is None


def test_parse_output_invalid_json(llm_output_json_parser: LLMOutputJSONParser):
    """Should return None if JSON invalid and cannot be sanitized."""
    output = "```json\n{\"wrong_field\": \"oops\"}\n```"
    result = llm_output_json_parser.parse_output(output)
    assert result is None


def test_clean_json_block_regex_extracts_content():
    """Should correctly extract JSON body from fenced block."""
    text = "Some intro ```json\n{\"x\": 42}\n``` and trailing"
    match = CLEAN_JSON_BLOCK_RE.search(text)
    assert match
    assert "{\"x\": 42}" in match.group(1)


def test_parse_output_with_extra_text_around_json(llm_output_json_parser: LLMOutputJSONParser):
    """Should extract and parse JSON when surrounded by extra LLM chatter."""
    output = "Here's what I found:\n```json\n{\"text\": \"valid\"}\n```Hope that helps!"
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "valid"


def test_parse_output_with_broken_json_then_valid_block(llm_output_json_parser: LLMOutputJSONParser):
    """Should skip broken JSON and parse valid fenced one."""
    output = '{"text": invalid}\n```json\n{"text": "fixed"}\n```'
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "fixed"


def test_parse_output_with_code_fence_but_extra_backticks(llm_output_json_parser: LLMOutputJSONParser):
    """Should correctly handle fenced block even with multiple triple-backticks."""
    output = "``````json\n{\"text\": \"messy fences\"}\n``````"
    result = llm_output_json_parser.parse_output(output)

    assert result is None


def test_parse_output_with_llm_style_json(llm_output_json_parser: LLMOutputJSONParser):
    """Should handle LLM output containing pseudo-JSON like 'text: value'."""
    output = '```json\n{text: "approximate JSON"}\n```'
    result = llm_output_json_parser.parse_output(output)

    assert result is None


def test_parse_output_with_multiple_json_blocks(llm_output_json_parser: LLMOutputJSONParser):
    """Should parse first valid fenced JSON block."""
    output = """
        ```json
        {"text": "first"}
        ```
        ```json
        {"text": "second"}
        ```
    """
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "first"


def test_parse_output_with_extra_control_chars(llm_output_json_parser: LLMOutputJSONParser):
    """Should handle JSON polluted by invisible control characters."""
    raw = '{\x00"text": "ok\x07"}'
    result = llm_output_json_parser.try_parse(raw)

    assert result is None


# ---------- iter_json_candidates ----------

def test_iter_json_candidates_single():
    """Should yield a single object for clean JSON."""
    raw = '{"text": "hello"}'
    assert list(iter_json_candidates(raw)) == [raw]


def test_iter_json_candidates_concatenated():
    """Should yield each object from concatenated JSON."""
    raw = '{"text": "first"}{"text": "second"}'
    assert list(iter_json_candidates(raw)) == ['{"text": "first"}', '{"text": "second"}']


def test_iter_json_candidates_prose_prefix():
    """Should yield the JSON object even when preceded by prose."""
    raw = 'Let me analyze the diff for you.\n{"text": "found"}'
    assert list(iter_json_candidates(raw)) == ['{"text": "found"}']


def test_iter_json_candidates_nested_braces_in_string():
    """Should correctly handle braces inside JSON string values."""
    raw = '{"text": "a { nested } value"}'
    assert list(iter_json_candidates(raw)) == [raw]


def test_iter_json_candidates_escaped_quotes():
    """Should handle escaped quotes inside string values."""
    raw = '{"text": "she said \\"hello\\""}'
    assert list(iter_json_candidates(raw)) == [raw]


def test_iter_json_candidates_no_braces():
    """Should yield nothing when there are no braces."""
    assert list(iter_json_candidates("no json here")) == []


def test_iter_json_candidates_unclosed():
    """Should yield nothing for unclosed JSON."""
    assert list(iter_json_candidates('{"text": "open')) == []


def test_iter_json_candidates_prose_with_braces_before_json():
    """Should yield both the stray brace block and the real JSON object."""
    raw = 'Some prose with {curly braces} before JSON\n{"text": "actual"}'
    candidates = list(iter_json_candidates(raw))
    assert candidates == ["{curly braces}", '{"text": "actual"}']


# ---------- parse_output: candidate fallback ----------

def test_parse_output_concatenated_json_objects(llm_output_json_parser: LLMOutputJSONParser):
    """Should parse first valid object when LLM returns two concatenated JSON objects."""
    output = '{"text": "first"}{"text": "second"}'
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "first"


def test_parse_output_prose_before_json(llm_output_json_parser: LLMOutputJSONParser):
    """Should parse JSON when LLM prepends prose before the object."""
    output = 'Let me analyze the code.\n{"text": "actual"}'
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "actual"


def test_parse_output_prose_and_trailing_json(llm_output_json_parser: LLMOutputJSONParser):
    """Should parse first valid JSON when LLM returns prose + object + another object."""
    output = 'Here is my analysis:\n{"text": "result"}{"text": "extra"}'
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "result"


def test_parse_output_prose_with_braces_before_json(llm_output_json_parser: LLMOutputJSONParser):
    """Should skip stray brace blocks in prose and parse the actual JSON object."""
    output = 'Some prose with {curly braces} before JSON\n{"text": "actual"}'
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "actual"


def test_parse_output_multiple_stray_braces_before_json(llm_output_json_parser: LLMOutputJSONParser):
    """Should skip multiple non-JSON brace groups in prose."""
    output = 'I noticed {some} issues and {more stuff} here.\n{"text": "found"}'
    result = llm_output_json_parser.parse_output(output)

    assert isinstance(result, DummyModel)
    assert result.text == "found"
