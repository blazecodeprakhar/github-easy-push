import datetime
from typing import Dict, List
from git_manager import GitManager

class AutoCommitter:
    """Generates intelligent commit messages based on repository status and file changes."""
    
    def __init__(self, git_mgr: GitManager):
        self.git_mgr = git_mgr

    def generate_smart_message(self, auto_version_bump: bool = True, bump_type: str = "patch") -> str:
        """
        Analyze changed, added, and deleted files to build a rich, structured update commit message.
        Example output:
        [Auto-Update v1.0.3] Modified 2 files (main.py, config.py) | Added 1 file (utils.py) - 2026-08-25 16:30
        """
        status = self.git_mgr.get_status()
        staged = status.get("staged", [])
        unstaged = status.get("unstaged", [])
        untracked = status.get("untracked", [])

        all_changes = staged + unstaged + untracked
        if not all_changes:
            return "Auto-Update: No file changes detected"

        modified = [item["file"] for item in all_changes if item.get("status") == "Modified"]
        added = [item["file"] for item in all_changes if item.get("status") in ["Added", "Untracked"]]
        deleted = [item["file"] for item in all_changes if item.get("status") == "Deleted"]
        renamed = [item["file"] for item in all_changes if item.get("status") == "Renamed"]

        summary_parts = []
        if modified:
            file_sample = ", ".join(modified[:3]) + (f" +{len(modified)-3} more" if len(modified) > 3 else "")
            summary_parts.append(f"Updated {len(modified)} file(s) ({file_sample})")
        if added:
            file_sample = ", ".join(added[:3]) + (f" +{len(added)-3} more" if len(added) > 3 else "")
            summary_parts.append(f"Added {len(added)} file(s) ({file_sample})")
        if deleted:
            file_sample = ", ".join(deleted[:3]) + (f" +{len(deleted)-3} more" if len(deleted) > 3 else "")
            summary_parts.append(f"Deleted {len(deleted)} file(s) ({file_sample})")
        if renamed:
            summary_parts.append(f"Renamed {len(renamed)} file(s)")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        version_prefix = ""
        if auto_version_bump:
            curr_ver = self.git_mgr.get_latest_version_tag()
            next_ver = self.git_mgr.bump_version(curr_ver, bump_type)
            version_prefix = f"[{next_ver}] "
        else:
            version_prefix = "[Auto-Update] "

        detail_str = " | ".join(summary_parts) if summary_parts else "Routine maintenance update"
        return f"{version_prefix}{detail_str} ({timestamp})"
