from enum import StrEnum


class LLMProvider(StrEnum):
    OPENAI = "OPENAI"
    GEMINI = "GEMINI"
    CLAUDE = "CLAUDE"
    OLLAMA = "OLLAMA"
    BEDROCK = "BEDROCK"
    OPENROUTER = "OPENROUTER"
    REQUESTY = "REQUESTY"
    AZURE_OPENAI = "AZURE_OPENAI"
