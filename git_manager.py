import os
import subprocess
import re
from typing import List, Dict, Tuple, Optional

class GitManager:
    """Handles low-level Git commands for a specific working directory."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)

    def set_repo_path(self, repo_path: str) -> bool:
        """Update active repository directory path."""
        abs_path = os.path.abspath(repo_path)
        if os.path.isdir(abs_path):
            self.repo_path = abs_path
            return True
        return False

    def _run_git(self, args: List[str]) -> Tuple[int, str, str]:
        """Execute a git command in the repository path."""
        try:
            # Set creationflags on Windows to avoid opening popup console windows
            creation_flags = 0
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                ["git"] + args,
                cwd=self.repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=creation_flags
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout.strip(), stderr.strip()
        except FileNotFoundError:
            return -1, "", "Git executable not found on system PATH."
        except Exception as e:
            return -1, "", str(e)

    def is_git_repo(self) -> bool:
        """Check if current path is inside a valid Git repository."""
        code, stdout, _ = self._run_git(["rev-parse", "--is-inside-work-tree"])
        return code == 0 and stdout == "true"

    def init_repo(self) -> Tuple[bool, str]:
        """Initialize a new Git repository."""
        code, stdout, stderr = self._run_git(["init"])
        if code == 0:
            return True, stdout
        return False, stderr

    def get_current_branch(self) -> str:
        """Get the name of the active branch."""
        code, stdout, _ = self._run_git(["branch", "--show-current"])
        if code == 0 and stdout:
            return stdout
        # Fallback for detached HEAD or older git versions
        code, stdout, _ = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        return stdout if code == 0 else "main"

    def get_branches(self) -> Tuple[List[str], List[str]]:
        """Return list of (local_branches, remote_branches)."""
        code, stdout, _ = self._run_git(["branch", "-a"])
        local_branches = []
        remote_branches = []
        if code == 0 and stdout:
            for line in stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                branch_name = line.lstrip("* ").strip()
                if branch_name.startswith("remotes/"):
                    if " -> " not in branch_name:
                        remote_branches.append(branch_name)
                else:
                    local_branches.append(branch_name)
        return local_branches, remote_branches

    def create_branch(self, branch_name: str, checkout: bool = True) -> Tuple[bool, str]:
        """Create a new branch and optionally switch to it."""
        args = ["checkout", "-b", branch_name] if checkout else ["branch", branch_name]
        code, stdout, stderr = self._run_git(args)
        return (code == 0, stdout if code == 0 else stderr)

    def switch_branch(self, branch_name: str) -> Tuple[bool, str]:
        """Switch to an existing branch."""
        code, stdout, stderr = self._run_git(["checkout", branch_name])
        return (code == 0, stdout if code == 0 else stderr)

    def delete_branch(self, branch_name: str, force: bool = False) -> Tuple[bool, str]:
        """Delete a local branch."""
        flag = "-D" if force else "-d"
        code, stdout, stderr = self._run_git(["branch", flag, branch_name])
        return (code == 0, stdout if code == 0 else stderr)

    def get_status(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get structured repository status (staged, unstaged, untracked).
        Returns dict with keys: 'staged', 'unstaged', 'untracked'.
        """
        code, stdout, _ = self._run_git(["status", "--porcelain=v1"])
        result = {"staged": [], "unstaged": [], "untracked": []}
        if code != 0 or not stdout:
            return result

        for line in stdout.splitlines():
            if len(line) < 3:
                continue
            index_status = line[0]
            work_tree_status = line[1]
            filepath = line[3:].strip()

            # Handle renamed files (e.g. "R  orig -> new")
            if " -> " in filepath:
                filepath = filepath.split(" -> ")[-1]

            if index_status in ['M', 'A', 'D', 'R', 'C']:
                status_desc = self._code_to_desc(index_status)
                result["staged"].append({"file": filepath, "status": status_desc, "code": index_status})
            
            if work_tree_status in ['M', 'D']:
                status_desc = self._code_to_desc(work_tree_status)
                result["unstaged"].append({"file": filepath, "status": status_desc, "code": work_tree_status})

            if index_status == '?' and work_tree_status == '?':
                result["untracked"].append({"file": filepath, "status": "Untracked", "code": "?"})

        return result

    def _code_to_desc(self, code_char: str) -> str:
        mapping = {
            'M': 'Modified',
            'A': 'Added',
            'D': 'Deleted',
            'R': 'Renamed',
            'C': 'Copied',
            '?': 'Untracked'
        }
        return mapping.get(code_char, 'Changed')

    def stage_all(self) -> Tuple[bool, str]:
        """Stage all changes (including untracked)."""
        code, stdout, stderr = self._run_git(["add", "-A"])
        return (code == 0, stdout if code == 0 else stderr)

    def stage_file(self, filepath: str) -> Tuple[bool, str]:
        """Stage a specific file."""
        code, stdout, stderr = self._run_git(["add", filepath])
        return (code == 0, stdout if code == 0 else stderr)

    def unstage_all(self) -> Tuple[bool, str]:
        """Unstage all staged files."""
        code, stdout, stderr = self._run_git(["reset"])
        return (code == 0, stdout if code == 0 else stderr)

    def unstage_file(self, filepath: str) -> Tuple[bool, str]:
        """Unstage a specific file."""
        code, stdout, stderr = self._run_git(["reset", "HEAD", "--", filepath])
        return (code == 0, stdout if code == 0 else stderr)

    def commit(self, message: str) -> Tuple[bool, str]:
        """Create a commit with the provided message."""
        if not message.strip():
            return False, "Commit message cannot be empty."
        code, stdout, stderr = self._run_git(["commit", "-m", message])
        return (code == 0, stdout if code == 0 else stderr)

    def push(self, remote: str = "origin", branch: Optional[str] = None, set_upstream: bool = True) -> Tuple[bool, str]:
        """Push commits to remote repository."""
        target_branch = branch or self.get_current_branch()
        args = ["push"]
        if set_upstream:
            args.extend(["-u", remote, target_branch])
        else:
            args.extend([remote, target_branch])

        code, stdout, stderr = self._run_git(args)
        output = stdout + "\n" + stderr
        return (code == 0, output.strip())

    def pull(self, remote: str = "origin", branch: Optional[str] = None) -> Tuple[bool, str]:
        """Pull latest changes from remote repository."""
        target_branch = branch or self.get_current_branch()
        code, stdout, stderr = self._run_git(["pull", remote, target_branch])
        output = stdout + "\n" + stderr
        return (code == 0, output.strip())

    def fetch(self, remote: str = "origin") -> Tuple[bool, str]:
        """Fetch remote changes."""
        code, stdout, stderr = self._run_git(["fetch", remote])
        return (code == 0, stdout if code == 0 else stderr)

    def get_commit_history(self, limit: int = 30) -> List[Dict[str, str]]:
        """
        Get list of recent commits with metadata.
        Returns list of dicts: hash, short_hash, author, date, message.
        """
        format_str = "%H|%h|%an|%ad|%s"
        code, stdout, _ = self._run_git(["log", f"-n{limit}", f"--pretty=format:{format_str}", "--date=short"])
        commits = []
        if code == 0 and stdout:
            for line in stdout.splitlines():
                parts = line.split("|", 4)
                if len(parts) == 5:
                    commits.append({
                        "hash": parts[0],
                        "short_hash": parts[1],
                        "author": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })
        return commits

    def revert_commit(self, commit_hash: str) -> Tuple[bool, str]:
        """
        Revert a specific commit by creating a new inverse commit (Soft Undo).
        """
        code, stdout, stderr = self._run_git(["revert", "--no-edit", commit_hash])
        output = stdout + "\n" + stderr
        return (code == 0, output.strip())

    def reset_to_commit(self, commit_hash: str, mode: str = "soft") -> Tuple[bool, str]:
        """
        Reset repository to target commit.
        Modes: 'soft' (keep working dir & index), 'mixed' (keep working dir), 'hard' (discard all changes).
        """
        flag = f"--{mode}"
        code, stdout, stderr = self._run_git(["reset", flag, commit_hash])
        output = stdout + "\n" + stderr
        return (code == 0, output.strip())

    def clone_repo(self, repo_url: str, target_dir: str) -> Tuple[bool, str]:
        """Clone a remote repository into target_dir."""
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            process = subprocess.Popen(
                ["git", "clone", repo_url, target_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=creation_flags
            )
            stdout, stderr = process.communicate()
            output = stdout + "\n" + stderr
            return (process.returncode == 0, output.strip())
        except Exception as e:
            return False, str(e)

    def get_remotes(self) -> Dict[str, str]:
        """Get dict of remote names and URLs."""
        code, stdout, _ = self._run_git(["remote", "-v"])
        remotes = {}
        if code == 0 and stdout:
            for line in stdout.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    remotes[parts[0]] = parts[1]
        return remotes

    def set_remote_url(self, remote_name: str, url: str) -> Tuple[bool, str]:
        """Set or add remote repository URL."""
        remotes = self.get_remotes()
        if remote_name in remotes:
            code, stdout, stderr = self._run_git(["remote", "set-url", remote_name, url])
        else:
            code, stdout, stderr = self._run_git(["remote", "add", remote_name, url])
        return (code == 0, stdout if code == 0 else stderr)

    def stash_save(self, message: str = "Stashed by Easy Push") -> Tuple[bool, str]:
        """Save current uncommitted changes to stash."""
        code, stdout, stderr = self._run_git(["stash", "push", "-m", message])
        output = stdout + "\n" + stderr
        return (code == 0, output.strip())

    def stash_pop(self) -> Tuple[bool, str]:
        """Pop the latest stashed changes."""
        code, stdout, stderr = self._run_git(["stash", "pop"])
        output = stdout + "\n" + stderr
        return (code == 0, output.strip())

    def get_stashes(self) -> List[str]:
        """List current stashes."""
        code, stdout, _ = self._run_git(["stash", "list"])
        if code == 0 and stdout:
            return stdout.splitlines()
        return []

    def create_tag(self, tag_name: str, message: str = "") -> Tuple[bool, str]:
        """Create a annotated or lightweight git tag."""
        if message:
            code, stdout, stderr = self._run_git(["tag", "-a", tag_name, "-m", message])
        else:
            code, stdout, stderr = self._run_git(["tag", tag_name])
        return (code == 0, stdout if code == 0 else stderr)

    def push_tags(self, remote: str = "origin") -> Tuple[bool, str]:
        """Push tags to remote repository."""
        code, stdout, stderr = self._run_git(["push", remote, "--tags"])
        output = stdout + "\n" + stderr
        return (code == 0, output.strip())

    def get_latest_version_tag(self) -> str:
        """Find the latest semver tag (e.g. v1.0.2). Returns 'v0.0.0' if none found."""
        code, stdout, _ = self._run_git(["tag", "-l"])
        if code == 0 and stdout:
            tags = stdout.splitlines()
            semver_regex = re.compile(r'^v?(\d+)\.(\d+)\.(\d+)$')
            versions = []
            for t in tags:
                match = semver_regex.match(t.strip())
                if match:
                    versions.append((int(match.group(1)), int(match.group(2)), int(match.group(3)), t.strip()))
            if versions:
                versions.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
                return versions[0][3]
        return "v0.0.0"

    def bump_version(self, current_version: str, bump_type: str = "patch") -> str:
        """Bump semver version string (patch, minor, major)."""
        match = re.match(r'^(v?)(\d+)\.(\d+)\.(\d+)$', current_version.strip())
        prefix = "v"
        if match:
            prefix = match.group(1) or "v"
            major, minor, patch = int(match.group(2)), int(match.group(3)), int(match.group(4))
        else:
            major, minor, patch = 0, 0, 0

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        return f"{prefix}{major}.{minor}.{patch}"
