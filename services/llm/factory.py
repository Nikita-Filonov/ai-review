from config import settings
from libs.constants.llm_provider import LLMProvider
from services.llm.claude.client import ClaudeLLMClient
from services.llm.gemini.client import GeminiLLMClient
from services.llm.openai.client import OpenAILLMClient
from services.llm.types import LLMClient


def get_llm_client() -> LLMClient:
    match settings.llm.provider:
        case LLMProvider.OPENAI:
            return OpenAILLMClient()
        case LLMProvider.GEMINI:
            return GeminiLLMClient()
        case LLMProvider.CLAUDE:
            return ClaudeLLMClient()
        case _:
            raise ValueError(f"Unsupported provider: {settings.llm.provider}")
