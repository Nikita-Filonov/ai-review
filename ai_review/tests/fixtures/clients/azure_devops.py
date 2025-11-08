import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.azure_devops.pr.schema.files import (
    AzureDevOpsPRItemSchema,
    AzureDevOpsPRChangeSchema,
    AzureDevOpsGetPRFilesResponseSchema,
)
from ai_review.clients.azure_devops.pr.schema.pull_request import (
    AzureDevOpsCommitSchema,
    AzureDevOpsRepositorySchema,
    AzureDevOpsGetPRResponseSchema,
)
from ai_review.clients.azure_devops.pr.schema.threads import (
    AzureDevOpsPRThreadSchema,
    AzureDevOpsPRCommentSchema,
    AzureDevOpsThreadContextSchema,
    AzureDevOpsGetPRThreadsResponseSchema,
    AzureDevOpsCreatePRCommentRequestSchema,
    AzureDevOpsCreatePRCommentResponseSchema,
    AzureDevOpsCreatePRThreadRequestSchema,
    AzureDevOpsCreatePRThreadResponseSchema,
)
from ai_review.clients.azure_devops.pr.schema.user import AzureDevOpsUserSchema
from ai_review.clients.azure_devops.pr.types import AzureDevOpsPullRequestsHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.vcs.azure_devops import AzureDevOpsPipelineConfig, AzureDevOpsHTTPClientConfig
from ai_review.libs.config.vcs.base import AzureDevOpsVCSConfig
from ai_review.libs.constants.vcs_provider import VCSProvider
from ai_review.services.vcs.azure_devops.client import AzureDevOpsVCSClient


# --- Fake HTTP Client for Azure DevOps ---
class FakeAzureDevOpsPullRequestsHTTPClient(AzureDevOpsPullRequestsHTTPClientProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    # --- Pull Request info ---
    async def get_pull_request(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int
    ) -> AzureDevOpsGetPRResponseSchema:
        self.calls.append(
            (
                "get_pull_request",
                {
                    "organization": organization,
                    "project": project,
                    "repository_id": repository_id,
                    "pull_request_id": pull_request_id
                }
            )
        )
        return AzureDevOpsGetPRResponseSchema(
            title="Test PR",
            description="Fake Azure DevOps PR",
            status="active",
            reviewers=[
                AzureDevOpsUserSchema(id="101", display_name="Reviewer", unique_name="reviewer@example.com"),
            ],
            created_by=AzureDevOpsUserSchema(id="100", display_name="Author", unique_name="author@example.com"),
            repository=AzureDevOpsRepositorySchema(id="repo123", name="fake-repo"),
            creation_date=None,
            pull_request_id=pull_request_id,
            source_ref_name="refs/heads/feature/test",
            target_ref_name="refs/heads/main",
            last_merge_commit=AzureDevOpsCommitSchema(commit_id="abc123"),
            last_merge_source_commit=AzureDevOpsCommitSchema(commit_id="abc123"),
            last_merge_target_commit=AzureDevOpsCommitSchema(commit_id="def456"),
        )

    # --- Changed files ---
    async def get_files(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            iteration_id: int
    ) -> AzureDevOpsGetPRFilesResponseSchema:
        self.calls.append(
            (
                "get_files",
                {
                    "organization": organization,
                    "project": project,
                    "repository_id": repository_id,
                    "pull_request_id": pull_request_id,
                    "iteration_id": iteration_id
                }
            )
        )
        return AzureDevOpsGetPRFilesResponseSchema(
            count=2,
            change_entries=[
                AzureDevOpsPRChangeSchema(
                    item=AzureDevOpsPRItemSchema(
                        path="src/app.py",
                        object_id="1",
                    ),
                    change_type="edit"
                ),
                AzureDevOpsPRChangeSchema(
                    item=AzureDevOpsPRItemSchema(
                        path="src/utils/helper.py",
                        object_id="2",
                    ),
                    change_type="add"
                ),
            ]
        )

    # --- Threads & Comments ---
    async def get_threads(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int
    ) -> AzureDevOpsGetPRThreadsResponseSchema:
        self.calls.append(
            (
                "get_threads",
                {
                    "organization": organization,
                    "project": project,
                    "repository_id": repository_id,
                    "pull_request_id": pull_request_id
                }
            )
        )

        user = AzureDevOpsUserSchema(id="200", display_name="Commenter", unique_name="user@example.com")
        thread_with_context = AzureDevOpsPRThreadSchema(
            id=1,
            status="active",
            comments=[
                AzureDevOpsPRCommentSchema(id=11, content="Inline comment", author=user),
            ],
            is_deleted=False,
            thread_context=AzureDevOpsThreadContextSchema(file_path="src/app.py")
        )
        general_thread = AzureDevOpsPRThreadSchema(
            id=2,
            status="active",
            comments=[
                AzureDevOpsPRCommentSchema(id=12, content="General comment", author=user),
            ],
            is_deleted=False,
            thread_context=None
        )

        return AzureDevOpsGetPRThreadsResponseSchema(value=[thread_with_context, general_thread], count=2)

    async def create_thread(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            request: AzureDevOpsCreatePRThreadRequestSchema
    ) -> AzureDevOpsCreatePRThreadResponseSchema:
        self.calls.append(
            (
                "create_thread",
                {
                    "organization": organization,
                    "project": project,
                    "repository_id": repository_id,
                    "pull_request_id": pull_request_id,
                    "request": request
                }
            )
        )
        return AzureDevOpsCreatePRThreadResponseSchema(
            id=10,
            status=request.status,
            comments=[
                AzureDevOpsPRCommentSchema(id=999, content=request.comments[0].content)
            ]
        )

    async def create_comment(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            thread_id: int,
            request: AzureDevOpsCreatePRCommentRequestSchema
    ) -> AzureDevOpsCreatePRCommentResponseSchema:
        self.calls.append(
            (
                "create_comment",
                {
                    "organization": organization,
                    "project": project,
                    "repository_id": repository_id,
                    "pull_request_id": pull_request_id,
                    "thread_id": thread_id,
                    "request": request
                }
            )
        )
        return AzureDevOpsCreatePRCommentResponseSchema(id=123, content=request.content)


class FakeAzureDevOpsHTTPClient:
    def __init__(self, pull_requests_client: AzureDevOpsPullRequestsHTTPClientProtocol):
        self.pr = pull_requests_client


# --- Pytest fixtures ---

@pytest.fixture
def fake_azure_devops_pull_requests_http_client() -> FakeAzureDevOpsPullRequestsHTTPClient:
    return FakeAzureDevOpsPullRequestsHTTPClient()


@pytest.fixture
def fake_azure_devops_http_client(
        fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient
) -> FakeAzureDevOpsHTTPClient:
    return FakeAzureDevOpsHTTPClient(pull_requests_client=fake_azure_devops_pull_requests_http_client)


@pytest.fixture
def azure_devops_vcs_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_azure_devops_http_client: FakeAzureDevOpsHTTPClient
) -> AzureDevOpsVCSClient:
    monkeypatch.setattr(
        "ai_review.services.vcs.azure_devops.client.get_azure_devops_http_client",
        lambda: fake_azure_devops_http_client,
    )
    return AzureDevOpsVCSClient()


@pytest.fixture
def azure_devops_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = AzureDevOpsVCSConfig(
        provider=VCSProvider.AZURE_DEVOPS,
        pipeline=AzureDevOpsPipelineConfig(
            organization="org",
            project="proj",
            repository_id="repo123",
            pull_request_id=5,
            iteration_id=7,
        ),
        http_client=AzureDevOpsHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://dev.azure.com/org"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "vcs", fake_config)
