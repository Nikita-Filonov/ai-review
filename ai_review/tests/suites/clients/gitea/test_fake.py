import pytest

from ai_review.tests.fixtures.clients.gitea import FakeGiteaPullRequestsHTTPClient


@pytest.mark.asyncio
async def test_gitea_fake_records_review_comment_deletion() -> None:
    fake = FakeGiteaPullRequestsHTTPClient()
    await fake.delete_review_comment("owner", "repo", 42)
    assert fake.calls[-1] == (
        "delete_review_comment",
        {"owner": "owner", "repo": "repo", "comment_id": 42},
    )
