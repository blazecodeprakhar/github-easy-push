# GitHub Easy Push

<p align="center">
  <img src="assets/icon.png" alt="GitHub Easy Push Icon" width="120" height="120" />
</p>

<p align="center">
  <b>Futuristic Windows Git Workstation & Automated Commit Engine</b><br>
  Developed by <b>Prakhar Yadav (<a href="https://github.com/blazecodeprakhar">@blazecodeprakhar</a>)</b>
</p>

---

## ⚡ Overview

GitHub Easy Push is a desktop software utility designed to automate Git workflows, commit formatting, semantic version tagging, and repository self analysis for Windows developers.

---

## 📸 Real Software Interface Screenshots

### 1. Main Dashboard & Workstation Overview
![GitHub Easy Push Dashboard](assets/images/screenshot_dashboard.png)

### 2. Workspace Self Analysis Engine
![Self Analysis Engine](assets/images/screenshot_self_analysis.png)

### 3. One Click Smart Automatic Push
![Automatic Push Engine](assets/images/screenshot_auto_push.png)

### 4. Selective Manual Push & Versioning Bumper
![Manual Push Engine](assets/images/screenshot_manual_push.png)

### 5. Commit History Timeline & Soft Undo Engine
![Commit History and Undo](assets/images/screenshot_history_undo.png)

### 6. Developer Power Tools & .gitignore Generator
![Developer Tools](assets/images/screenshot_dev_tools.png)

---

## 🌟 Key Features

* **One Click Smart Auto Push**: Automatically scans file diffs, generates timestamped update notes, stages files, tags versions, and pushes to remote GitHub origins in 1 click.
* **Commit Undo Engine**: Perform Soft Revert (creates inverse commit while keeping local edits) or Hard Reset (restores repository state strictly back to target commit hash).
* **Self Analyzing Engine**: Deeply inspects Git repositories, commit parent lineage graphs, .gitignore rule protection for sensitive files, and sync health.
* **Semantic Version Bumper**: Automatic calculation and tagging for Patch (+0.0.1), Minor (+0.1.0), and Major (+1.0.0) releases.
* **Portable Windows Executable**: Single standalone `.exe` binary that runs anywhere on Windows without Python installation.

---

## 🚀 Quick Start Guide

### Direct Executable Execution
Download `GitHub_Easy_Push.exe` and double click to run instantly on Windows 10 or 11.

### Running from Source Code
```bash
git clone https://github.com/blazecodeprakhar/github-easy-push.git
cd github-easy-push
pip install -r requirements.txt
python main.py
```

### Compiling Standalone Binary (.exe)
```bash
python build_exe.py
```

---

## 📁 Repository Directory Structure

```
github-easy-push/
├── assets/
│   ├── icon.png
│   ├── images/          # Real software screenshots
│   ├── docs/            # PDF User Manuals
│   └── downloads/       # Portable ZIP packages
├── GitHub_Easy_Push.exe  # Standalone Windows executable
├── main.py              # Main Python launcher
├── app_gui.py           # Tkinter GUI Workstation Interface
├── git_manager.py       # Subprocess Git CLI Wrapper
├── auto_committer.py    # Auto Commit & Semver Bumper Engine
├── repo_analyzer.py     # Workspace Self Analysis Engine
├── github_api.py        # GitHub PAT Integration
├── gitignore_templates.py
├── build_exe.py         # Single binary PyInstaller builder
├── index.html           # Website Landing Page
├── guide.html           # Step-by-step User Guide Page
├── docs.html            # Documentation Search Query Center
├── styles.css           # Sci-Fi Dark Mode Stylesheet
├── script.js            # Falling Star Particle Engine
├── README.md
└── requirements.txt
```

---

## 👤 Author Profile

* **Developer**: Prakhar Yadav
* **GitHub**: [blazecodeprakhar](https://github.com/blazecodeprakhar)
* **Portfolio**: [blazecodeprakhar.netlify.app](https://blazecodeprakhar.netlify.app)
* **License**: MIT Open Source License
