from pathlib import Path

import aiofiles

from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.artifacts.schema import LLMArtifactSchema
from ai_review.services.artifacts.tools import make_artifact_id
from ai_review.services.artifacts.types import ArtifactsServiceProtocol

logger = get_logger("ARTIFACTS_SERVICE")


class ArtifactsService(ArtifactsServiceProtocol):
    @classmethod
    async def save_llm_interaction(cls, prompt: str, prompt_system: str, response: str | None = None) -> str | None:
        if not settings.artifacts.llm_enabled:
            logger.debug("Artifacts for LLM saving is disabled, skipping")
            return None

        artifact_id = make_artifact_id(prompt)
        logger.info(f"Creating LLM interaction with id={artifact_id}")

        file = settings.artifacts.llm_dir / f"{artifact_id}.json"
        record = LLMArtifactSchema(
            id=artifact_id,
            prompt=prompt,
            response=response,
            prompt_system=prompt_system
        )

        try:
            await cls.save_artifact(file, record.model_dump_json(indent=2), kind="llm_interaction")
        except Exception as error:
            logger.exception(f"Failed to save LLM interaction {artifact_id}: {error}")

        return artifact_id

    @classmethod
    async def save_artifact(cls, file: Path, content: str, kind: str = "artifact") -> Path | None:
        try:
            async with aiofiles.open(file, "w", encoding="utf-8") as aiofile:
                await aiofile.write(content)
            logger.debug(f"Saved {kind} → {file}")
            return file
        except Exception as error:
            logger.exception(f"Failed to save {kind} {file.stem}: {error}")
            return None
