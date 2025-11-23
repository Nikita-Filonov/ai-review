from pathlib import Path

import aiofiles

from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.artifacts.schema.base import BaseArtifactSchema
from ai_review.services.artifacts.schema.llm import LLMArtifactSchema, LLMArtifactDataSchema
from ai_review.services.artifacts.schema.vcs import (
    VCSInlineArtifactSchema,
    VCSInlineArtifactDataSchema,
    VCSSummaryArtifactSchema,
    VCSSummaryArtifactDataSchema,
    VCSInlineReplyArtifactSchema,
    VCSInlineReplyArtifactDataSchema,
    VCSSummaryReplyArtifactSchema,
    VCSSummaryReplyArtifactDataSchema,
)
from ai_review.services.artifacts.types import ArtifactsServiceProtocol
from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.review.internal.inline.schema import InlineCommentSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema

logger = get_logger("ARTIFACTS_SERVICE")


class ArtifactsService(ArtifactsServiceProtocol):
    @classmethod
    async def save(
            cls,
            artifact: BaseArtifactSchema,
            artifacts_dir: Path,
            artifacts_enabled: bool,
    ) -> str | None:
        if not artifacts_enabled:
            logger.debug(f"Skipping {artifact.type} artifact: saving disabled")
            return None

        artifact_file = artifacts_dir / f"{artifact.id}.json"

        try:
            async with aiofiles.open(artifact_file, "w", encoding="utf-8") as aiofile:
                await aiofile.write(artifact.model_dump_json(indent=2))

            logger.debug(f"Saved {artifact.type} → {artifact_file}")
            return str(artifact.id)

        except Exception as error:
            logger.exception(f"Failed to save {artifact.type} → {artifact_file}: {error}")
            return None

    @classmethod
    async def save_llm(
            cls,
            prompt: str,
            response: str,
            prompt_system: str,
            cost_report: CostReportSchema | None = None
    ) -> str | None:
        artifact = LLMArtifactSchema(
            data=LLMArtifactDataSchema(
                prompt=prompt,
                response=response,
                prompt_system=prompt_system,
                cost_report=cost_report,
            )
        )

        return await cls.save(
            artifact=artifact,
            artifacts_dir=settings.artifacts.llm_dir,
            artifacts_enabled=settings.artifacts.llm_enabled,
        )

    @classmethod
    async def save_vcs_inline(cls, comment: InlineCommentSchema) -> str | None:
        artifact = VCSInlineArtifactSchema(
            data=VCSInlineArtifactDataSchema(inline_comment=comment)
        )

        return await cls.save(
            artifact=artifact,
            artifacts_dir=settings.artifacts.vcs_dir,
            artifacts_enabled=settings.artifacts.vcs_enabled,
        )

    @classmethod
    async def save_vcs_summary(cls, comment: SummaryCommentSchema) -> str | None:
        artifact = VCSSummaryArtifactSchema(
            data=VCSSummaryArtifactDataSchema(summary_comment=comment)
        )

        return await cls.save(
            artifact=artifact,
            artifacts_dir=settings.artifacts.vcs_dir,
            artifacts_enabled=settings.artifacts.vcs_enabled,
        )

    @classmethod
    async def save_vcs_inline_reply(cls, thread_id: str, reply: InlineCommentReplySchema) -> str | None:
        artifact = VCSInlineReplyArtifactSchema(
            data=VCSInlineReplyArtifactDataSchema(
                thread_id=thread_id,
                inline_comment_reply=reply,
            )
        )

        return await cls.save(
            artifact=artifact,
            artifacts_dir=settings.artifacts.vcs_dir,
            artifacts_enabled=settings.artifacts.vcs_enabled,
        )

    @classmethod
    async def save_vcs_summary_reply(cls, thread_id: str, reply: SummaryCommentReplySchema) -> str | None:
        artifact = VCSSummaryReplyArtifactSchema(
            data=VCSSummaryReplyArtifactDataSchema(
                thread_id=thread_id,
                summary_comment_reply=reply,
            )
        )

        return await cls.save(
            artifact=artifact,
            artifacts_dir=settings.artifacts.vcs_dir,
            artifacts_enabled=settings.artifacts.vcs_enabled,
        )
