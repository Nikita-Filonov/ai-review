import pytest

from ai_review.services.agent.loop.tools import is_attempted_action


@pytest.mark.parametrize(
    "output, expected",
    [
        ('{"action":"TOOL_CALL","command":"git grep -n -i -l "migration" -- docs"}', True),
        ('</think>{"action":"TOOL_CALL","command":"cat modules/Sample.java"}', True),
        (
            'Let me examine the key files first.{"action":"TOOL_CALL","command":"cat modules/Sample.java"}',
            True,
        ),
        ('{"action": "final", "content": "oops', True),
        ("## Summary\n\n- The change looks correct.", False),
        ('[{"file":"a.py","line":10,"message":"Unused import","suggestion":null}]', False),
        ("", False),
        ("The action taken by the FINAL migration is unclear", False),
    ],
)
def test_is_attempted_action_detects_the_protocol_envelope(output: str, expected: bool) -> None:
    assert is_attempted_action(output) is expected
