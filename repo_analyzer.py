import os
import re
import configparser
from typing import Dict, List, Any, Optional, Tuple
from git_manager import GitManager

class RepoAnalyzer:
    """
    Self-analyzing engine that scans project directories, inspects .git structures,
    analyzes .gitignore rules, maps commit graphs/lineage, and generates actionable insights.
    """

    def __init__(self, git_mgr: GitManager):
        self.git_mgr = git_mgr

    def analyze_workspace(self, search_dir: str) -> Dict[str, Any]:
        """
        Scan directory for Git repositories, inspect .gitignore files,
        and collect comprehensive metadata.
        """
        search_dir = os.path.abspath(search_dir)
        git_dirs = self.find_git_repositories(search_dir)
        
        is_current_repo = self.git_mgr.is_git_repo()
        
        repo_info = {}
        if is_current_repo:
            repo_info = self.deep_analyze_current_repo()

        gitignore_analysis = self.analyze_gitignore_rules(search_dir)

        return {
            "root_dir": search_dir,
            "detected_git_repos": git_dirs,
            "is_valid_git_repo": is_current_repo,
            "current_repo_details": repo_info,
            "gitignore_analysis": gitignore_analysis
        }

    def find_git_repositories(self, root_dir: str, max_depth: int = 3) -> List[str]:
        """Recursively discover all .git folders within root_dir up to max_depth."""
        found_repos = []
        root_dir = os.path.abspath(root_dir)

        # Check if root itself is a repo
        if os.path.isdir(os.path.join(root_dir, ".git")):
            found_repos.append(root_dir)

        root_depth = root_dir.count(os.sep)
        for dirpath, dirnames, _ in os.walk(root_dir):
            current_depth = dirpath.count(os.sep) - root_depth
            if current_depth > max_depth:
                dirnames.clear()  # Don't recurse deeper
                continue

            if ".git" in dirnames:
                repo_path = os.path.abspath(dirpath)
                if repo_path not in found_repos:
                    found_repos.append(repo_path)
                # Don't recurse inside .git
                dirnames.remove(".git")

        return found_repos

    def deep_analyze_current_repo(self) -> Dict[str, Any]:
        """
        Deep analysis of current working repository:
        - Remote URLs & GitHub owner/repo extraction
        - Commit graph lineage (parents, commit tree)
        - Branch tracking & unsynced commit counts
        - Health warnings & suggestions
        """
        remotes = self.git_mgr.get_remotes()
        branch = self.git_mgr.get_current_branch()
        status = self.git_mgr.get_status()
        history = self.git_mgr.get_commit_history(limit=50)

        # Extract GitHub repo details from origin URL
        github_details = self._parse_github_url(remotes.get("origin", ""))

        # Analyze commit lineage (parents graph)
        lineage = self._analyze_commit_lineage()

        # Check unpushed / unpulled status
        unpushed_count, unpulled_count = self._get_sync_divergence(branch)

        # Health assessment
        warnings = []
        if not remotes:
            warnings.append("⚠️ No remote origin URL configured. Pushing to GitHub is disabled until a remote is added.")
        elif not github_details:
            warnings.append("⚠️ Remote URL is not a standard GitHub repository link.")

        total_uncommitted = len(status["staged"]) + len(status["unstaged"]) + len(status["untracked"])
        if total_uncommitted > 0:
            warnings.append(f"ℹ️ You have {total_uncommitted} uncommitted change(s). Use One-Click Smart Auto-Push to commit them.")

        if unpushed_count > 0:
            warnings.append(f"🚀 You have {unpushed_count} local commit(s) ready to push to GitHub!")

        if unpulled_count > 0:
            warnings.append(f"⬇️ Remote has {unpulled_count} commit(s) ahead of your local branch. Pull before pushing.")

        return {
            "branch": branch,
            "remotes": remotes,
            "github_info": github_details,
            "status": status,
            "commit_history_sample": history,
            "lineage_graph": lineage,
            "unpushed_commits": unpushed_count,
            "unpulled_commits": unpulled_count,
            "health_warnings": warnings
        }

    def _parse_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """Parse owner, repo name, and web link from git remote URL."""
        if not url:
            return None

        # Regex for https://github.com/owner/repo or git@github.com:owner/repo
        match = re.search(r'github\.com[:/]([^/]+)/([^/\.]+)', url)
        if match:
            owner = match.group(1)
            repo_name = match.group(2).replace(".git", "")
            return {
                "owner": owner,
                "repo": repo_name,
                "web_url": f"https://github.com/{owner}/{repo_name}"
            }
        return None

    def _analyze_commit_lineage(self) -> List[Dict[str, str]]:
        """Fetch raw parent relationships for commits: Hash | Short Hash | Parent Hashes | Author | Date | Subject."""
        code, stdout, _ = self.git_mgr._run_git(["log", "-n25", "--pretty=format:%H|%h|%P|%an|%ad|%s", "--date=short"])
        lineage = []
        if code == 0 and stdout:
            for line in stdout.splitlines():
                parts = line.split("|", 5)
                if len(parts) == 6:
                    parents = parts[2].split() if parts[2] else []
                    lineage.append({
                        "hash": parts[0],
                        "short_hash": parts[1],
                        "parents": parents,
                        "author": parts[3],
                        "date": parts[4],
                        "subject": parts[5]
                    })
        return lineage

    def _get_sync_divergence(self, branch: str) -> Tuple[int, int]:
        """Count how many commits local is ahead/behind remote."""
        code, stdout, _ = self.git_mgr._run_git(["rev-list", "--left-right", "--count", f"@{'{u}'}...HEAD"])
        if code == 0 and stdout:
            parts = stdout.strip().split()
            if len(parts) == 2:
                try:
                    behind = int(parts[0])
                    ahead = int(parts[1])
                    return ahead, behind
                except ValueError:
                    pass
        return 0, 0

    def analyze_gitignore_rules(self, repo_dir: str) -> Dict[str, Any]:
        """Inspect .gitignore rules and verify if sensitive files are protected."""
        gitignore_file = os.path.join(repo_dir, ".gitignore")
        exists = os.path.exists(gitignore_file)
        rules = []

        if exists:
            try:
                with open(gitignore_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            rules.append(line)
            except Exception:
                pass

        # Check critical file protection (.env, secrets, node_modules, build dirs, __pycache__)
        sensitive_patterns = [".env", "node_modules/", "__pycache__/", "*.pem", "*.key", "build/", "dist/", ".venv/"]
        protected_status = {}
        
        for pattern in sensitive_patterns:
            protected_status[pattern] = any(
                rule == pattern or rule.rstrip('/') == pattern.rstrip('/') or pattern.startswith(rule.lstrip('*'))
                for rule in rules
            )

        return {
            "exists": exists,
            "file_path": gitignore_file if exists else None,
            "rule_count": len(rules),
            "rules_sample": rules[:20],
            "protected_patterns": protected_status
        }
