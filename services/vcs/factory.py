from config import settings
from libs.constants.vcs_provider import VCSProvider
from services.vcs.gitlab.client import GitLabVCSClient
from services.vcs.types import VCSClient


def get_vcs_client() -> VCSClient:
    match settings.vcs.provider:
        case VCSProvider.GITLAB:
            return GitLabVCSClient()
        case _:
            raise ValueError(f"Unsupported provider: {settings.llm.provider}")
