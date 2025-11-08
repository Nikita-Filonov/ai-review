import pytest
from httpx import AsyncClient

from ai_review.clients.azure_devops.client import get_azure_devops_http_client, AzureDevOpsHTTPClient
from ai_review.clients.azure_devops.pr.client import AzureDevOpsPullRequestsHTTPClient


@pytest.mark.usefixtures("azure_devops_http_client_config")
def test_get_azure_devops_http_client_builds_ok():
    azure_devops_http_client = get_azure_devops_http_client()

    assert isinstance(azure_devops_http_client, AzureDevOpsHTTPClient)
    assert isinstance(azure_devops_http_client.pr, AzureDevOpsPullRequestsHTTPClient)
    assert isinstance(azure_devops_http_client.pr.client, AsyncClient)
