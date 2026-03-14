from ai_review.config import settings
from ai_review.libs.llm.output_json_parser import LLMOutputJSONParser
from ai_review.libs.logger import get_logger
from ai_review.services.agent.loop.schema import (
    AgentAction,
    AgentStepSchema,
    AgentTraceSchema,
    AgentLoopResultSchema
)
from ai_review.services.agent.loop.types import AgentLoopServiceProtocol
from ai_review.services.agent.tool.types import AgentToolServiceProtocol
from ai_review.services.llm.types import LLMClientProtocol, ChatResultSchema
from ai_review.services.prompt.types import PromptServiceProtocol

logger = get_logger("AGENT_LOOP_SERVICE")


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

        self.parser = LLMOutputJSONParser(AgentStepSchema)
        self.traces: list[AgentTraceSchema] = []
        self.signatures: set[str] = set()
        self.context_used = 0

    def clear(self):
        self.traces = []
        self.signatures = set()
        self.context_used = 0
        logger.debug("Agent loop state cleared")

    async def run_step(self, step: AgentStepSchema, chat: ChatResultSchema, iteration: int) -> AgentTraceSchema:
        if step.command in self.signatures:
            logger.debug(f"Duplicate tool call blocked at iteration {iteration}: {step.command}")
            return AgentTraceSchema(
                step=step,
                warning=f"Duplicate tool call blocked: {step.command}",
                iteration=iteration,
                raw_output=chat.text,
                total_tokens=chat.total_tokens,
                prompt_tokens=chat.prompt_tokens,
                completion_tokens=chat.completion_tokens,
            )

        self.signatures.add(step.command)
        logger.debug(f"Executing agent tool command at iteration {iteration}: {step.command}")
        tool_output = await self.agent_tool.execute(step.command)

        return AgentTraceSchema(
            step=step,
            iteration=iteration,
            raw_output=chat.text,
            tool_output=tool_output,
            total_tokens=chat.total_tokens,
            prompt_tokens=chat.prompt_tokens,
            completion_tokens=chat.completion_tokens,
        )

    async def force_final(
            self,
            prompt: str,
            prompt_system: str,
    ) -> AgentLoopResultSchema:
        logger.info("Forcing FINAL response after loop limits reached")

        agent_prompt = self.prompt.build_agent_request(
            traces=self.traces,
            force_final=True,
            original_prompt=prompt,
            original_prompt_system=prompt_system,
        )
        agent_prompt_system = self.prompt.build_system_agent_request()
        logger.debug(
            f"Force-final prompt "
            f"(prompt_chars={len(agent_prompt)}, system_chars={len(agent_prompt_system)}, "
            f"traces={len(self.traces)})"
        )

        fallback_result = await self.llm.chat(
            prompt=agent_prompt,
            prompt_system=agent_prompt_system,
        )
        fallback_text = fallback_result.text
        fallback_step: AgentStepSchema | None = self.parser.parse_output(fallback_text)
        logger.debug(
            f"Forced FINAL raw response received; "
            f"parsed_as_final={bool(fallback_step and fallback_step.action.is_final)}"
        )

        final_text = (
            fallback_step.content
            if fallback_step and fallback_step.action.is_final
            else fallback_text
        )

        self.traces.append(
            AgentTraceSchema(
                step=fallback_step or AgentStepSchema(action=AgentAction.FINAL, content=fallback_text),
                warning="Forced final response after max_requests/context_limit.",
                iteration=len(self.traces) + 1,
                raw_output=fallback_text,
                total_tokens=fallback_result.total_tokens,
                prompt_tokens=fallback_result.prompt_tokens,
                completion_tokens=fallback_result.completion_tokens,
            )
        )

        return AgentLoopResultSchema(
            traces=self.traces,
            final_text=final_text,
            stop_reason="max_requests_or_context_limit",
        )

    async def run(self, prompt: str, prompt_system: str) -> AgentLoopResultSchema:
        self.clear()
        logger.info(
            f"Starting agent loop: max_iterations={self.max_iterations}, max_context_chars={self.max_context_chars}"
        )

        for iteration in range(1, self.max_iterations + 1):
            logger.debug(f"Agent loop iteration started: {iteration}")

            agent_prompt = self.prompt.build_agent_request(
                traces=self.traces,
                force_final=False,
                original_prompt=prompt,
                original_prompt_system=prompt_system,
            )
            agent_prompt_system = self.prompt.build_system_agent_request()
            logger.debug(
                f"Agent prompt for iteration {iteration} "
                f"(prompt_chars={len(agent_prompt)}, system_chars={len(agent_prompt_system)}, "
                f"traces={len(self.traces)})"
            )
            
            result = await self.llm.chat(
                prompt=agent_prompt,
                prompt_system=agent_prompt_system,
            )
            logger.debug(f"Agent LLM response at iteration {iteration}: {result.text[:500]}")

            step: AgentStepSchema | None = self.parser.parse_output(result.text)
            if step is None:
                fallback_text = result.text or ""
                logger.info(f"Agent loop iteration {iteration} returned unstructured response; stopping")
                self.traces.append(
                    AgentTraceSchema(
                        step=AgentStepSchema(
                            action=AgentAction.FINAL,
                            content=fallback_text or "Empty model response",
                        ),
                        warning="Failed to parse structured action. Returning raw model output.",
                        iteration=iteration,
                        raw_output=fallback_text,
                        total_tokens=result.total_tokens,
                        prompt_tokens=result.prompt_tokens,
                        completion_tokens=result.completion_tokens,
                    )
                )

                return AgentLoopResultSchema(
                    traces=self.traces,
                    final_text=fallback_text,
                    stop_reason="unstructured_response",
                )

            if step.action.is_final:
                logger.info(f"Agent loop iteration {iteration} returned FINAL action")
                self.traces.append(
                    AgentTraceSchema(
                        step=step,
                        iteration=iteration,
                        raw_output=result.text,
                        total_tokens=result.total_tokens,
                        prompt_tokens=result.prompt_tokens,
                        completion_tokens=result.completion_tokens,
                    )
                )

                return AgentLoopResultSchema(
                    traces=self.traces,
                    final_text=step.content,
                    stop_reason="final",
                )

            trace = await self.run_step(step=step, chat=result, iteration=iteration)
            self.traces.append(trace)

            self.context_used += len(trace.tool_output or "")
            logger.debug(
                f"Agent loop context usage after iteration {iteration}: "
                f"{self.context_used}/{self.max_context_chars}"
            )
            if self.context_used >= self.max_context_chars:
                logger.info("Agent context limit reached, forcing final response")
                break

        logger.info("Agent loop finished regular iterations without FINAL action; switching to force-final flow")
        return await self.force_final(prompt=prompt, prompt_system=prompt_system)
