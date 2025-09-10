from clients.gitlab.mr.client import get_gitlab_merge_requests_http_client
from clients.openai.client import get_openai_http_client
from config import settings
from libs.asynchronous.gather import bounded_gather
from libs.logger import get_logger
from services.diff.service import DiffService
from services.prompt.adapter.openai import build_openai_chat_request
from services.prompt.service import PromptService
from services.review.inline.adapter.gitlab import (
    build_gitlab_create_mr_discussion_requests,
)
from services.review.inline.schema import InlineCommentListSchema
from services.review.inline.service import InlineCommentService
from services.review.summary.service import SummaryCommentService

logger = get_logger("REVIEW_SERVICE")


class ReviewService:
    def __init__(self):
        self.openai_http_client = get_openai_http_client()
        self.gitlab_mr_http_client = get_gitlab_merge_requests_http_client()

        self.diff = DiffService()
        self.prompt = PromptService()
        self.inline = InlineCommentService()
        self.summary = SummaryCommentService()

    async def ask_openai(self, prompt_text: str) -> str:
        try:
            chat_completion_request = build_openai_chat_request(prompt_text)
            chat_completion_response = await self.openai_http_client.chat_completion(
                chat_completion_request
            )

            raw = (chat_completion_response.choices[0].message.content or "").strip()
            if not raw:
                logger.warning(
                    f"OpenAI returned an empty response (prompt length={len(prompt_text)} chars)"
                )

            return raw
        except Exception as error:
            logger.error("OpenAI request failed: %s", error, exc_info=True)
            raise

    async def run_inline_review(self) -> None:
        project_id = settings.gitlab_pipeline.project_id
        merge_request_id = settings.gitlab_pipeline.merge_request_iid

        get_mr_changes_response = await self.gitlab_mr_http_client.get_mr_changes(
            project_id=project_id,
            merge_request_id=merge_request_id
        )
        allowed_map = self.diff.build_allowed_map(get_mr_changes_response.changes)

        for change in get_mr_changes_response.changes:
            prompt_text = self.prompt.build_inline_request(
                diff=f"# File: {change.new_path}\n{change.diff}"
            )
            chat_completion_raw = await self.ask_openai(prompt_text)

            comments: InlineCommentListSchema = (
                self.inline.parse_model_output(chat_completion_raw)
                .dedupe()
                .filter(allowed_map)
            )
            if not comments.root:
                continue

            create_mr_discussion_requests = build_gitlab_create_mr_discussion_requests(
                comments=comments,
                base_sha=get_mr_changes_response.diff_refs.base_sha,
                head_sha=get_mr_changes_response.diff_refs.head_sha,
                start_sha=get_mr_changes_response.diff_refs.start_sha,
            )
            results = await bounded_gather([
                self.gitlab_mr_http_client.create_mr_discussion(
                    project_id=project_id,
                    merge_request_id=merge_request_id,
                    request=create_mr_discussion_request,
                )
                for create_mr_discussion_request in create_mr_discussion_requests
            ])
            for result in results:
                if isinstance(result, Exception):
                    logger.error("Failed to create GitLab discussion: %s", result)

    async def run_summary_review(self) -> None:
        project_id = settings.gitlab_pipeline.project_id
        merge_request_id = settings.gitlab_pipeline.merge_request_iid

        get_mr_changes_response = await self.gitlab_mr_http_client.get_mr_changes(
            project_id=project_id,
            merge_request_id=merge_request_id,
        )

        diffs: list[str] = [
            f"--- {change.new_path} ---\n{change.diff}"
            for change in get_mr_changes_response.changes
        ]
        prompt_text = self.prompt.build_summary_request(diffs)
        chat_completion_raw = await self.ask_openai(prompt_text)

        summary = self.summary.parse_model_output(chat_completion_raw)
        await self.gitlab_mr_http_client.create_mr_comment(
            comment=summary.text,
            project_id=project_id,
            merge_request_id=merge_request_id,
        )
