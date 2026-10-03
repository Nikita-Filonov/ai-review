from ai_review.clients.azure_devops.pr.schema.files import AzureDevOpsPRItemSchema


def test_azure_devops_item_allows_missing_path() -> None:
    assert AzureDevOpsPRItemSchema(path=None).path is None
