from enum import StrEnum


class VCSProvider(StrEnum):
    GITEA = "GITEA"
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    BITBUCKET = "BITBUCKET"
