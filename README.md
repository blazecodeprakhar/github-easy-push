# ⚡ GitHub Easy Push Software

**GitHub Easy Push** is a desktop application written in Python designed to make Git and GitHub workflows effortless. It features smart automatic push operations, granular manual commits with semantic version bumping, deep commit history revert/undo capabilities, self-analyzing repository insights, GitHub API integration, and developer productivity tools.

---

## 🌟 Key Features

1. **🔍 Self-Analyzing Engine & Repository Insights**:
   - Automatically scans the application directory and subfolders to discover `.git` structures.
   - Deeply inspects commit lineage graphs ("which commit leads to which").
   - Analyzes `.gitignore` rules and audits protection for sensitive patterns (`.env`, `node_modules/`, `build/`, `.venv/`).
   - Evaluates sync health (unpushed local commits, unpulled remote commits) and displays actionable recommendations.

2. **Repository Selector & Connection Manager**:
   - Open any local Git repository or clone remote GitHub repositories.
   - Live dashboard cards displaying active branch, staged/unstaged changes, version tags, and remote origin URL.
   - Quick toolbar actions: **Pull**, **Fetch**, **Open in File Explorer**, **Initialize Git Repo**, **Set Remote Origin URL**.

3. **🚀 One-Click Automatic Smart Push**:
   - Auto-detects modified, newly added, and deleted files across your project.
   - Generates structured, timestamped commit messages (e.g. `[Auto-Update v1.0.1] Updated main.py, utils.py | Added 2 files (2026-08-25 16:30)`).
   - Stages changes, bumps version tag, commits, and pushes directly to GitHub in **one click**.

4. **✍️ Manual Push & Version Bumper**:
   - Interactive file staging table with individual file toggle controls.
   - Custom commit title and detailed release notes.
   - **Semantic Versioning Bumper**: Automatically calculates and tags Patch (`v1.0.1`), Minor (`v1.1.0`), or Major (`v2.0.0`) releases.

5. **↩️ History Visualizer & Repository Undo Engine**:
   - Full timeline view of repository commit history (Short Hash, Author, Date, Message).
   - **Soft Undo (Safe Revert)**: Creates a clean inverse commit reverting changes without losing local edits.
   - **Hard Undo / Reset**: Wipes uncommitted changes and resets the entire repository state back to any chosen past commit or pasted commit hash / remote state.

6. **🛠️ Developer Power Tools**:
   - **Branch Manager**: Create, switch, list, or delete branches.
   - **Stash Manager**: Stash pending uncommitted work and pop stashes on demand.
   - **.gitignore Generator**: Instantly generate preconfigured `.gitignore` files for Python, Node.js/React, C/C++, Java, and Go.

7. **🔗 Clickable Watermark**:
   - Sleek UI watermark bar linking directly to **`blazecodeprakhar`**:
     `blazecodeprakhar — https://github.com/blazecodeprakhar`
   - Clicking the link opens the profile page directly in the default web browser.

8. **📦 Windows Executable (.exe) Packager**:
   - Pre-packaged `build_exe.py` script to generate a standalone Windows executable (`GitHub_Easy_Push.exe`).

---

## 🚀 How to Run the Software

### Method 1: Run with Python Directly
```bash
python main.py
```

### Method 2: Build as a Standalone Windows Executable (.exe)
Run the automated build script:
```bash
python build_exe.py
```
This will compile the app into a single executable folder at:
`dist/GitHub_Easy_Push/GitHub_Easy_Push.exe`

---

## 💻 Technical Architecture

- `main.py`: Entry point launcher.
- `app_gui.py`: Dark-themed modern GUI built with Python `tkinter` & `ttk`.
- `repo_analyzer.py`: Self-analyzing engine inspecting Git structures, lineage, and `.gitignore` safety.
- `git_manager.py`: Subprocess wrapper executing native Git CLI commands robustly.
- `auto_committer.py`: Engine for generating structured commit summaries.
- `github_api.py`: Standard library HTTP client for GitHub REST API calls.
- `gitignore_templates.py`: Ready-to-use `.gitignore` templates.
- `build_exe.py`: PyInstaller compilation script.

---

*Created for seamless developer workflows.*
