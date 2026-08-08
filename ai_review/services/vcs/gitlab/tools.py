from ai_review.clients.gitlab.mr.schema.draft_notes import GitLabDraftNoteSchema
from ai_review.config import settings


def filter_ai_review_drafts(
        drafts: list[GitLabDraftNoteSchema],
) -> list[GitLabDraftNoteSchema]:
    tags = (
        settings.review.inline_tag,
        settings.review.inline_reply_tag,
        settings.review.inline_fallback_tag,
        settings.review.summary_tag,
        settings.review.summary_reply_tag,
    )
    return [
        draft
        for draft in drafts
        if any(tag and tag in draft.note for tag in tags)
    ]
