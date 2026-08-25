import urllib.request
import urllib.parse
import json
from typing import Dict, Tuple, Optional

class GitHubAPI:
    """GitHub REST API Client using standard urllib (no third-party dependencies required)."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token.strip() if token else None

    def set_token(self, token: str):
        self.token = token.strip() if token else None

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Easy-Push-Python-App"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def test_connection(self) -> Tuple[bool, str, Optional[Dict]]:
        """Verify GitHub Personal Access Token (PAT) and fetch authenticated user info."""
        if not self.token:
            return False, "No Personal Access Token provided.", None
        
        try:
            req = urllib.request.Request(f"{self.BASE_URL}/user", headers=self._headers())
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    username = data.get("login", "User")
                    return True, f"Connected successfully as '{username}'", data
                else:
                    return False, f"GitHub returned HTTP status {response.status}", None
        except urllib.error.HTTPError as e:
            if e.code == 401:
                return False, "Authentication failed: Invalid Personal Access Token.", None
            return False, f"HTTP Error {e.code}: {e.reason}", None
        except Exception as e:
            return False, f"Connection error: {str(e)}", None

    def get_repo_details(self, owner: str, repo: str) -> Tuple[bool, str, Optional[Dict]]:
        """Fetch remote repository metadata."""
        try:
            url = f"{self.BASE_URL}/repos/{owner}/{repo}"
            req = urllib.request.Request(url, headers=self._headers())
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return True, "Repository found.", data
                return False, f"HTTP status {response.status}", None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False, "Repository not found or private (Token may require repo scope).", None
            return False, f"HTTP Error {e.code}", None
        except Exception as e:
            return False, str(e), None

    def create_release(self, owner: str, repo: str, tag_name: str, title: str, body: str, draft: bool = False, prerelease: bool = False) -> Tuple[bool, str]:
        """Create a GitHub Release for a given tag."""
        if not self.token:
            return False, "GitHub Personal Access Token required to create releases."
        
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/releases"
        payload = {
            "tag_name": tag_name,
            "name": title or tag_name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease
        }
        
        data_bytes = json.dumps(payload).encode('utf-8')
        headers = self._headers()
        headers["Content-Type"] = "application/json"

        try:
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status in [200, 201]:
                    res_data = json.loads(response.read().decode('utf-8'))
                    html_url = res_data.get("html_url", "")
                    return True, f"Release published successfully! {html_url}"
                return False, f"Failed to create release (HTTP {response.status})"
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8', errors='ignore')
            return False, f"GitHub Release API Error ({e.code}): {err_msg}"
        except Exception as e:
            return False, f"Error: {str(e)}"
