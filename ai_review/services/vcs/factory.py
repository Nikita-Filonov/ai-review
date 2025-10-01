from ai_review.config import settings
from ai_review.libs.constants.vcs_provider import VCSProvider
from ai_review.services.vcs.github.client import GitHubVCSClient
from ai_review.services.vcs.gitlab.client import GitLabVCSClient
from ai_review.services.vcs.types import VCSClientProtocol


def get_vcs_client() -> VCSClientProtocol:
    match settings.vcs.provider:
        case VCSProvider.GITLAB:
            return GitLabVCSClient()
        case VCSProvider.GITHUB:
            return GitHubVCSClient()
        case _:
            raise ValueError(f"Unsupported VCS provider: {settings.vcs.provider}")
