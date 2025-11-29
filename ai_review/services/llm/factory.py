from ai_review.config import settings
from ai_review.libs.constants.llm_provider import LLMProvider
from ai_review.services.llm.azure_openai.client import AzureOpenAILLMClient
from ai_review.services.llm.bedrock.client import BedrockLLMClient
from ai_review.services.llm.claude.client import ClaudeLLMClient
from ai_review.services.llm.gemini.client import GeminiLLMClient
from ai_review.services.llm.ollama.client import OllamaLLMClient
from ai_review.services.llm.openai.client import OpenAILLMClient
from ai_review.services.llm.openrouter.client import OpenRouterLLMClient
from ai_review.services.llm.types import LLMClientProtocol


def get_llm_client() -> LLMClientProtocol:
    match settings.llm.provider:
        case LLMProvider.OPENAI:
            return OpenAILLMClient()
        case LLMProvider.GEMINI:
            return GeminiLLMClient()
        case LLMProvider.CLAUDE:
            return ClaudeLLMClient()
        case LLMProvider.OLLAMA:
            return OllamaLLMClient()
        case LLMProvider.BEDROCK:
            return BedrockLLMClient()
        case LLMProvider.OPENROUTER:
            return OpenRouterLLMClient()
        case LLMProvider.AZURE_OPENAI:
            return AzureOpenAILLMClient()
        case _:
            raise ValueError(f"Unsupported LLM provider: {settings.llm.provider}")
