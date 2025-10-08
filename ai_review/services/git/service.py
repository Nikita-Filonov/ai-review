import subprocess
from pathlib import Path

from ai_review.libs.logger import get_logger
from ai_review.services.git.types import GitServiceProtocol

logger = get_logger("GIT_SERVICE")


class GitService(GitServiceProtocol):
    def __init__(self, repo_dir: str = "."):
        self.repo_dir = Path(repo_dir)

    def run_git(self, *args: str) -> str:
        cmd = ["git", *args]
        logger.debug(f"Running git command: {' '.join(cmd)} (cwd={self.repo_dir})")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stderr.strip():
                logger.debug(f"Git stderr: {result.stderr.strip()}")
            return result.stdout
        except subprocess.CalledProcessError as error:
            logger.warning(
                f"Git command failed (exit={error.returncode}): {' '.join(cmd)}\n"
                f"stderr: {error.stderr.strip()}"
            )
            raise

    def get_diff(self, base_sha: str, head_sha: str, unified: int = 3) -> str:
        return self.run_git("diff", f"--unified={unified}", base_sha, head_sha)

    def get_diff_for_file(self, base_sha: str, head_sha: str, file: str, unified: int = 3) -> str:
        if not file:
            logger.warning(f"Skipping git diff for empty filename (base={base_sha}, head={head_sha})")
            return ""

        logger.debug(f"Generating diff for {file} between {base_sha}..{head_sha}")
        output = self.run_git("diff", f"--unified={unified}", base_sha, head_sha, "--", file)
        if not output.strip():
            logger.info(f"No diff found for {file} (possibly deleted or not tracked)")

        return output

    def get_changed_files(self, base_sha: str, head_sha: str) -> list[str]:
        output = self.run_git("diff", "--name-only", base_sha, head_sha)
        files = [line.strip() for line in output.splitlines() if line.strip()]
        logger.debug(f"Changed files between {base_sha}..{head_sha}: {files}")
        return files

    def get_file_at_commit(self, file_path: str, sha: str) -> str | None:
        if not file_path:
            logger.warning(f"Skipping git show for empty file_path at {sha}")
            return None

        try:
            return self.run_git("show", f"{sha}:{file_path}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"File '{file_path}' not found in commit {sha}: {e.stderr.strip()}")
            return None
