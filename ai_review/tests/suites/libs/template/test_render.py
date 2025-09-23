from ai_review.libs.template.render import render_template


def test_replaces_single_variable():
    text = "Hello, <<name>>!"
    values = {"name": "Alice"}
    result = render_template(text, values)
    assert result == "Hello, Alice!"


def test_replaces_multiple_variables():
    text = "User: <<user>>, Branch: <<branch>>"
    values = {"user": "nikita", "branch": "main"}
    result = render_template(text, values)
    assert result == "User: nikita, Branch: main"


def test_missing_variable_keeps_placeholder():
    text = "Hello, <<name>>, you are <<role>>"
    values = {"name": "Bob"}
    result = render_template(text, values)
    assert result == "Hello, Bob, you are <<role>>"


def test_custom_placeholder_format():
    text = "Hello, [[name]]!"
    values = {"name": "Alice"}
    result = render_template(text, values, placeholder="[[{value}]]")
    assert result == "Hello, Alice!"


def test_placeholder_with_digits_and_underscores():
    text = "Key: <<var_123>>"
    values = {"var_123": "ok"}
    result = render_template(text, values)
    assert result == "Key: ok"


def test_no_placeholders_in_text():
    text = "Nothing to replace"
    values = {"name": "Alice"}
    result = render_template(text, values)
    assert result == "Nothing to replace"


def test_partial_overlap_does_not_replace():
    text = "This is <<var>> and <<var_extra>>"
    values = {"var": "A", "var_extra": "B"}
    result = render_template(text, values)
    assert result == "This is A and B"


def test_placeholder_with_dot_and_dash():
    text = "Branch: <<feature-1.2>>"
    values = {"feature-1.2": "ok"}
    result = render_template(text, values)
    assert result == "Branch: ok"


def test_multiple_same_placeholders():
    text = "<<name>>, <<name>>, <<name>>!"
    values = {"name": "Alice"}
    result = render_template(text, values)
    assert result == "Alice, Alice, Alice!"
