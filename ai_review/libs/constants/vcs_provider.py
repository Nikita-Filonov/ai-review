from enum import StrEnum


class VCSProvider(StrEnum):
    GITEA = "GITEA"
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    BITBUCKET_CLOUD = "BITBUCKET_CLOUD"
    BITBUCKET_SERVER = "BITBUCKET_SERVER"
