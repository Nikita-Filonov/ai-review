from datetime import datetime, timezone
from enum import StrEnum
from typing import Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field, UUID4

ArtifactData = TypeVar('ArtifactData', bound=BaseModel)


class ArtifactType(StrEnum):
    LLM = "LLM_INTERACTION"
    VCS_INLINE = "VCS_INLINE"
    VCS_SUMMARY = "VCS_SUMMARY"
    VCS_INLINE_REPLY = "VCS_INLINE_REPLY"
    VCS_SUMMARY_REPLY = "VCS_SUMMARY_REPLY"


class BaseArtifactSchema(BaseModel, Generic[ArtifactData]):
    id: UUID4 = Field(default_factory=uuid4)
    type: ArtifactType
    data: ArtifactData
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
