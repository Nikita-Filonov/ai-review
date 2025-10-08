import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.gitlab.mr.schema.changes import (
    GitLabUserSchema,
    GitLabMRChangeSchema,
    GitLabDiffRefsSchema,
    GitLabGetMRChangesResponseSchema,
)
from ai_review.clients.gitlab.mr.schema.discussions import (
    GitLabDiscussionSchema,
    GitLabGetMRDiscussionsResponseSchema,
    GitLabCreateMRDiscussionRequestSchema,
    GitLabCreateMRDiscussionResponseSchema,
    GitLabCreateMRDiscussionReplyResponseSchema,
)
from ai_review.clients.gitlab.mr.schema.notes import (
    GitLabNoteSchema,
    GitLabGetMRNotesResponseSchema,
    GitLabCreateMRNoteResponseSchema,
)
from ai_review.clients.gitlab.mr.schema.position import GitLabPositionSchema
from ai_review.clients.gitlab.mr.types import GitLabMergeRequestsHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.vcs.base import GitLabVCSConfig
from ai_review.libs.config.vcs.gitlab import GitLabPipelineConfig, GitLabHTTPClientConfig
from ai_review.libs.constants.vcs_provider import VCSProvider
from ai_review.services.vcs.gitlab.client import GitLabVCSClient


class FakeGitLabMergeRequestsHTTPClient(GitLabMergeRequestsHTTPClientProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def get_changes(self, project_id: str, merge_request_id: str) -> GitLabGetMRChangesResponseSchema:
        self.calls.append(("get_changes", {"project_id": project_id, "merge_request_id": merge_request_id}))
        return GitLabGetMRChangesResponseSchema(
            id=1,
            iid=1,
            title="Fake Merge Request",
            author=GitLabUserSchema(id=42, name="Tester", username="tester"),
            labels=["bugfix", "backend"],
            description="This is a fake MR for testing",
            project_id=1,
            diff_refs=GitLabDiffRefsSchema(
                base_sha="abc123",
                head_sha="def456",
                start_sha="ghi789",
            ),
            source_branch="feature/test",
            target_branch="main",
            changes=[
                GitLabMRChangeSchema(
                    diff="@@ -1,2 +1,2 @@\n- old\n+ new",
                    old_path="main.py",
                    new_path="main.py",
                )
            ],
        )

    async def get_notes(self, project_id: str, merge_request_id: str) -> GitLabGetMRNotesResponseSchema:
        self.calls.append(("get_notes", {"project_id": project_id, "merge_request_id": merge_request_id}))
        return GitLabGetMRNotesResponseSchema(
            root=[
                GitLabNoteSchema(
                    id=1,
                    body="General comment",
                    author=GitLabUserSchema(id=301, name="Charlie", username="charlie"),
                ),
                GitLabNoteSchema(
                    id=2,
                    body="Another note",
                    author=GitLabUserSchema(id=302, name="Diana", username="diana"),
                ),
            ]
        )

    async def get_discussions(self, project_id: str, merge_request_id: str) -> GitLabGetMRDiscussionsResponseSchema:
        self.calls.append(("get_discussions", {"project_id": project_id, "merge_request_id": merge_request_id}))
        return GitLabGetMRDiscussionsResponseSchema(
            root=[
                GitLabDiscussionSchema(
                    id="discussion-1",
                    notes=[
                        GitLabNoteSchema(
                            id=10,
                            body="Inline comment A",
                            position=GitLabPositionSchema(
                                base_sha="abc123",
                                head_sha="def456",
                                start_sha="ghi789",
                                new_path="src/app.py",
                                new_line=12,
                            ),
                        ),
                        GitLabNoteSchema(
                            id=11,
                            body="Inline comment B",
                            position=GitLabPositionSchema(
                                base_sha="abc123",
                                head_sha="def456",
                                start_sha="ghi789",
                                new_path="src/app.py",
                                new_line=14,
                            ),
                        ),
                    ],
                    position=GitLabPositionSchema(
                        base_sha="abc123",
                        head_sha="def456",
                        start_sha="ghi789",
                        new_path="src/app.py",
                        new_line=12,
                    ),
                ),
                GitLabDiscussionSchema(
                    id="discussion-2",
                    notes=[GitLabNoteSchema(id=20, body="Outdated diff comment", position=None)],
                    position=None,
                ),
            ]
        )

    async def create_note(self, body: str, project_id: str, merge_request_id: str) -> GitLabCreateMRNoteResponseSchema:
        self.calls.append(
            (
                "create_note",
                {"body": body, "project_id": project_id, "merge_request_id": merge_request_id}
            )
        )
        return GitLabCreateMRNoteResponseSchema(id=99, body=body)

    async def create_discussion(
            self,
            project_id: str,
            merge_request_id: str,
            request: GitLabCreateMRDiscussionRequestSchema,
    ) -> GitLabCreateMRDiscussionResponseSchema:
        self.calls.append(
            (
                "create_discussion",
                {"project_id": project_id, "merge_request_id": merge_request_id, "body": request.body}
            )
        )
        return GitLabCreateMRDiscussionResponseSchema(
            id="discussion-new",
            notes=[GitLabNoteSchema(id=1, body=request.body)]
        )

    async def create_discussion_reply(
            self,
            project_id: str,
            merge_request_id: str,
            discussion_id: str,
            body: str,
    ) -> GitLabCreateMRDiscussionReplyResponseSchema:
        self.calls.append(
            (
                "create_discussion_reply",
                {
                    "project_id": project_id,
                    "merge_request_id": merge_request_id,
                    "discussion_id": discussion_id,
                    "body": body,
                },
            )
        )
        return GitLabCreateMRDiscussionReplyResponseSchema(id=100, body=body)


class FakeGitLabHTTPClient:
    def __init__(self, merge_requests_client: FakeGitLabMergeRequestsHTTPClient):
        self.mr = merge_requests_client


@pytest.fixture
def fake_gitlab_merge_requests_http_client() -> FakeGitLabMergeRequestsHTTPClient:
    return FakeGitLabMergeRequestsHTTPClient()


@pytest.fixture
def fake_gitlab_http_client(
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient
) -> FakeGitLabHTTPClient:
    return FakeGitLabHTTPClient(merge_requests_client=fake_gitlab_merge_requests_http_client)


@pytest.fixture
def gitlab_vcs_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_gitlab_http_client: FakeGitLabHTTPClient
) -> GitLabVCSClient:
    monkeypatch.setattr(
        "ai_review.services.vcs.gitlab.client.get_gitlab_http_client",
        lambda: fake_gitlab_http_client,
    )

    return GitLabVCSClient()


@pytest.fixture
def gitlab_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = GitLabVCSConfig(
        provider=VCSProvider.GITLAB,
        pipeline=GitLabPipelineConfig(
            project_id="project-id",
            merge_request_id="merge-request-id"
        ),
        http_client=GitLabHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://gitlab.com"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "vcs", fake_config)
