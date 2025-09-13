import fnmatch

from config import settings
from libs.logger import get_logger

logger = get_logger("REVIEW_POLICY_SERVICE")


class ReviewPolicyService:
    @classmethod
    def should_review(cls, file: str) -> bool:
        review = settings.review

        for pattern in review.ignore_changes:
            if fnmatch.fnmatch(file, pattern):
                logger.debug(f"Skipping {file} (matched ignore: {pattern})")
                return False

        if not review.allow_changes:
            logger.debug(f"Allowing {file} (no allow rules, passed ignore)")
            return True

        for pattern in review.allow_changes:
            if fnmatch.fnmatch(file, pattern):
                logger.debug(f"Allowing {file} (matched allow: {pattern})")
                return True

        logger.debug(f"Skipping {file} (did not match any allow rule)")
        return False

    @classmethod
    def apply(cls, files: list[str]) -> list[str]:
        allowed = [file for file in files if cls.should_review(file)]
        skipped = [file for file in files if not cls.should_review(file)]

        if skipped:
            logger.info(f"Skipped {len(skipped)} files by policy: {skipped}")

        if allowed:
            logger.info(f"Proceeding with {len(allowed)} files after policy filter")

        return allowed
