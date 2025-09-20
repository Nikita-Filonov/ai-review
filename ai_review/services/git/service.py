import subprocess
from pathlib import Path

from ai_review.services.git.types import GitServiceProtocol


class GitService(GitServiceProtocol):
    def __init__(self, repo_dir: str = "."):
        self.repo_dir = Path(repo_dir)

    def run_git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def get_diff(self, base_sha: str, head_sha: str, unified: int = 3) -> str:
        return self.run_git("diff", f"--unified={unified}", base_sha, head_sha)

    def get_diff_for_file(self, base_sha: str, head_sha: str, file: str, unified: int = 3) -> str:
        return self.run_git("diff", f"--unified={unified}", base_sha, head_sha, "--", file)

    def get_changed_files(self, base_sha: str, head_sha: str) -> list[str]:
        output = self.run_git("diff", "--name-only", base_sha, head_sha)
        return [line.strip() for line in output.splitlines() if line.strip()]

    def get_file_at_commit(self, file_path: str, sha: str) -> str | None:
        try:
            return self.run_git("show", f"{sha}:{file_path}")
        except subprocess.CalledProcessError:
            return None
