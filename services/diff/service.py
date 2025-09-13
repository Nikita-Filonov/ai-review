from pathlib import Path

from config import settings
from libs.diff.models import Diff
from libs.diff.parser import DiffParser
from libs.logger import get_logger
from services.diff.mode import MAP_REVIEW_MODE

logger = get_logger("DIFF_SERVICE")


def marker_for_line(line_number: int, changed: set[int]) -> str:
    return f"   {settings.review.review_change_marker}" if line_number in changed else ""


class DiffService:
    @classmethod
    def parse(cls, raw_diff: str) -> Diff:
        if not raw_diff.strip():
            logger.debug("Received empty diff string")
            return Diff(files=[], raw=raw_diff)

        try:
            return DiffParser.parse(raw_diff)
        except Exception as error:
            logger.error(f"Failed to parse diff: {error}")
            raise

    @classmethod
    def apply_diff(cls, raw_diff: str, file_path: str) -> str:
        diff = cls.parse(raw_diff)
        changed = set(sum(diff.changed_lines().values(), []))

        file = Path(file_path)
        if not file.exists():
            logger.warning(f"File not found when applying diff: {file_path}")
            return f"# File {file_path} not found"

        try:
            file_lines = file.read_text(encoding="utf-8").splitlines()
        except Exception as error:
            logger.error(f"Failed to read file {file_path}: {error}")
            return f"# Failed to read {file_path}: {error}"

        if not file_lines:
            logger.debug(f"File {file_path} is empty")
            return f"# File {file_path} is empty"

        filter_mode_func = MAP_REVIEW_MODE[settings.review.mode]
        annotated = [
            f"{line_no}: {content}{marker_for_line(line_no, changed)}"
            for line_no, content in enumerate(file_lines, start=1)
            if filter_mode_func(line_no, changed)
        ]

        logger.debug(
            f"Annotated file {file_path}: {len(changed)} changed lines, {len(file_lines)} total"
        )
        return "\n".join(annotated)

    @classmethod
    def build_changed_lines_by_file(cls, raw_diff: str, file_path: str) -> dict[str, set[int]]:
        diff = cls.parse(raw_diff)
        changed = set(diff.changed_lines().get(file_path, []))
        logger.debug(f"Changed lines for {file_path}: {sorted(changed)}")
        return {file_path: changed}

    @classmethod
    def apply_diff_for_files(cls, diffs_by_file: dict[str, str]) -> list[str]:
        results: list[str] = []
        for file, raw_diff in diffs_by_file.items():
            if not raw_diff.strip():
                logger.debug(f"No diff for {file}, skipping")
                continue

            annotated = cls.apply_diff(raw_diff, file)
            results.append(f"# File: {file}\n{annotated}")

        return results
