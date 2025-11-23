from pydantic import BaseModel

from ai_review.services.artifacts.schema.base import BaseArtifactSchema, ArtifactType
from ai_review.services.review.internal.inline.schema import InlineCommentSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema


class VCSInlineArtifactDataSchema(BaseModel):
    inline_comment: InlineCommentSchema


class VCSSummaryArtifactDataSchema(BaseModel):
    summary_comment: SummaryCommentSchema


class VCSInlineReplyArtifactDataSchema(BaseModel):
    thread_id: str | int
    inline_comment_reply: InlineCommentReplySchema


class VCSSummaryReplyArtifactDataSchema(BaseModel):
    thread_id: str | int
    summary_comment_reply: SummaryCommentReplySchema


class VCSInlineArtifactSchema(BaseArtifactSchema[VCSInlineArtifactDataSchema]):
    type: ArtifactType = ArtifactType.VCS_INLINE


class VCSSummaryArtifactSchema(BaseArtifactSchema[VCSSummaryArtifactDataSchema]):
    type: ArtifactType = ArtifactType.VCS_SUMMARY


class VCSInlineReplyArtifactSchema(BaseArtifactSchema[VCSInlineReplyArtifactDataSchema]):
    type: ArtifactType = ArtifactType.VCS_INLINE_REPLY


class VCSSummaryReplyArtifactSchema(BaseArtifactSchema[VCSSummaryReplyArtifactDataSchema]):
    type: ArtifactType = ArtifactType.VCS_SUMMARY_REPLY
