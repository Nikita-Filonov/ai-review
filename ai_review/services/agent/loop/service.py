from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.agent.loop.parser import AgentResponseParser
from ai_review.services.agent.loop.schema import (
    AgentLoopResultSchema,
    AgentStepSchema,
    AgentTraceSchema,
)
from ai_review.services.agent.loop.state import AgentRunState
from ai_review.services.agent.loop.tools import is_attempted_action
from ai_review.services.agent.loop.types import AgentLoopServiceProtocol
from ai_review.services.agent.tool.types import AgentToolServiceProtocol
from ai_review.services.llm.types import ChatResultSchema, LLMClientProtocol
from ai_review.services.prompt.types import PromptServiceProtocol

logger = get_logger("AGENT_LOOP_SERVICE")

PROTOCOL_RETRY_WARNING = (
    "Invalid response discarded: it did not follow the agent JSON protocol. "
    "Respond with one or more TOOL_CALL objects, one per command, separated by newlines: "
    '{"action": "TOOL_CALL", "command": "<single command>"} '
    'or a single {"action": "FINAL", "content": "<complete answer as a string>"} object. '
    "Do not mix FINAL with TOOL_CALL; wait for tool results before finalizing. "
    "Do not include markdown fences or prose outside the JSON objects. "
    'Every quote inside a JSON string value must be escaped as \\".'
)


class AgentLoopService(AgentLoopServiceProtocol):
    def __init__(
            self,
            llm: LLMClientProtocol,
            prompt: PromptServiceProtocol,
            agent_tool: AgentToolServiceProtocol,
    ):
        self.llm = llm
        self.prompt = prompt
        self.agent_tool = agent_tool
        self.max_iterations = settings.agent.max_iterations
        self.max_context_chars = settings.agent.max_total_context_chars
        self.max_protocol_violations = settings.agent.max_protocol_violations
        self.parser = AgentResponseParser()

    async def request(
            self,
            prompt: str,
            prompt_system: str,
            state: AgentRunState,
            force_final: bool,
    ) -> ChatResultSchema:
        agent_prompt = self.prompt.build_agent_request(
            traces=state.traces,
            force_final=force_final,
            original_prompt=prompt,
            original_prompt_system=prompt_system,
        )
        agent_prompt_system = self.prompt.build_system_agent_request()
        logger.debug(
            f"Agent request (force_final={force_final}, prompt_chars={len(agent_prompt)}, "
            f"system_chars={len(agent_prompt_system)}, traces={len(state.traces)})"
        )
        return await self.llm.chat(prompt=agent_prompt, prompt_system=agent_prompt_system)

    async def run_step(
            self,
            step: AgentStepSchema,
            chat: ChatResultSchema,
            state: AgentRunState,
            iteration: int,
    ) -> AgentTraceSchema:
        command = step.command
        if command is None:
            raise ValueError("A TOOL_CALL step must contain a command")

        if command in state.signatures:
            logger.debug(f"Duplicate tool call blocked at iteration {iteration}: {command}")
            return AgentTraceSchema(
                step=step,
                warning=f"Duplicate tool call blocked: {command}",
                iteration=iteration,
                raw_output=chat.text,
            )

        state.signatures.add(command)
        logger.debug(f"Executing agent tool command at iteration {iteration}: {command}")
        tool_output = await self.agent_tool.execute(command)
        return AgentTraceSchema(
            step=step,
            iteration=iteration,
            raw_output=chat.text,
            tool_output=tool_output,
        )

    async def force_final(
            self,
            prompt: str,
            prompt_system: str,
            state: AgentRunState,
    ) -> AgentLoopResultSchema:
        logger.info("Forcing FINAL response after loop limits reached")
        chat = await self.request(prompt=prompt, prompt_system=prompt_system, state=state, force_final=True)
        steps = self.parser.parse(chat.text)
        step = steps[0] if len(steps) == 1 else None
        if step is None and is_attempted_action(chat.text):
            logger.warning(
                "Forced FINAL response does not contain a single valid action; "
                "returning the raw model output as a last resort"
            )
        return state.finish(
            chat=chat,
            iteration=state.traces[-1].iteration + 1 if state.traces else 1,
            step=step,
            stop_reason="max_requests_or_context_limit",
            warning="Forced final response after max_requests/context_limit.",
        )

    async def run(self, prompt: str, prompt_system: str) -> AgentLoopResultSchema:
        state = AgentRunState()
        logger.info(
            f"Starting agent loop: max_iterations={self.max_iterations}, max_context_chars={self.max_context_chars}"
        )
        for iteration in range(1, self.max_iterations + 1):
            chat = await self.request(prompt=prompt, prompt_system=prompt_system, state=state, force_final=False)
            logger.debug(f"Agent LLM response at iteration {iteration}: {chat.text[:500]}")
            steps = self.parser.parse(chat.text)

            if not steps:
                if not is_attempted_action(chat.text):
                    logger.info(f"Agent loop iteration {iteration} returned content without an agent envelope")
                    return state.finish(
                        chat=chat,
                        iteration=iteration,
                        step=None,
                        stop_reason="unstructured_response",
                        warning="Model returned content without an agent envelope.",
                    )

                state.protocol_violations += 1
                logger.warning(
                    f"Agent loop iteration {iteration} returned an unparseable action "
                    f"({state.protocol_violations}/{self.max_protocol_violations} tolerated); discarding it"
                )
                state.record_trace(
                    AgentTraceSchema(warning=PROTOCOL_RETRY_WARNING, iteration=iteration, raw_output=chat.text),
                    chat=chat,
                )
                if state.protocol_violations > self.max_protocol_violations:
                    logger.info("Too many unparseable actions; switching to force-final flow")
                    break
                continue

            tool_steps = [step for step in steps if not step.action.is_final]
            if not tool_steps:
                logger.info(f"Agent loop iteration {iteration} returned FINAL action")
                return state.finish(chat=chat, iteration=iteration, step=steps[0], stop_reason="final")

            # A FINAL alongside tools cannot use their results yet. Ask again after executing them.
            for step in tool_steps:
                trace = await self.run_step(step=step, chat=chat, state=state, iteration=iteration)
                state.record_trace(trace, chat=chat)
                if state.context_used >= self.max_context_chars:
                    break

            logger.debug(f"Agent context usage after iteration {iteration}: {state.context_used}/{self.max_context_chars}")
            if state.context_used >= self.max_context_chars:
                logger.info("Agent context limit reached, forcing final response")
                break

        return await self.force_final(prompt=prompt, prompt_system=prompt_system, state=state)
