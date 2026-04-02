import os
import re
import base64
import time
import logging
import requests
from getpass import getpass
from typing import Optional, List, Dict, Tuple, Any

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when GitHub API rate limit is exceeded."""
    def __init__(self, reset_time: int = 0):
        self.reset_time = reset_time
        super().__init__(f"Rate limit exceeded. Resets in {reset_time} seconds.")


class GitHubClient:
    """
    GitHub API client with authentication, retry logic,
    rate limit handling, and comprehensive repo access.
    """

    MAX_RETRIES = 3
    RETRY_DELAY = 2

    def __init__(self):
        self.token: Optional[str] = None
        self.username: Optional[str] = None
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RepoAnalyzer/2.0"
        })
        self.is_authenticated = False
        self._rate_remaining = 60
        self._rate_limit = 60

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make an API request with retry logic and rate limit handling.

        Args:
            method: HTTP method (get, post, put, etc.)
            url: Full URL to request
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            RateLimitError: If rate limit is exceeded and cannot wait
            Exception: If all retries fail
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.request(method, url, **kwargs)

                # Update rate limit info
                self._rate_remaining = int(response.headers.get("X-RateLimit-Remaining", 60))
                self._rate_limit = int(response.headers.get("X-RateLimit-Limit", 60))

                # Handle rate limiting
                if response.status_code == 403:
                    remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
                    if remaining == 0:
                        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                        wait_seconds = max(reset_time - int(time.time()), 0) + 1
                        if wait_seconds <= 300:  # Wait up to 5 minutes
                            logger.warning(f"Rate limited. Waiting {wait_seconds}s...")
                            print(f"  ⏳ Rate limited. Waiting {wait_seconds} seconds...")
                            time.sleep(wait_seconds)
                            continue
                        else:
                            raise RateLimitError(wait_seconds)

                # Handle server errors with retry
                if response.status_code >= 500:
                    if attempt < self.MAX_RETRIES - 1:
                        wait = self.RETRY_DELAY * (attempt + 1)
                        logger.warning(f"Server error {response.status_code}, retry in {wait}s")
                        time.sleep(wait)
                        continue

                return response

            except requests.exceptions.ConnectionError as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    wait = self.RETRY_DELAY * (attempt + 1)
                    logger.warning(f"Connection error, retry in {wait}s: {e}")
                    print(f"  ⚠️ Connection error, retrying in {wait}s...")
                    time.sleep(wait)
                    continue

            except requests.exceptions.Timeout as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    wait = self.RETRY_DELAY * (attempt + 1)
                    logger.warning(f"Timeout, retry in {wait}s")
                    time.sleep(wait)
                    continue

        raise Exception(f"Failed after {self.MAX_RETRIES} retries: {last_error}")

    def authenticate(self, token: str) -> Dict[str, Any]:
        """
        Authenticate with GitHub using a personal access token.

        Args:
            token: GitHub personal access token

        Returns:
            Dictionary with user information

        Raises:
            Exception: If authentication fails
        """
        self.token = token
        self.session.headers.update({"Authorization": f"token {token}"})

        response = self._request("get", f"{self.base_url}/user")

        if response.status_code == 200:
            data = response.json()
            self.username = data.get("login")
            self.is_authenticated = True

            return {
                "username": data.get("login"),
                "name": data.get("name", "N/A"),
                "email": data.get("email", "N/A"),
                "bio": data.get("bio", "N/A"),
                "company": data.get("company", "N/A"),
                "location": data.get("location", "N/A"),
                "public_repos": data.get("public_repos", 0),
                "private_repos": data.get("total_private_repos", 0),
                "total_repos": data.get("public_repos", 0) + data.get("total_private_repos", 0),
                "followers": data.get("followers", 0),
                "following": data.get("following", 0),
                "html_url": data.get("html_url", ""),
                "avatar_url": data.get("avatar_url", ""),
                "created_at": data.get("created_at", ""),
                "disk_usage": data.get("disk_usage", 0),
                "plan": data.get("plan", {}).get("name", "free"),
                "two_factor_authentication": data.get("two_factor_authentication", False),
            }

        if response.status_code == 401:
            raise Exception("Authentication failed: Invalid token")
        raise Exception(f"Authentication failed: HTTP {response.status_code}")

    @staticmethod
    def get_token_secure() -> str:
        """
        Get GitHub token securely from environment variable or user input.
        Uses getpass to hide input when possible.

        Returns:
            GitHub token string
        """
        # Check environment variable first
        token = os.environ.get("GITHUB_TOKEN", "").strip()
        if token:
            print("  🔑 Using token from GITHUB_TOKEN environment variable")
            return token

        # Try getpass (hides input)
        try:
            token = getpass("🔑 Enter your GitHub Token (hidden): ").strip()
        except Exception:
            # Fallback for environments where getpass doesn't work (like some notebooks)
            token = input("🔑 Enter your GitHub Token: ").strip()

        return token

    def get_token_scopes(self) -> List[str]:
        """Get the scopes/permissions of the current token."""
        response = self._request("get", f"{self.base_url}/user")
        if response.status_code == 200:
            scopes = response.headers.get("X-OAuth-Scopes", "")
            return [s.strip() for s in scopes.split(",") if s.strip()]
        return []

    def get_rate_limit(self) -> Dict[str, int]:
        """Get current API rate limit status."""
        response = self._request("get", f"{self.base_url}/rate_limit")
        if response.status_code == 200:
            core = response.json().get("rate", {})
            return {
                "limit": core.get("limit", 0),
                "remaining": core.get("remaining", 0),
                "reset": core.get("reset", 0)
            }
        return {"limit": 60, "remaining": self._rate_remaining, "reset": 0}

    def get_user_repos(self, include_private: bool = True, sort: str = "updated") -> List[Dict]:
        """
        Get all repositories for the authenticated user.

        Args:
            include_private: Include private repositories
            sort: Sort by (updated, created, pushed, full_name)

        Returns:
            List of repository dictionaries
        """
        if not self.is_authenticated:
            raise Exception("Must authenticate first!")

        repos = []
        page = 1

        while True:
            response = self._request("get", f"{self.base_url}/user/repos", params={
                "sort": sort,
                "direction": "desc",
                "per_page": 100,
                "page": page,
                "type": "all" if include_private else "public"
            })

            if response.status_code != 200:
                raise Exception(f"Failed to fetch repos: HTTP {response.status_code}")

            data = response.json()
            if not data:
                break

            for repo in data:
                repos.append({
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "description": repo.get("description", "No description"),
                    "private": repo.get("private", False),
                    "html_url": repo.get("html_url"),
                    "language": repo.get("language", "Unknown"),
                    "size": repo.get("size", 0),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "open_issues": repo.get("open_issues_count", 0),
                    "default_branch": repo.get("default_branch", "main"),
                    "created_at": repo.get("created_at", ""),
                    "updated_at": repo.get("updated_at", ""),
                    "topics": repo.get("topics", []),
                    "license": (repo.get("license") or {}).get("name", "None"),
                    "archived": repo.get("archived", False),
                    "fork": repo.get("fork", False),
                })

            page += 1
            if len(data) < 100:
                break

        return repos

    def parse_repo_url(self, url: str) -> Tuple[str, str]:
        """
        Parse a GitHub repository URL or owner/repo string.

        Args:
            url: GitHub URL or owner/repo format

        Returns:
            Tuple of (owner, repo_name)

        Raises:
            ValueError: If URL format is invalid
        """
        url = url.strip().rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]

        patterns = [
            r"github\.com/([^/]+)/([^/]+)",
            r"^([^/\s]+)/([^/\s]+)$"
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), match.group(2)

        raise ValueError(
            f"Invalid repository URL: {url}\n"
            f"Use format: owner/repo or https://github.com/owner/repo"
        )

    def get_repo_info(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a repository.

        Args:
            owner: Repository owner username
            repo_name: Repository name

        Returns:
            Dictionary with repository information
        """
        response = self._request("get", f"{self.base_url}/repos/{owner}/{repo_name}")

        if response.status_code == 200:
            repo = response.json()
            return {
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description", "No description"),
                "private": repo.get("private", False),
                "html_url": repo.get("html_url"),
                "language": repo.get("language", "Unknown"),
                "size": repo.get("size", 0),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "open_issues": repo.get("open_issues_count", 0),
                "default_branch": repo.get("default_branch", "main"),
                "created_at": repo.get("created_at", ""),
                "updated_at": repo.get("updated_at", ""),
                "topics": repo.get("topics", []),
                "license": (repo.get("license") or {}).get("name", "None"),
                "subscribers_count": repo.get("subscribers_count", 0),
                "owner": {
                    "login": repo.get("owner", {}).get("login"),
                    "avatar_url": repo.get("owner", {}).get("avatar_url"),
                    "html_url": repo.get("owner", {}).get("html_url"),
                },
            }
        elif response.status_code == 404:
            raise Exception(f"Repository not found: {owner}/{repo_name}")
        elif response.status_code == 403:
            raise Exception(f"Access denied: {owner}/{repo_name} (check token permissions)")
        else:
            raise Exception(f"Error fetching repo info: HTTP {response.status_code}")

    def get_repo_tree(self, owner: str, repo_name: str, branch: Optional[str] = None) -> List[Dict]:
        """
        Get the complete file tree of a repository.

        Args:
            owner: Repository owner
            repo_name: Repository name
            branch: Branch name (uses default if None)

        Returns:
            List of file/directory dictionaries
        """
        if not branch:
            info = self.get_repo_info(owner, repo_name)
            branch = info["default_branch"]

        response = self._request(
            "get",
            f"{self.base_url}/repos/{owner}/{repo_name}/git/trees/{branch}",
            params={"recursive": "1"}
        )

        if response.status_code == 200:
            return [
                {
                    "path": item.get("path"),
                    "type": item.get("type"),
                    "size": item.get("size", 0),
                    "sha": item.get("sha"),
                }
                for item in response.json().get("tree", [])
            ]

        raise Exception(f"Failed to get file tree: HTTP {response.status_code}")

    def get_file_content(self, owner: str, repo_name: str,
                         file_path: str, branch: Optional[str] = None) -> Optional[str]:
        """
        Get the content of a specific file.

        Args:
            owner: Repository owner
            repo_name: Repository name
            file_path: Path to file in repository
            branch: Branch name (uses default if None)

        Returns:
            File content as string, or None if not found
        """
        params = {"ref": branch} if branch else {}

        response = self._request(
            "get",
            f"{self.base_url}/repos/{owner}/{repo_name}/contents/{file_path}",
            params=params
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("encoding") == "base64":
                try:
                    return base64.b64decode(data["content"]).decode("utf-8")
                except UnicodeDecodeError:
                    return f"[Binary file: {file_path}]"
            return data.get("content", "")
        elif response.status_code == 404:
            return None

        return f"[Error reading file: HTTP {response.status_code}]"

    def get_repo_languages(self, owner: str, repo_name: str) -> Dict[str, int]:
        """Get language breakdown for a repository."""
        response = self._request("get", f"{self.base_url}/repos/{owner}/{repo_name}/languages")
        return response.json() if response.status_code == 200 else {}

    def get_repo_branches(self, owner: str, repo_name: str) -> List[str]:
        """Get all branch names for a repository."""
        response = self._request(
            "get",
            f"{self.base_url}/repos/{owner}/{repo_name}/branches",
            params={"per_page": 100}
        )
        if response.status_code == 200:
            return [branch["name"] for branch in response.json()]
        return []

    def get_repo_contributors(self, owner: str, repo_name: str) -> List[Dict]:
        """Get contributors for a repository."""
        response = self._request(
            "get",
            f"{self.base_url}/repos/{owner}/{repo_name}/contributors",
            params={"per_page": 30}
        )
        if response.status_code == 200:
            return [
                {
                    "login": contributor.get("login"),
                    "contributions": contributor.get("contributions", 0),
                    "html_url": contributor.get("html_url"),
                }
                for contributor in response.json()
            ]
        return []

    def get_latest_commits(self, owner: str, repo_name: str,
                           count: int = 10, branch: Optional[str] = None) -> List[Dict]:
        """Get latest commits for a repository."""
        params = {"per_page": count}
        if branch:
            params["sha"] = branch

        response = self._request(
            "get",
            f"{self.base_url}/repos/{owner}/{repo_name}/commits",
            params=params
        )

        if response.status_code == 200:
            return [
                {
                    "sha": commit.get("sha", "")[:7],
                    "message": commit.get("commit", {}).get("message", ""),
                    "author": commit.get("commit", {}).get("author", {}).get("name", ""),
                    "date": commit.get("commit", {}).get("author", {}).get("date", ""),
                    "html_url": commit.get("html_url", ""),
                }
                for commit in response.json()
            ]
        return []

    def clear_token(self):
        """Clear the stored token from memory for security."""
        self.token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        self.is_authenticated = False
        self.username = None
