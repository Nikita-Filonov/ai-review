from ai_review.libs.json import extract_json_objects
from ai_review.libs.llm.output_json_parser import CLEAN_JSON_BLOCK_RE, LLMOutputJSONParser
from ai_review.services.agent.loop.schema import AgentStepSchema
from ai_review.services.agent.loop.tools import is_attempted_action


class AgentResponseParser:
    def __init__(self):
        self.json_parser = LLMOutputJSONParser[AgentStepSchema](AgentStepSchema)

    def parse(self, output: str) -> list[AgentStepSchema]:
        if not is_attempted_action(output):
            return []

        objects = extract_json_objects(output)
        remainder = output
        for raw in objects:
            remainder = remainder.replace(raw, "", 1)

        # Do not execute a partial batch when extraction skipped a malformed action.
        if objects and is_attempted_action(remainder):
            return []

        # The single-step parser can repair the first fenced object. It must not hide other actions.
        if not objects and (match := CLEAN_JSON_BLOCK_RE.search(output)):
            if is_attempted_action(output[:match.start()] + output[match.end():]):
                return []

        # Preserve the existing single-step parsing, including JSON sanitization.
        if len(objects) <= 1:
            step = self.json_parser.parse_output(output)
            return [step] if step is not None else []

        steps: list[AgentStepSchema] = []
        for raw in objects:
            step = self.json_parser.parse_output(raw)
            if step is None:
                return []
            steps.append(step)

        if sum(step.action.is_final for step in steps) > 1:
            return []
        return steps
