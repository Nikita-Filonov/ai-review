from enum import StrEnum


class LLMProvider(StrEnum):
    OPENAI = "OPENAI"
    GEMINI = "GEMINI"
    CLAUDE = "CLAUDE"
    OLLAMA = "OLLAMA"
    BEDROCK = "BEDROCK"
    OPENROUTER = "OPENROUTER"
    AZURE_OPENAI = "AZURE_OPENAI"
