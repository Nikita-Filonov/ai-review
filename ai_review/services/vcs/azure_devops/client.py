from collections import defaultdict
from urllib.parse import urlparse

from ai_review.clients.azure_devops.client import get_azure_devops_http_client
from ai_review.clients.azure_devops.pr.schema.threads import (
    AzureDevOpsCreateThreadRequestSchema,
    AzureDevOpsCreateCommentRequestSchema
)
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.azure_devops.adapter import get_review_comment_from_azure_devops_comment
from ai_review.services.vcs.types import (
    VCSClientProtocol,
    ThreadKind,
    UserSchema,
    BranchRefSchema,
    ReviewInfoSchema,
    ReviewThreadSchema,
    ReviewCommentSchema,
)

logger = get_logger("AZURE_DEVOPS_VCS_CLIENT")


def extract_organization_name(organization_url: str) -> str:
    """
    Extract organization name from Azure DevOps URL.
    
    Supports formats:
    - https://dev.azure.com/organization/
    - https://organization.visualstudio.com/
    - organization (already just the name)
    """
    # If it's not a URL, assume it's already the organization name
    if not organization_url.startswith(('http://', 'https://')):
        return organization_url.strip('/')
    
    parsed = urlparse(organization_url)
    
    # Format: https://dev.azure.com/organization/
    if 'dev.azure.com' in parsed.netloc:
        path_parts = parsed.path.strip('/').split('/')
        return path_parts[0] if path_parts else ''
    
    # Format: https://organization.visualstudio.com/
    if 'visualstudio.com' in parsed.netloc:
        return parsed.netloc.split('.')[0]
    
    # Fallback: return as is
    return organization_url.strip('/')


class AzureDevOpsVCSClient(VCSClientProtocol):
    def __init__(self):
        self.http_client = get_azure_devops_http_client()
        # Extract organization name from URL if needed
        self.organization = extract_organization_name(settings.vcs.pipeline.organization)
        self.project = settings.vcs.pipeline.project
        self.repository_id = settings.vcs.pipeline.repository_id
        self.pull_request_id = settings.vcs.pipeline.pull_request_id
        self.pr_ref = f"{self.organization}/{self.project}/{self.repository_id}/PR#{self.pull_request_id}"

    # --- Review info ---
    async def get_review_info(self) -> ReviewInfoSchema:
        try:
            pr = await self.http_client.pr.get_pull_request(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id
            )
            
            changes = await self.http_client.pr.get_changes(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id
            )

            logger.info(f"Fetched PR info for {self.pr_ref}")
            logger.debug(f"Raw changes response: {changes}")
            logger.info(f"Number of changes: {len(changes.changes)}")

            changed_files = []
            for change in changes.changes:
                logger.debug(f"Processing change: {change}")
                # Azure DevOps change structure: item can have 'path' key
                if isinstance(change.item, dict):
                    file_path = change.item.get("path", "")
                    if file_path:
                        # Remove leading '/' if present
                        file_path = file_path.lstrip('/')
                        # Only include files, not directories
                        # Check if it's a file by looking for file extension or common file names
                        filename = file_path.split('/')[-1]
                        is_file = ('.' in filename or 
                                 filename.lower() in ['readme', 'makefile', 'dockerfile', 'docker-compose.yml', 'package.json', 'requirements.txt'])
                        
                        if is_file:
                            changed_files.append(file_path)
                            logger.debug(f"Added file: {file_path}")
                        else:
                            logger.debug(f"Skipped directory: {file_path}")
            
            logger.info(f"Total changed files found: {len(changed_files)}")

            # Get commit SHAs with fallback to HEAD and base branch
            source_sha = ""
            target_sha = ""
            
            if pr.last_merge_source_commit:
                source_sha = pr.last_merge_source_commit.get("commitId", "")
            if pr.last_merge_target_commit:
                target_sha = pr.last_merge_target_commit.get("commitId", "")
            
            # If SHAs are missing, use branch refs as fallback
            if not source_sha:
                source_sha = pr.source_ref_name
                logger.warning(f"Source commit SHA not found, using branch ref: {source_sha}")
            if not target_sha:
                target_sha = pr.target_ref_name
                logger.warning(f"Target commit SHA not found, using branch ref: {target_sha}")
            
            logger.info(f"PR SHAs - Source: {source_sha}, Target: {target_sha}")

            return ReviewInfoSchema(
                id=pr.pull_request_id,
                title=pr.title,
                description=pr.description,
                author=UserSchema(
                    id=pr.created_by.id,
                    name=pr.created_by.display_name,
                    username=pr.created_by.unique_name,
                ),
                labels=[label.name for label in pr.labels if label.name],
                base_sha=target_sha,
                head_sha=source_sha,
                assignees=[],
                reviewers=[
                    UserSchema(id=user.id, name=user.display_name, username=user.unique_name)
                    for user in pr.reviewers
                ],
                source_branch=BranchRefSchema(
                    ref=pr.source_ref_name,
                    sha=source_sha,
                ),
                target_branch=BranchRefSchema(
                    ref=pr.target_ref_name,
                    sha=target_sha,
                ),
                changed_files=changed_files,
            )
        except Exception as error:
            logger.exception(f"Failed to fetch PR info {self.pr_ref}: {error}")
            return ReviewInfoSchema()

    # --- Comments ---
    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        """Get all non-inline comments (threads without file context)"""
        try:
            response = await self.http_client.pr.get_threads(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id
            )
            
            comments = []
            for thread in response.root:
                # Only include threads without file context (general comments)
                if not thread.thread_context:
                    for comment in thread.comments:
                        comments.append(get_review_comment_from_azure_devops_comment(comment, thread))
            
            logger.info(f"Fetched {len(comments)} general comments for {self.pr_ref}")
            return comments
        except Exception as error:
            logger.exception(f"Failed to fetch general comments for {self.pr_ref}: {error}")
            return []

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        """Get all inline comments (threads with file context)"""
        try:
            response = await self.http_client.pr.get_threads(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id
            )
            
            comments = []
            for thread in response.root:
                # Only include threads with file context (inline comments)
                if thread.thread_context:
                    for comment in thread.comments:
                        comments.append(get_review_comment_from_azure_devops_comment(comment, thread))
            
            logger.info(f"Fetched {len(comments)} inline comments for {self.pr_ref}")
            return comments
        except Exception as error:
            logger.exception(f"Failed to fetch inline comments for {self.pr_ref}: {error}")
            return []

    async def create_general_comment(self, message: str) -> None:
        """Create a general (non-inline) comment"""
        try:
            logger.info(f"Posting general comment to PR {self.pr_ref}")
            request = AzureDevOpsCreateThreadRequestSchema(
                comments=[{"content": message}],
                status="active"
            )
            await self.http_client.pr.create_thread(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
                request=request
            )
            logger.info(f"Created general comment in PR {self.pr_ref}")
        except Exception as error:
            logger.exception(f"Failed to create general comment in PR {self.pr_ref}: {error}")
            raise

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        """Create an inline comment on a specific file and line"""
        try:
            logger.info(f"Posting inline comment in {self.pr_ref} at {file}:{line}")
            logger.debug(f"Original file path: '{file}'")
            
            # Get PR info to get the latest commit SHA
            pr = await self.http_client.pr.get_pull_request(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id
            )
            
            # Azure DevOps requires filePath to start with '/'
            file_path = f'/{file}' if not file.startswith('/') else file
            logger.debug(f"Formatted file path: '{file_path}'")
            
            # Thread context for inline comment on Files tab
            # Must use camelCase keys for Azure DevOps API
            thread_context = {
                "filePath": file_path,
                "rightFileStart": {"line": line, "offset": 1},
                "rightFileEnd": {"line": line, "offset": 1}
            }
            
            logger.debug(f"Thread context: {thread_context}")
            
            # Create request with threadContext (using alias)
            request_dict = {
                "comments": [{"content": message}],
                "status": "active",
                "threadContext": thread_context  # Use camelCase key directly
            }
            
            logger.debug(f"Request: {request_dict}")
            
            # Call API directly with dict instead of Pydantic model
            await self.http_client.pr.create_thread_with_dict(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
                request_dict=request_dict
            )
            logger.info(f"✅ Created inline comment in {self.pr_ref} at {file}:{line} (will appear on Files tab)")
        except Exception as error:
            logger.exception(f"Failed to create inline comment in {self.pr_ref} at {file}:{line}: {error}")
            raise

    # --- Replies ---
    async def create_inline_reply(self, thread_id: int | str, message: str) -> None:
        """Reply to an existing inline comment thread"""
        try:
            logger.info(f"Replying to inline thread {thread_id} in PR {self.pr_ref}")
            request = AzureDevOpsCreateCommentRequestSchema(
                content=message,
                parent_comment_id=0
            )
            await self.http_client.pr.create_comment(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
                thread_id=int(thread_id),
                request=request
            )
            logger.info(f"Created inline reply to thread {thread_id} in PR {self.pr_ref}")
        except Exception as error:
            logger.exception(f"Failed to create inline reply to thread {thread_id} in {self.pr_ref}: {error}")
            raise

    async def create_summary_reply(self, thread_id: int | str, message: str) -> None:
        """Reply to an existing summary/general comment thread"""
        try:
            logger.info(f"Replying to general thread {thread_id} in PR {self.pr_ref}")
            request = AzureDevOpsCreateCommentRequestSchema(
                content=message,
                parent_comment_id=0
            )
            await self.http_client.pr.create_comment(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
                thread_id=int(thread_id),
                request=request
            )
            logger.info(f"Created summary reply to thread {thread_id} in PR {self.pr_ref}")
        except Exception as error:
            logger.exception(f"Failed to create summary reply to thread {thread_id} in {self.pr_ref}: {error}")
            raise

    # --- Threads ---
    async def get_inline_threads(self) -> list[ReviewThreadSchema]:
        """Get all inline comment threads (with file context)"""
        try:
            response = await self.http_client.pr.get_threads(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id
            )
            
            threads = []
            for thread in response.root:
                # Only include threads with file context
                if thread.thread_context:
                    comments = [
                        get_review_comment_from_azure_devops_comment(comment, thread)
                        for comment in thread.comments
                    ]
                    
                    file_path = thread.thread_context.file_path
                    line = None
                    if thread.thread_context.right_file_end:
                        line = thread.thread_context.right_file_end.get("line")
                    
                    threads.append(ReviewThreadSchema(
                        id=thread.id,
                        kind=ThreadKind.INLINE,
                        file=file_path,
                        line=line,
                        comments=sorted(comments, key=lambda c: int(c.id))
                    ))
            
            logger.info(f"Built {len(threads)} inline threads for {self.pr_ref}")
            return threads
        except Exception as error:
            logger.exception(f"Failed to fetch inline threads for {self.pr_ref}: {error}")
            return []

    async def get_general_threads(self) -> list[ReviewThreadSchema]:
        """Get all general comment threads (without file context)"""
        try:
            response = await self.http_client.pr.get_threads(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id
            )
            
            threads = []
            for thread in response.root:
                # Only include threads without file context
                if not thread.thread_context:
                    comments = [
                        get_review_comment_from_azure_devops_comment(comment, thread)
                        for comment in thread.comments
                    ]
                    
                    threads.append(ReviewThreadSchema(
                        id=thread.id,
                        kind=ThreadKind.SUMMARY,
                        comments=sorted(comments, key=lambda c: int(c.id))
                    ))
            
            logger.info(f"Built {len(threads)} general threads for {self.pr_ref}")
            return threads
        except Exception as error:
            logger.exception(f"Failed to build general threads for {self.pr_ref}: {error}")
            return []

