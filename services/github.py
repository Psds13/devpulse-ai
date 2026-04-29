import httpx
import re
from typing import Tuple, List, Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)

class GitHubService:
    def __init__(self, token: str = None):
        self.token = token
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def parse_repo_url(self, url: str) -> Tuple[str, str]:
        # Extract owner and name from https://github.com/owner/name
        # Supports ending in .git or not
        match = re.search(r"github\.com/([^/]+)/([^/]+)", url)
        if match:
            return match.group(1), match.group(2).replace(".git", "")
        raise ValueError("Invalid GitHub URL")

    async def get_recent_commits(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error fetching commits for {owner}/{repo}: {e}")
                return []

    async def get_commit_details(self, owner: str, repo: str, commit_sha: str) -> Dict[str, Any]:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error fetching commit details {commit_sha}: {e}")
                return {}
