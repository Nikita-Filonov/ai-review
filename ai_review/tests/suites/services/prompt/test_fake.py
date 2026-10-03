from ai_review.services.prompt.schema import PromptContextSchema
from ai_review.tests.fixtures.services.prompt import FakePromptService


def test_fake_prompt_records_template_and_context() -> None:
    prompt = FakePromptService()
    context = PromptContextSchema(review_title="Example")
    assert prompt.prepare_prompt(["template"], context) == "FAKE_PROMPT"
    assert prompt.calls[-1] == ("prepare_prompt", {"prompts": ["template"], "context": context})
