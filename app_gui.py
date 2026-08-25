import os
import sys
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
from typing import Optional

from git_manager import GitManager
from auto_committer import AutoCommitter
from github_api import GitHubAPI
from repo_analyzer import RepoAnalyzer
import gitignore_templates

class FluidProgressBar(tk.Canvas):
    """Custom animated fluid green progress bar with percentage readout and glowing tip."""
    def __init__(self, parent, width=580, height=24, bg="#07090E", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=1, highlightbackground="#334155", **kwargs)
        self.curr_val = 5.0
        self.target_val = 5.0
        self._animate()

    def set_value(self, val: float):
        self.target_val = min(100.0, max(0.0, float(val)))

    def _animate(self):
        try:
            if not self.winfo_exists():
                return
            if abs(self.curr_val - self.target_val) > 0.4:
                self.curr_val += (self.target_val - self.curr_val) * 0.25
            else:
                self.curr_val = self.target_val

            self.delete("all")
            w = self.winfo_width() or 580
            h = self.winfo_height() or 24

            fill_w = (self.curr_val / 100.0) * w
            if fill_w > 0:
                # Fluid emerald green fill
                self.create_rectangle(0, 0, fill_w, h, fill="#10B981", outline="")
                # Glowing cyan-emerald leading tip
                tip_w = min(18, fill_w)
                self.create_rectangle(fill_w - tip_w, 0, fill_w, h, fill="#34D399", outline="")

            # Centered Percentage Readout
            pct_text = f"{int(self.curr_val)}%"
            text_col = "#000000" if self.curr_val > 45 else "#F8FAFC"
            self.create_text(w / 2, h / 2, text=pct_text, fill=text_col, font=("Segoe UI", 9, "bold"))

            self.after(30, self._animate)
        except Exception:
            pass


class EasyPushGUI(tk.Tk):
    """Ultra-Dark Developer Desktop Application for GitHub Easy Push."""

    # Developer OLED Dark Color Palette
    BG_DARK = "#11111B"       # Deepest OLED Dark
    BG_CARD = "#181825"       # Rich Card Base
    BG_CARD_ALT = "#1E1E2E"   # Input & Elevated Cards
    BORDER_COLOR = "#313244"  # Sleek Border Highlight
    
    TEXT_MAIN = "#CDD6F4"     # Crisp White-Blue Text
    TEXT_MUTED = "#7F849C"    # Muted Gray
    
    ACCENT_BLUE = "#89B4FA"   # Electric Blue
    ACCENT_CYAN = "#89DCEB"   # Cyan Glow
    ACCENT_GREEN = "#A6E3A1"  # Mint Green
    ACCENT_RED = "#F38BA8"    # Soft Crimson
    ACCENT_ORANGE = "#FAB387" # Amber Orange
    ACCENT_PURPLE = "#CBA6F7" # Deep Lavender

    FONT_FAMILY = "Segoe UI"

    def __init__(self):
        super().__init__()
        self.title("GitHub Easy Push - Developer Workstation Engine")
        
        # Window geometry & centering
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = 1140 if sw > 1180 else sw - 40
        h = 770 if sh > 820 else sh - 60
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(980, 680)
        self.configure(bg=self.BG_DARK)

        # Set Window Icon
        self._load_window_icon()

        # Core Engines
        self.git_mgr = GitManager(os.getcwd())
        self.auto_committer = AutoCommitter(self.git_mgr)
        self.github_api = GitHubAPI()
        self.analyzer = RepoAnalyzer(self.git_mgr)

        # Application State
        self.current_repo_path = tk.StringVar(value=os.getcwd())
        self.pat_token = tk.StringVar(value="")

        self._configure_styles()
        self._build_ui()

        # Initial refresh and self analysis
        self.after(200, self.refresh_repo_status)

    def _load_window_icon(self):
        """Set native window icon if available."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            png_path = os.path.join(base_dir, "icon.png")

            if os.path.exists(png_path):
                img = tk.PhotoImage(file=png_path)
                self.iconphoto(True, img)
        except Exception:
            pass

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure(".", background=self.BG_DARK, foreground=self.TEXT_MAIN, font=(self.FONT_FAMILY, 10))
        style.configure("TFrame", background=self.BG_DARK)
        style.configure("Card.TFrame", background=self.BG_CARD, relief="flat", borderwidth=0)
        
        style.configure("TLabel", background=self.BG_DARK, foreground=self.TEXT_MAIN, font=(self.FONT_FAMILY, 10))
        style.configure("Card.TLabel", background=self.BG_CARD, foreground=self.TEXT_MAIN, font=(self.FONT_FAMILY, 10))
        style.configure("Header.TLabel", background=self.BG_CARD, foreground=self.ACCENT_CYAN, font=(self.FONT_FAMILY, 14, "bold"))
        style.configure("Title.TLabel", background=self.BG_DARK, foreground=self.ACCENT_BLUE, font=(self.FONT_FAMILY, 16, "bold"))
        style.configure("Status.TLabel", background=self.BG_CARD, foreground=self.ACCENT_GREEN, font=(self.FONT_FAMILY, 11, "bold"))

        # Notebook tabs styling
        style.configure("TNotebook", background=self.BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.BG_CARD, foreground=self.TEXT_MUTED, font=(self.FONT_FAMILY, 10, "bold"), padding=[14, 8])
        style.map("TNotebook.Tab", background=[("selected", self.BG_CARD_ALT)], foreground=[("selected", self.ACCENT_CYAN)])

        # Treeview styling
        style.configure("Treeview", background=self.BG_CARD, foreground=self.TEXT_MAIN, fieldbackground=self.BG_CARD, rowheight=26, font=(self.FONT_FAMILY, 9))
        style.configure("Treeview.Heading", background=self.BG_CARD_ALT, foreground=self.ACCENT_CYAN, font=(self.FONT_FAMILY, 10, "bold"))
        style.map("Treeview", background=[("selected", self.ACCENT_BLUE)], foreground=[("selected", "#000000")])

    def _build_ui(self):
        # Top Header Bar
        header_frame = tk.Frame(self, bg=self.BG_CARD, height=55, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))

        title_lbl = tk.Label(header_frame, text="⚡ GitHub Easy Push", font=(self.FONT_FAMILY, 16, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN)
        title_lbl.pack(side=tk.LEFT, padx=15, pady=8)

        subtitle_lbl = tk.Label(header_frame, text="Developer Workstation Engine • One-Click Push • Self-Analyzing", font=(self.FONT_FAMILY, 9, "italic"), bg=self.BG_CARD, fg=self.TEXT_MUTED)
        subtitle_lbl.pack(side=tk.LEFT, padx=5, pady=8)

        # Top Bar Repository Picker & Sync Controls
        repo_bar = tk.Frame(self, bg=self.BG_DARK)
        repo_bar.pack(side=tk.TOP, fill=tk.X, padx=15, pady=(5, 10))

        tk.Label(repo_bar, text="Repository Path:", font=(self.FONT_FAMILY, 10, "bold"), bg=self.BG_DARK, fg=self.TEXT_MAIN).pack(side=tk.LEFT, padx=(0, 5))
        
        self.repo_entry = tk.Entry(repo_bar, textvariable=self.current_repo_path, font=(self.FONT_FAMILY, 10), bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN, insertbackground=self.TEXT_MAIN, relief="flat", highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        self.repo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=4)
        self.repo_entry.bind("<Return>", lambda e: self.on_repo_path_change())

        browse_btn = tk.Button(repo_bar, text="📁 Browse", command=self.browse_repo_directory, bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN, activebackground=self.ACCENT_BLUE, relief="flat", font=(self.FONT_FAMILY, 9, "bold"), padx=10)
        browse_btn.pack(side=tk.LEFT, padx=4)

        clone_btn = tk.Button(repo_bar, text="🌐 Clone Repo", command=self.prompt_clone_repo, bg=self.BG_CARD_ALT, fg=self.ACCENT_ORANGE, activebackground=self.ACCENT_ORANGE, relief="flat", font=(self.FONT_FAMILY, 9, "bold"), padx=10)
        clone_btn.pack(side=tk.LEFT, padx=4)

        analyze_btn = tk.Button(repo_bar, text="🔍 Self Analyze", command=self.run_self_analysis, bg=self.ACCENT_PURPLE, fg="#000000", activebackground=self.ACCENT_PURPLE, relief="flat", font=(self.FONT_FAMILY, 9, "bold"), padx=10)
        analyze_btn.pack(side=tk.LEFT, padx=4)

        refresh_btn = tk.Button(repo_bar, text="🔄 Refresh", command=self.refresh_repo_status, bg=self.ACCENT_BLUE, fg="#000000", activebackground=self.ACCENT_BLUE, relief="flat", font=(self.FONT_FAMILY, 9, "bold"), padx=12)
        refresh_btn.pack(side=tk.LEFT, padx=4)

        # Main Notebook Tabbed Interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Create Tabs
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_self_analysis = ttk.Frame(self.notebook)
        self.tab_auto_push = ttk.Frame(self.notebook)
        self.tab_manual_push = ttk.Frame(self.notebook)
        self.tab_undo_history = ttk.Frame(self.notebook)
        self.tab_dev_tools = ttk.Frame(self.notebook)
        self.tab_github_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text="📊 Dashboard")
        self.notebook.add(self.tab_self_analysis, text="🔍 Self Analysis")
        self.notebook.add(self.tab_auto_push, text="🚀 Automatic Push")
        self.notebook.add(self.tab_manual_push, text="✍️ Manual Push & Versioning")
        self.notebook.add(self.tab_undo_history, text="↩️ History & Undo")
        self.notebook.add(self.tab_dev_tools, text="🛠️ Developer Tools")
        self.notebook.add(self.tab_github_settings, text="🔑 GitHub Settings")

        self._build_dashboard_tab()
        self._build_self_analysis_tab()
        self._build_auto_push_tab()
        self._build_manual_push_tab()
        self._build_undo_history_tab()
        self._build_dev_tools_tab()
        self._build_github_settings_tab()

        # Bottom Action Log Console & Clickable Watermark Bar
        bottom_container = tk.Frame(self, bg=self.BG_CARD)
        bottom_container.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(5, 10))

        # Watermark Bar at very bottom
        watermark_bar = tk.Frame(bottom_container, bg=self.BG_CARD_ALT, height=26, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        watermark_bar.pack(side=tk.BOTTOM, fill=tk.X)

        wm_left = tk.Label(
            watermark_bar,
            text="Developed by ",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.BG_CARD_ALT,
            fg=self.TEXT_MUTED
        )
        wm_left.pack(side=tk.LEFT, padx=(15, 0), pady=4)

        # Clickable Author Name Link (WITHOUT raw URL text)
        wm_author_link = tk.Label(
            watermark_bar,
            text="blazecodeprakhar",
            font=(self.FONT_FAMILY, 9, "bold", "underline"),
            bg=self.BG_CARD_ALT,
            fg=self.ACCENT_CYAN,
            cursor="hand2"
        )
        wm_author_link.pack(side=tk.LEFT, padx=0, pady=4)
        wm_author_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/blazecodeprakhar"))

        wm_info = tk.Label(
            watermark_bar,
            text="GitHub Easy Push v1.2 • Developer Edition",
            font=(self.FONT_FAMILY, 8, "italic"),
            bg=self.BG_CARD_ALT,
            fg=self.TEXT_MUTED
        )
        wm_info.pack(side=tk.RIGHT, padx=15, pady=4)

        # Execution Log Console
        log_frame = tk.Frame(bottom_container, bg=self.BG_CARD, height=105)
        log_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        log_hdr = tk.Frame(log_frame, bg=self.BG_CARD)
        log_hdr.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        tk.Label(log_hdr, text="📋 Execution Console Log", font=(self.FONT_FAMILY, 9, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN).pack(side=tk.LEFT)
        tk.Button(log_hdr, text="Clear Console", command=self.clear_log, font=(self.FONT_FAMILY, 8), bg=self.BG_CARD_ALT, fg=self.TEXT_MUTED, relief="flat", padx=6).pack(side=tk.RIGHT)

        self.log_text = tk.Text(log_frame, height=4, font=("Consolas", 9), bg=self.BG_CARD, fg=self.TEXT_MAIN, insertbackground=self.TEXT_MAIN, relief="flat")
        self.log_text.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=2)

    def log(self, message: str):
        """Append log output to console window."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ------------------ DASHBOARD TAB ------------------
    def _build_dashboard_tab(self):
        cards_frame = tk.Frame(self.tab_dashboard, bg=self.BG_DARK)
        cards_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=15)

        # Status Cards Grid
        c1 = tk.Frame(cards_frame, bg=self.BG_CARD, width=230, height=92, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        c1.pack_propagate(False)
        c1.grid(row=0, column=0, padx=8, pady=5)
        tk.Label(c1, text="ACTIVE BRANCH", font=(self.FONT_FAMILY, 9, "bold"), bg=self.BG_CARD, fg=self.TEXT_MUTED).pack(anchor="w", padx=10, pady=(10, 2))
        self.lbl_branch = tk.Label(c1, text="main", font=(self.FONT_FAMILY, 14, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN)
        self.lbl_branch.pack(anchor="w", padx=10)

        c2 = tk.Frame(cards_frame, bg=self.BG_CARD, width=230, height=92, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        c2.pack_propagate(False)
        c2.grid(row=0, column=1, padx=8, pady=5)
        tk.Label(c2, text="PENDING CHANGES", font=(self.FONT_FAMILY, 9, "bold"), bg=self.BG_CARD, fg=self.TEXT_MUTED).pack(anchor="w", padx=10, pady=(10, 2))
        self.lbl_changes_count = tk.Label(c2, text="0 Modified / 0 New", font=(self.FONT_FAMILY, 12, "bold"), bg=self.BG_CARD, fg=self.ACCENT_ORANGE)
        self.lbl_changes_count.pack(anchor="w", padx=10)

        c3 = tk.Frame(cards_frame, bg=self.BG_CARD, width=230, height=92, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        c3.pack_propagate(False)
        c3.grid(row=0, column=2, padx=8, pady=5)
        tk.Label(c3, text="LATEST VERSION TAG", font=(self.FONT_FAMILY, 9, "bold"), bg=self.BG_CARD, fg=self.TEXT_MUTED).pack(anchor="w", padx=10, pady=(10, 2))
        self.lbl_latest_tag = tk.Label(c3, text="v0.0.0", font=(self.FONT_FAMILY, 14, "bold"), bg=self.BG_CARD, fg=self.ACCENT_GREEN)
        self.lbl_latest_tag.pack(anchor="w", padx=10)

        c4 = tk.Frame(cards_frame, bg=self.BG_CARD, width=250, height=92, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        c4.pack_propagate(False)
        c4.grid(row=0, column=3, padx=8, pady=5)
        tk.Label(c4, text="REMOTE GITHUB ORIGIN", font=(self.FONT_FAMILY, 9, "bold"), bg=self.BG_CARD, fg=self.TEXT_MUTED).pack(anchor="w", padx=10, pady=(10, 2))
        self.lbl_remote_url = tk.Label(c4, text="Not Connected", font=(self.FONT_FAMILY, 9), bg=self.BG_CARD, fg=self.TEXT_MAIN, wraplength=230)
        self.lbl_remote_url.pack(anchor="w", padx=10)

        # Quick Actions Frame
        act_frame = tk.Frame(self.tab_dashboard, bg=self.BG_CARD, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        act_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(act_frame, text="⚡ Quick Workstation Actions", font=(self.FONT_FAMILY, 12, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN).pack(anchor="w", padx=15, pady=(15, 10))

        btn_grid = tk.Frame(act_frame, bg=self.BG_CARD)
        btn_grid.pack(anchor="w", padx=15, pady=5)

        tk.Button(btn_grid, text="🚀 One-Click Smart Push", command=self.do_auto_push, bg=self.ACCENT_GREEN, fg="#000000", font=(self.FONT_FAMILY, 10, "bold"), relief="flat", padx=16, pady=8, cursor="hand2").grid(row=0, column=0, padx=6, pady=6)
        tk.Button(btn_grid, text="⬇️ Pull Latest from GitHub", command=self.do_pull, bg=self.BG_CARD_ALT, fg=self.ACCENT_BLUE, font=(self.FONT_FAMILY, 10, "bold"), relief="flat", padx=16, pady=8, cursor="hand2").grid(row=0, column=1, padx=6, pady=6)
        tk.Button(btn_grid, text="🔍 Self-Analyze Repo", command=self.run_self_analysis, bg=self.ACCENT_PURPLE, fg="#000000", font=(self.FONT_FAMILY, 10, "bold"), relief="flat", padx=16, pady=8, cursor="hand2").grid(row=0, column=2, padx=6, pady=6)
        tk.Button(btn_grid, text="📂 Open File Explorer", command=self.open_in_explorer, bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN, font=(self.FONT_FAMILY, 10, "bold"), relief="flat", padx=16, pady=8, cursor="hand2").grid(row=0, column=3, padx=6, pady=6)

        # Remote URL Setter
        remote_setter = tk.Frame(act_frame, bg=self.BG_CARD)
        remote_setter.pack(fill=tk.X, padx=15, pady=15)
        tk.Label(remote_setter, text="Set GitHub Remote Origin URL:", font=(self.FONT_FAMILY, 10, "bold"), bg=self.BG_CARD, fg=self.TEXT_MAIN).pack(side=tk.LEFT, padx=(0, 10))
        self.entry_remote_set = tk.Entry(remote_setter, font=(self.FONT_FAMILY, 10), bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN, insertbackground=self.TEXT_MAIN, relief="flat", highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        self.entry_remote_set.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=3)
        tk.Button(remote_setter, text="Save Origin", command=self.save_remote_url, bg=self.ACCENT_BLUE, fg="#000000", font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=12, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # ------------------ SELF ANALYSIS TAB ------------------
    def _build_self_analysis_tab(self):
        container = tk.Frame(self.tab_self_analysis, bg=self.BG_CARD, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        hdr_frame = tk.Frame(container, bg=self.BG_CARD)
        hdr_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        tk.Label(hdr_frame, text="🔍 Self-Analyzing Engine & Repository Insights", font=(self.FONT_FAMILY, 13, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN).pack(side=tk.LEFT)
        tk.Button(hdr_frame, text="🔄 Run Deep Analysis Now", command=self.run_self_analysis, bg=self.ACCENT_PURPLE, fg="#000000", font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=12, pady=4, cursor="hand2").pack(side=tk.RIGHT)

        # Output text area for analysis findings
        self.analysis_text = tk.Text(container, font=("Consolas", 10), bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN, insertbackground=self.TEXT_MAIN, relief="flat", padx=10, pady=10)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    def run_self_analysis(self):
        path = self.current_repo_path.get()
        self.log(f"Running deep self-analysis on: {path}...")
        
        def run():
            analysis = self.analyzer.analyze_workspace(path)
            
            self.analysis_text.config(state=tk.NORMAL)
            self.analysis_text.delete("1.0", tk.END)

            lines = []
            lines.append("==========================================================================")
            lines.append(" 🔍 GITHUB EASY PUSH - SELF-ANALYSIS REPORT")
            lines.append("==========================================================================")
            lines.append(f" Root Directory Scanned: {analysis['root_dir']}")
            lines.append(f" Total Git Repositories Discovered: {len(analysis['detected_git_repos'])}")
            for r in analysis['detected_git_repos']:
                lines.append(f"   -> {r}")
            lines.append("")

            current_details = analysis.get("current_repo_details", {})
            if analysis["is_valid_git_repo"] and current_details:
                lines.append("--------------------------------------------------------------------------")
                lines.append(" 📌 ACTIVE REPOSITORY DETAILS & COMMIT LINEAGE")
                lines.append("--------------------------------------------------------------------------")
                lines.append(f" Active Branch : {current_details.get('branch')}")
                
                gh_info = current_details.get("github_info")
                if gh_info:
                    lines.append(f" GitHub Owner  : @{gh_info.get('owner')}")
                    lines.append(f" Repository    : {gh_info.get('repo')}")
                    lines.append(f" GitHub URL    : {gh_info.get('web_url')}")
                else:
                    lines.append(" GitHub Info   : Not connected to standard GitHub URL")

                lines.append(f" Local Commits Ahead (Unpushed)  : {current_details.get('unpushed_commits')}")
                lines.append(f" Remote Commits Ahead (Unpulled) : {current_details.get('unpulled_commits')}")
                lines.append("")

                warnings = current_details.get("health_warnings", [])
                if warnings:
                    lines.append(" 💡 HEALTH RECOMMENDATIONS & WARNINGS:")
                    for w in warnings:
                        lines.append(f"   {w}")
                    lines.append("")

                lines.append(" 🌳 RECENT COMMIT LINEAGE GRAPH (Which commit leads to which):")
                lineage = current_details.get("lineage_graph", [])
                for idx, c in enumerate(lineage[:15]):
                    parents_str = ", ".join([p[:7] for p in c["parents"]]) if c["parents"] else "Root Commit"
                    lines.append(f"   [{c['short_hash']}] -> Parents: [{parents_str}] | {c['date']} | {c['author']}: {c['subject']}")
                lines.append("")

            gitignore_info = analysis.get("gitignore_analysis", {})
            lines.append("--------------------------------------------------------------------------")
            lines.append(" 📄 .GITIGNORE RULES & PROTECTION ANALYSIS")
            lines.append("--------------------------------------------------------------------------")
            if gitignore_info.get("exists"):
                lines.append(f" .gitignore File Found: YES ({gitignore_info.get('rule_count')} rules)")
                lines.append(" Protection Check for Common Files:")
                for pattern, protected in gitignore_info.get("protected_patterns", {}).items():
                    status_symbol = "✅ PROTECTED" if protected else "⚠️ NOT EXPLICITLY IGNORED"
                    lines.append(f"   - {pattern:<15} : {status_symbol}")
            else:
                lines.append(" .gitignore File Found: NO ⚠️ (Use Developer Tools tab to generate one!)")

            lines.append("==========================================================================")

            full_report = "\n".join(lines)
            self.analysis_text.insert(tk.END, full_report)
            self.analysis_text.config(state=tk.DISABLED)

            self.notebook.select(self.tab_self_analysis)
            self.log("Self-analysis complete!")

        threading.Thread(target=run, daemon=True).start()

    # ------------------ AUTOMATIC PUSH TAB ------------------
    def _build_auto_push_tab(self):
        container = tk.Frame(self.tab_auto_push, bg=self.BG_CARD, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        tk.Label(container, text="🚀 One-Click Smart Automatic Push", font=(self.FONT_FAMILY, 14, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN).pack(anchor="w", padx=20, pady=(20, 5))
        tk.Label(container, text="Automatically scans all modified, added, and deleted files, crafts a timestamped summary, updates version, commits and pushes to GitHub.", font=(self.FONT_FAMILY, 10), bg=self.BG_CARD, fg=self.TEXT_MUTED).pack(anchor="w", padx=20, pady=(0, 15))

        opts_frame = tk.Frame(container, bg=self.BG_CARD_ALT, padx=15, pady=15, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        opts_frame.pack(fill=tk.X, padx=20, pady=10)

        self.var_auto_bump = tk.BooleanVar(value=True)
        cb_bump = tk.Checkbutton(opts_frame, text="Auto-bump Semantic Version Tag", variable=self.var_auto_bump, font=(self.FONT_FAMILY, 10, "bold"), bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN, selectcolor=self.BG_DARK, activebackground=self.BG_CARD_ALT, activeforeground=self.TEXT_MAIN)
        cb_bump.pack(side=tk.LEFT, padx=10)

        tk.Label(opts_frame, text="Bump Type:", font=(self.FONT_FAMILY, 10), bg=self.BG_CARD_ALT, fg=self.TEXT_MUTED).pack(side=tk.LEFT, padx=(20, 5))
        self.var_auto_bump_type = tk.StringVar(value="patch")
        bump_cb = ttk.Combobox(opts_frame, textvariable=self.var_auto_bump_type, values=["patch", "minor", "major"], state="readonly", width=10)
        bump_cb.pack(side=tk.LEFT, padx=5)

        preview_frame = tk.Frame(container, bg=self.BG_CARD, pady=10)
        preview_frame.pack(fill=tk.X, padx=20)
        tk.Label(preview_frame, text="Generated Commit Message Preview:", font=(self.FONT_FAMILY, 10, "bold"), bg=self.BG_CARD, fg=self.TEXT_MAIN).pack(anchor="w", pady=(5, 5))
        self.lbl_auto_msg_preview = tk.Label(preview_frame, text="[Auto-Update v1.0.1] Updated files...", font=("Consolas", 10, "italic"), bg=self.BG_CARD_ALT, fg=self.ACCENT_GREEN, anchor="w", padx=10, pady=8, relief="flat", wraplength=800)
        self.lbl_auto_msg_preview.pack(fill=tk.X)

        btn_auto = tk.Button(container, text="⚡ AUTO COMMIT & PUSH TO GITHUB", command=self.do_auto_push, bg=self.ACCENT_GREEN, fg="#000000", font=(self.FONT_FAMILY, 13, "bold"), relief="flat", padx=30, pady=15, cursor="hand2")
        btn_auto.pack(pady=25)

    # ------------------ MANUAL PUSH TAB ------------------
    def _build_manual_push_tab(self):
        top_frame = tk.Frame(self.tab_manual_push, bg=self.BG_CARD, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        left_col = tk.Frame(top_frame, bg=self.BG_CARD, width=420)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 10), pady=15)

        tk.Label(left_col, text="📂 Changed Files (Stage / Unstage)", font=(self.FONT_FAMILY, 11, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN).pack(anchor="w", pady=(0, 5))

        tree_scroll = ttk.Scrollbar(left_col)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_tree = ttk.Treeview(left_col, columns=("State", "File", "Status"), show="headings", yscrollcommand=tree_scroll.set, height=12)
        tree_scroll.config(command=self.file_tree.yview)
        
        self.file_tree.heading("State", text="Staged")
        self.file_tree.heading("File", text="File Path")
        self.file_tree.heading("Status", text="Status")

        self.file_tree.column("State", width=70, anchor="center")
        self.file_tree.column("File", width=240, anchor="w")
        self.file_tree.column("Status", width=90, anchor="center")
        self.file_tree.pack(fill=tk.BOTH, expand=True)

        stage_btns = tk.Frame(left_col, bg=self.BG_CARD)
        stage_btns.pack(fill=tk.X, pady=8)
        tk.Button(stage_btns, text="✅ Stage All", command=self.do_stage_all, bg=self.BG_CARD_ALT, fg=self.ACCENT_GREEN, font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT, padx=4)
        tk.Button(stage_btns, text="❌ Unstage All", command=self.do_unstage_all, bg=self.BG_CARD_ALT, fg=self.ACCENT_RED, font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT, padx=4)
        tk.Button(stage_btns, text="Toggle Selected", command=self.toggle_selected_file_stage, bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN, font=(self.FONT_FAMILY, 9), relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT, padx=4)

        right_col = tk.Frame(top_frame, bg=self.BG_CARD)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 15), pady=15)

        tk.Label(right_col, text="✍️ Commit & Version Details", font=(self.FONT_FAMILY, 11, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN).pack(anchor="w", pady=(0, 5))

        tk.Label(right_col, text="Commit Title:", font=(self.FONT_FAMILY, 10, "bold"), bg=self.BG_CARD, fg=self.TEXT_MAIN).pack(anchor="w", pady=(5, 2))
        self.entry_commit_msg = tk.Entry(right_col, font=(self.FONT_FAMILY, 10), bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN, insertbackground=self.TEXT_MAIN, relief="flat", highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        self.entry_commit_msg.pack(fill=tk.X, ipady=4, pady=(0, 10))

        tk.Label(right_col, text="Version Bump Option:", font=(self.FONT_FAMILY, 10, "bold"), bg=self.BG_CARD, fg=self.TEXT_MAIN).pack(anchor="w", pady=(5, 2))
        ver_frame = tk.Frame(right_col, bg=self.BG_CARD)
        ver_frame.pack(fill=tk.X, pady=(0, 10))

        self.var_manual_bump = tk.StringVar(value="none")
        r_none = tk.Radiobutton(ver_frame, text="No Bump", value="none", variable=self.var_manual_bump, bg=self.BG_CARD, fg=self.TEXT_MAIN, selectcolor=self.BG_DARK, activebackground=self.BG_CARD, activeforeground=self.TEXT_MAIN)
        r_patch = tk.Radiobutton(ver_frame, text="Patch (+0.0.1)", value="patch", variable=self.var_manual_bump, bg=self.BG_CARD, fg=self.TEXT_MAIN, selectcolor=self.BG_DARK, activebackground=self.BG_CARD, activeforeground=self.TEXT_MAIN)
        r_minor = tk.Radiobutton(ver_frame, text="Minor (+0.1.0)", value="minor", variable=self.var_manual_bump, bg=self.BG_CARD, fg=self.TEXT_MAIN, selectcolor=self.BG_DARK, activebackground=self.BG_CARD, activeforeground=self.TEXT_MAIN)
        r_major = tk.Radiobutton(ver_frame, text="Major (+1.0.0)", value="major", variable=self.var_manual_bump, bg=self.BG_CARD, fg=self.TEXT_MAIN, selectcolor=self.BG_DARK, activebackground=self.BG_CARD, activeforeground=self.TEXT_MAIN)

        r_none.pack(side=tk.LEFT, padx=5)
        r_patch.pack(side=tk.LEFT, padx=5)
        r_minor.pack(side=tk.LEFT, padx=5)
        r_major.pack(side=tk.LEFT, padx=5)

        self.var_push_after_commit = tk.BooleanVar(value=True)
        cb_push = tk.Checkbutton(right_col, text="Push to Remote GitHub after commit", variable=self.var_push_after_commit, font=(self.FONT_FAMILY, 10, "bold"), bg=self.BG_CARD, fg=self.ACCENT_GREEN, selectcolor=self.BG_DARK, activebackground=self.BG_CARD, activeforeground=self.ACCENT_GREEN)
        cb_push.pack(anchor="w", pady=10)

        btn_manual_commit = tk.Button(right_col, text="🚀 COMMIT & PUSH NOW", command=self.do_manual_commit_push, bg=self.ACCENT_BLUE, fg="#000000", font=(self.FONT_FAMILY, 11, "bold"), relief="flat", padx=20, pady=10, cursor="hand2")
        btn_manual_commit.pack(anchor="w", pady=15)

    # ------------------ HISTORY & UNDO TAB ------------------
    def _build_undo_history_tab(self):
        container = tk.Frame(self.tab_undo_history, bg=self.BG_CARD, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        hdr_frame = tk.Frame(container, bg=self.BG_CARD)
        hdr_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        tk.Label(hdr_frame, text="↩️ Repository History & Commit Undo Engine", font=(self.FONT_FAMILY, 12, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN).pack(side=tk.LEFT)

        tree_scroll = ttk.Scrollbar(container)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15))

        self.history_tree = ttk.Treeview(container, columns=("Hash", "Author", "Date", "Message"), show="headings", yscrollcommand=tree_scroll.set, height=12)
        tree_scroll.config(command=self.history_tree.yview)

        self.history_tree.heading("Hash", text="Short Hash")
        self.history_tree.heading("Author", text="Author")
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("Message", text="Commit Message")

        self.history_tree.column("Hash", width=90, anchor="center")
        self.history_tree.column("Author", width=130, anchor="w")
        self.history_tree.column("Date", width=100, anchor="center")
        self.history_tree.column("Message", width=450, anchor="w")

        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=(15, 0))

        undo_bar = tk.Frame(container, bg=self.BG_CARD_ALT, padx=10, pady=10, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        undo_bar.pack(fill=tk.X, padx=15, pady=15)

        tk.Button(undo_bar, text="🔄 Soft Revert Selected Commit (Safe)", command=self.do_soft_undo_selected, bg=self.ACCENT_GREEN, fg="#000000", font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=12, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(undo_bar, text="⚠️ Hard Reset to Selected Commit", command=self.do_hard_reset_selected, bg=self.ACCENT_RED, fg="#FFFFFF", font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=12, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(undo_bar, text="🌐 Paste Target Commit Hash / Reset", command=self.prompt_paste_commit_reset, bg=self.ACCENT_ORANGE, fg="#000000", font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=12, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # ------------------ DEVELOPER TOOLS TAB ------------------
    def _build_dev_tools_tab(self):
        container = tk.Frame(self.tab_dev_tools, bg=self.BG_CARD, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        b_frame = tk.Frame(container, bg=self.BG_CARD_ALT, padx=15, pady=15, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        b_frame.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(b_frame, text="🌿 Branch Manager", font=(self.FONT_FAMILY, 11, "bold"), bg=self.BG_CARD_ALT, fg=self.ACCENT_CYAN).pack(anchor="w", pady=(0, 8))

        b_controls = tk.Frame(b_frame, bg=self.BG_CARD_ALT)
        b_controls.pack(fill=tk.X)

        tk.Label(b_controls, text="Switch Branch:", font=(self.FONT_FAMILY, 10), bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN).pack(side=tk.LEFT, padx=(0, 5))
        self.cb_branches = ttk.Combobox(b_controls, state="readonly", width=20)
        self.cb_branches.pack(side=tk.LEFT, padx=5)

        tk.Button(b_controls, text="Switch", command=self.do_switch_branch, bg=self.ACCENT_BLUE, fg="#000000", font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(b_controls, text="➕ Create Branch", command=self.prompt_create_branch, bg=self.ACCENT_GREEN, fg="#000000", font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(b_controls, text="🗑️ Delete Branch", command=self.prompt_delete_branch, bg=self.ACCENT_RED, fg="#FFFFFF", font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT, padx=5)

        s_frame = tk.Frame(container, bg=self.BG_CARD_ALT, padx=15, pady=15, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        s_frame.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(s_frame, text="📦 Stash Manager", font=(self.FONT_FAMILY, 11, "bold"), bg=self.BG_CARD_ALT, fg=self.ACCENT_CYAN).pack(anchor="w", pady=(0, 8))

        s_controls = tk.Frame(s_frame, bg=self.BG_CARD_ALT)
        s_controls.pack(fill=tk.X)

        tk.Button(s_controls, text="📥 Stash Current Changes", command=self.do_stash_save, bg=self.BG_CARD, fg=self.TEXT_MAIN, font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=12, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(s_controls, text="📤 Pop Latest Stash", command=self.do_stash_pop, bg=self.BG_CARD, fg=self.ACCENT_GREEN, font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=12, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)

        g_frame = tk.Frame(container, bg=self.BG_CARD_ALT, padx=15, pady=15, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        g_frame.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(g_frame, text="📄 .gitignore Template Generator", font=(self.FONT_FAMILY, 11, "bold"), bg=self.BG_CARD_ALT, fg=self.ACCENT_CYAN).pack(anchor="w", pady=(0, 8))

        g_controls = tk.Frame(g_frame, bg=self.BG_CARD_ALT)
        g_controls.pack(fill=tk.X)

        tk.Label(g_controls, text="Select Tech Stack:", font=(self.FONT_FAMILY, 10), bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN).pack(side=tk.LEFT, padx=(0, 5))
        self.cb_gitignore = ttk.Combobox(g_controls, values=list(gitignore_templates.TEMPLATES.keys()), state="readonly", width=22)
        self.cb_gitignore.set("Python")
        self.cb_gitignore.pack(side=tk.LEFT, padx=5)

        tk.Button(g_controls, text="Generate .gitignore", command=self.do_generate_gitignore, bg=self.ACCENT_PURPLE, fg="#000000", font=(self.FONT_FAMILY, 9, "bold"), relief="flat", padx=12, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # ------------------ GITHUB SETTINGS TAB ------------------
    def _build_github_settings_tab(self):
        container = tk.Frame(self.tab_github_settings, bg=self.BG_CARD, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        tk.Label(container, text="🔑 GitHub Credentials & Authentication", font=(self.FONT_FAMILY, 13, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN).pack(anchor="w", pady=(20, 10), padx=20)
        tk.Label(container, text="Enter a GitHub Personal Access Token (PAT) with 'repo' scope to enable automated GitHub API features (Repo Info, Releases).", font=(self.FONT_FAMILY, 9), bg=self.BG_CARD, fg=self.TEXT_MUTED).pack(anchor="w", pady=(0, 15), padx=20)

        pat_frame = tk.Frame(container, bg=self.BG_CARD_ALT, padx=15, pady=15, highlightthickness=1, highlightbackground=self.BORDER_COLOR)
        pat_frame.pack(fill=tk.X, pady=10, padx=20)

        tk.Label(pat_frame, text="Personal Access Token:", font=(self.FONT_FAMILY, 10, "bold"), bg=self.BG_CARD_ALT, fg=self.TEXT_MAIN).pack(anchor="w", pady=(0, 5))
        self.entry_pat = tk.Entry(pat_frame, textvariable=self.pat_token, font=("Consolas", 10), bg=self.BG_CARD, fg=self.TEXT_MAIN, insertbackground=self.TEXT_MAIN, show="*", relief="flat")
        self.entry_pat.pack(fill=tk.X, ipady=4, pady=(0, 10))

        btn_test_pat = tk.Button(pat_frame, text="🔍 Test GitHub Connection", command=self.do_test_github_connection, bg=self.ACCENT_BLUE, fg="#000000", font=(self.FONT_FAMILY, 10, "bold"), relief="flat", padx=15, pady=6, cursor="hand2")
        btn_test_pat.pack(anchor="w")

        self.lbl_pat_status = tk.Label(container, text="Status: Not tested", font=(self.FONT_FAMILY, 10, "bold"), bg=self.BG_CARD, fg=self.TEXT_MUTED)
        self.lbl_pat_status.pack(anchor="w", pady=15, padx=20)

    # ------------------ EVENT HANDLERS & LOGIC ------------------

    def on_repo_path_change(self):
        new_path = self.current_repo_path.get().strip()
        if self.git_mgr.set_repo_path(new_path):
            self.log(f"Switched working repository to: {new_path}")
            self.refresh_repo_status()
        else:
            messagebox.showerror("Invalid Path", f"Directory does not exist: {new_path}")

    def browse_repo_directory(self):
        d = filedialog.askdirectory(title="Select Local Repository Directory", initialdir=self.current_repo_path.get())
        if d:
            self.current_repo_path.set(d)
            self.on_repo_path_change()

    def prompt_clone_repo(self):
        url = simpledialog.askstring("Clone Remote Repository", "Enter remote GitHub repository URL (https://...):")
        if not url:
            return
        target_dir = filedialog.askdirectory(title="Select Destination Directory")
        if not target_dir:
            return
        
        self.log(f"Cloning {url} into {target_dir}...")
        
        def run_clone():
            success, output = self.git_mgr.clone_repo(url, target_dir)
            self.log(output)
            if success:
                self.current_repo_path.set(target_dir)
                self.on_repo_path_change()
                messagebox.showinfo("Clone Complete", f"Repository cloned successfully into:\n{target_dir}")
            else:
                messagebox.showerror("Clone Failed", f"Failed to clone repository:\n{output}")

        threading.Thread(target=run_clone, daemon=True).start()

    def refresh_repo_status(self):
        path = self.current_repo_path.get()
        if not self.git_mgr.set_repo_path(path):
            self.lbl_branch.config(text="Invalid Path", fg=self.ACCENT_RED)
            return

        is_repo = self.git_mgr.is_git_repo()
        if not is_repo:
            self.lbl_branch.config(text="Not a Git Repo", fg=self.ACCENT_RED)
            self.lbl_changes_count.config(text="N/A")
            self.lbl_remote_url.config(text="None")
            self.lbl_latest_tag.config(text="None")
            return

        branch = self.git_mgr.get_current_branch()
        self.lbl_branch.config(text=branch, fg=self.ACCENT_CYAN)

        status = self.git_mgr.get_status()
        staged = status["staged"]
        unstaged = status["unstaged"]
        untracked = status["untracked"]

        total_changes = len(staged) + len(unstaged) + len(untracked)
        self.lbl_changes_count.config(text=f"{len(unstaged)+len(staged)} Modified / {len(untracked)} New", fg=self.ACCENT_ORANGE if total_changes > 0 else self.ACCENT_GREEN)

        tag = self.git_mgr.get_latest_version_tag()
        self.lbl_latest_tag.config(text=tag)

        remotes = self.git_mgr.get_remotes()
        origin_url = remotes.get("origin", "No remote 'origin' configured")
        self.lbl_remote_url.config(text=origin_url)
        self.entry_remote_set.delete(0, tk.END)
        self.entry_remote_set.insert(0, origin_url if "http" in origin_url or "git@" in origin_url else "")

        smart_msg = self.auto_committer.generate_smart_message(auto_version_bump=self.var_auto_bump.get(), bump_type=self.var_auto_bump_type.get())
        self.lbl_auto_msg_preview.config(text=smart_msg)

        self._populate_file_tree(staged, unstaged, untracked)
        self._populate_history_tree()

        local_branches, _ = self.git_mgr.get_branches()
        self.cb_branches["values"] = local_branches
        if branch in local_branches:
            self.cb_branches.set(branch)

    def _populate_file_tree(self, staged, unstaged, untracked):
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        for s in staged:
            self.file_tree.insert("", tk.END, values=("✅ Yes", s["file"], s["status"]))
        for u in unstaged:
            self.file_tree.insert("", tk.END, values=("❌ No", u["file"], u["status"]))
        for ut in untracked:
            self.file_tree.insert("", tk.END, values=("❌ No", ut["file"], "Untracked"))

    def _populate_history_tree(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        commits = self.git_mgr.get_commit_history(limit=30)
        for c in commits:
            self.history_tree.insert("", tk.END, values=(c["short_hash"], c["author"], c["date"], c["message"]), tags=(c["hash"],))

    def save_remote_url(self):
        url = self.entry_remote_set.get().strip()
        if not url:
            messagebox.showerror("Error", "Remote URL cannot be empty.")
            return

        # Smart Auto-Init: If folder is not a Git repo yet, offer to init Git automatically!
        if not self.git_mgr.is_git_repo():
            if messagebox.askyesno("Initialize Git Repo", "This folder is not initialized as a Git repository yet.\n\nWould you like GitHub Easy Push to initialize a Git repository here now and connect it to your GitHub link?"):
                ok, init_msg = self.git_mgr.init_repo()
                self.log(init_msg)
                if not ok:
                    messagebox.showerror("Error", f"Failed to initialize Git repository:\n{init_msg}")
                    return

        success, msg = self.git_mgr.set_remote_url("origin", url)
        self.log(msg)
        if success:
            messagebox.showinfo("Success", f"Remote 'origin' set to:\n{url}")
            self.refresh_repo_status()
        else:
            messagebox.showerror("Error", f"Failed to set remote URL:\n{msg}")

    def open_in_explorer(self):
        path = self.current_repo_path.get()
        if os.path.exists(path):
            os.startfile(path)

    def do_init_repo(self):
        success, msg = self.git_mgr.init_repo()
        self.log(msg)
        if success:
            messagebox.showinfo("Success", "Initialized empty Git repository.")
            self.refresh_repo_status()
        else:
            messagebox.showerror("Error", f"Failed to init repository:\n{msg}")

    def do_fetch(self):
        def run():
            self.log("Fetching remote repository status...")
            success, msg = self.git_mgr.fetch()
            self.log(msg)
            if success:
                messagebox.showinfo("Fetch Complete", "Fetched remote status.")
            self.refresh_repo_status()

        threading.Thread(target=run, daemon=True).start()

    def do_pull(self):
        def run():
            self.log("Pulling latest changes from GitHub origin...")
            success, msg = self.git_mgr.pull()
            self.log(msg)
            if success:
                messagebox.showinfo("Pull Complete", "Successfully pulled latest changes!")
            else:
                messagebox.showwarning("Pull Notice", f"Pull response:\n{msg}")
            self.refresh_repo_status()

        threading.Thread(target=run, daemon=True).start()

    # Auto Push Execution
    def do_auto_push(self):
        if not self.git_mgr.is_git_repo():
            if messagebox.askyesno("Initialize Git Repo", "This folder is not initialized as a Git repository yet.\n\nWould you like GitHub Easy Push to initialize Git here now and connect it to your remote URL?"):
                ok, msg = self.git_mgr.init_repo()
                self.log(msg)
                if not ok:
                    messagebox.showerror("Error", f"Failed to initialize Git repository:\n{msg}")
                    return
                self.refresh_repo_status()
            else:
                return

        # Launch Live Deployment Progress Modal Window
        self._launch_deployment_modal(
            title="🚀 One-Click Smart Auto-Push",
            execute_fn=self._execute_auto_push_backend
        )

    def _launch_deployment_modal(self, title: str, execute_fn):
        """Creates a sleek live deployment modal with progress bar and real-time Git streaming console."""
        modal = tk.Toplevel(self)
        modal.title("GitHub Easy Push - Live Deployment Engine")
        modal.geometry("640x480")
        modal.configure(bg="#0F172A")
        modal.transient(self)
        modal.grab_set()

        # Center modal
        modal.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 320
        y = self.winfo_y() + (self.winfo_height() // 2) - 240
        modal.geometry(f"640x480+{max(0, x)}+{max(0, y)}")

        # Header Frame
        hdr = tk.Frame(modal, bg="#1E293B", padx=15, pady=12)
        hdr.pack(fill=tk.X, side=tk.TOP)

        lbl_title = tk.Label(hdr, text=title, font=("Segoe UI", 14, "bold"), fg="#22D3EE", bg="#1E293B")
        lbl_title.pack(anchor="w")

        lbl_status = tk.Label(hdr, text="Initializing deployment pipeline...", font=("Segoe UI", 9), fg="#94A3B8", bg="#1E293B")
        lbl_status.pack(anchor="w")

        # Progress Bar Frame
        pframe = tk.Frame(modal, bg="#0F172A", padx=15, pady=10)
        pframe.pack(fill=tk.X)

        pbar = FluidProgressBar(pframe, width=580, height=24)
        pbar.pack(fill=tk.X, pady=5)

        # Log Output Box
        log_frame = tk.Frame(modal, bg="#0F172A", padx=15, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)

        lbl_log = tk.Label(log_frame, text="Live Execution Stream Log:", font=("Segoe UI", 9, "bold"), fg="#F8FAFC", bg="#0F172A")
        lbl_log.pack(anchor="w", pady=(0, 5))

        txt_stream = scrolledtext.ScrolledText(log_frame, bg="#07090E", fg="#38BDF8", font=("Consolas", 9), height=10)
        txt_stream.pack(fill=tk.BOTH, expand=True)

        # Footer Frame
        btn_frame = tk.Frame(modal, bg="#1E293B", pady=10, padx=15)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

        btn_close = tk.Button(btn_frame, text="Deploying...", font=("Segoe UI", 10, "bold"), bg="#334155", fg="#FFFFFF", state=tk.DISABLED, command=modal.destroy, padx=20, pady=5)
        btn_close.pack(side=tk.RIGHT)

        def append_log(line: str, step_status: str = None, progress_val: float = None):
            def update_ui():
                if step_status:
                    lbl_status.config(text=step_status)
                if progress_val is not None:
                    pbar.set_value(progress_val)
                txt_stream.insert(tk.END, line + "\n")
                txt_stream.see(tk.END)
                self.log(line)
            modal.after(0, update_ui)

        def run_thread():
            ok, result_msg = execute_fn(append_log)
            def on_complete():
                if ok:
                    pbar.set_value(100)
                    lbl_status.config(text="✔ Deployment Completed Successfully to GitHub!", fg="#34D399")
                    lbl_title.config(fg="#34D399")
                    btn_close.config(text="✔ Close", bg="#10B981", fg="#000000", state=tk.NORMAL)
                    txt_stream.insert(tk.END, "\n========================================\n[SUCCESS] Pushed changes & tags to GitHub!\n========================================\n")
                else:
                    lbl_status.config(text="⚠ Push Encountered Warning or Error", fg="#FB7185")
                    btn_close.config(text="Close", bg="#EF4444", fg="#FFFFFF", state=tk.NORMAL)
                    txt_stream.insert(tk.END, f"\n[NOTICE] {result_msg}\n")
                txt_stream.see(tk.END)
                self.refresh_repo_status()
            modal.after(0, on_complete)

        threading.Thread(target=run_thread, daemon=True).start()

    def _execute_auto_push_backend(self, append_log_fn):
        """Backend execution logic for Smart Auto-Push with step progress callbacks."""
        append_log_fn("Scanning workspace for file diffs...", step_status="1/4 Staging modified files...", progress_val=15)
        ok, msg = self.git_mgr.stage_all()
        append_log_fn(f"Staging status: {msg if msg else 'All modified files staged.'}")
        if not ok:
            return False, f"Failed to stage files: {msg}"

        append_log_fn("Generating smart commit message...", step_status="2/4 Committing changes...", progress_val=35)
        commit_msg = self.auto_committer.generate_smart_message(
            auto_version_bump=self.var_auto_bump.get(),
            bump_type=self.var_auto_bump_type.get()
        )

        append_log_fn(f"Commit message: '{commit_msg}'")
        ok, msg = self.git_mgr.commit(commit_msg)
        append_log_fn(f"Commit output:\n{msg}")
        if not ok and "nothing to commit" not in msg.lower():
            return False, f"Commit error: {msg}"

        if self.var_auto_bump.get():
            append_log_fn("Creating semantic release tag...", step_status="3/4 Creating version tag...", progress_val=60)
            curr_ver = self.git_mgr.get_latest_version_tag()
            next_ver = self.git_mgr.bump_version(curr_ver, self.var_auto_bump_type.get())
            append_log_fn(f"Tagging release {next_ver}...")
            self.git_mgr.create_tag(next_ver, f"Release {next_ver}")

        append_log_fn("Pushing commits to remote origin on GitHub...", step_status="4/4 Pushing data to GitHub...", progress_val=80)
        ok, msg = self.git_mgr.push(progress_callback=lambda line: append_log_fn(line, progress_val=90))
        append_log_fn(msg)

        if self.var_auto_bump.get():
            append_log_fn("Pushing release tags to remote origin...")
            self.git_mgr.push_tags()

        return ok, msg

    # Manual Push Actions
    def do_stage_all(self):
        ok, msg = self.git_mgr.stage_all()
        self.log(f"Stage all: {msg if msg else 'OK'}")
        self.refresh_repo_status()

    def do_unstage_all(self):
        ok, msg = self.git_mgr.unstage_all()
        self.log(f"Unstage all: {msg if msg else 'OK'}")
        self.refresh_repo_status()

    def toggle_selected_file_stage(self):
        selected = self.file_tree.selection()
        if not selected:
            return
        for sel in selected:
            item = self.file_tree.item(sel)
            staged_val, filepath, _ = item["values"]
            if staged_val == "✅ Yes":
                self.git_mgr.unstage_file(filepath)
            else:
                self.git_mgr.stage_file(filepath)
        self.refresh_repo_status()

    def do_manual_commit_push(self):
        msg = self.entry_commit_msg.get().strip()
        if not msg:
            messagebox.showerror("Error", "Please enter a commit title.")
            return

        def execute_manual_backend(append_log_fn):
            bump_option = self.var_manual_bump.get()
            final_msg = msg
            if bump_option != "none":
                append_log_fn("Creating semantic release tag...", step_status="1/3 Creating version tag...", progress_val=30)
                curr_ver = self.git_mgr.get_latest_version_tag()
                next_ver = self.git_mgr.bump_version(curr_ver, bump_option)
                final_msg = f"[{next_ver}] {msg}"
                self.git_mgr.create_tag(next_ver, f"Release {next_ver}")

            append_log_fn(f"Committing changes: '{final_msg}'...", step_status="2/3 Committing changes...", progress_val=50)
            ok, out = self.git_mgr.commit(final_msg)
            append_log_fn(out)
            if not ok and "nothing to commit" not in out.lower():
                return False, f"Commit error: {out}"

            if self.var_push_after_commit.get():
                append_log_fn("Pushing commits to remote origin on GitHub...", step_status="3/3 Pushing data to GitHub...", progress_val=80)
                pok, pout = self.git_mgr.push(progress_callback=lambda line: append_log_fn(line, progress_val=90))
                append_log_fn(pout)
                if bump_option != "none":
                    append_log_fn("Pushing release tags to remote origin...")
                    self.git_mgr.push_tags()
                return pok, pout

            return True, "Commit complete."

        self._launch_deployment_modal(
            title="🚀 Manual Commit & Push Deployment",
            execute_fn=execute_manual_backend
        )

    # History & Undo Actions
    def do_soft_undo_selected(self):
        sel = self.history_tree.selection()
        if not sel:
            messagebox.showwarning("Select Commit", "Please select a commit from the history list.")
            return
        item = self.history_tree.item(sel[0])
        tags = item.get("tags", [])
        commit_hash = tags[0] if tags else item["values"][0]

        if messagebox.askyesno("Confirm Soft Revert", f"Soft Undo will revert commit {commit_hash} by creating an inverse commit while keeping your working changes.\nProceed?"):
            ok, msg = self.git_mgr.revert_commit(commit_hash)
            self.log(msg)
            if ok:
                messagebox.showinfo("Success", "Soft Undo completed successfully.")
            else:
                messagebox.showerror("Error", f"Revert failed:\n{msg}")
            self.refresh_repo_status()

    def do_hard_reset_selected(self):
        sel = self.history_tree.selection()
        if not sel:
            messagebox.showwarning("Select Commit", "Please select a commit from the history list.")
            return
        item = self.history_tree.item(sel[0])
        tags = item.get("tags", [])
        commit_hash = tags[0] if tags else item["values"][0]

        if messagebox.askyesno("⚠️ DANGER: HARD RESET", f"WARNING: Hard Reset will ROLL BACK your repository strictly to commit:\n{commit_hash}\n\nAll uncommitted changes will be permanently discarded!\nAre you sure?", icon='warning'):
            ok, msg = self.git_mgr.reset_to_commit(commit_hash, mode="hard")
            self.log(msg)
            if ok:
                messagebox.showinfo("Reset Complete", f"Repository state hard-reset to commit {commit_hash}")
            else:
                messagebox.showerror("Error", f"Reset failed:\n{msg}")
            self.refresh_repo_status()

    def prompt_paste_commit_reset(self):
        target = simpledialog.askstring("Rollback / Undo to Commit", "Paste Target Commit Hash or Repository URL:")
        if not target:
            return
        target = target.strip()
        mode = "hard" if messagebox.askyesno("Reset Mode", "Perform HARD RESET to wipe uncommitted changes?\n(Choose 'No' for Soft Reset)") else "soft"
        
        ok, msg = self.git_mgr.reset_to_commit(target, mode=mode)
        self.log(msg)
        if ok:
            messagebox.showinfo("Success", f"Repository state successfully reset to {target}")
        else:
            messagebox.showerror("Error", f"Failed to reset repository:\n{msg}")
        self.refresh_repo_status()

    # Dev Tools Actions
    def do_switch_branch(self):
        branch = self.cb_branches.get()
        if not branch:
            return
        ok, msg = self.git_mgr.switch_branch(branch)
        self.log(msg)
        if ok:
            messagebox.showinfo("Switched Branch", f"Switched to branch: {branch}")
        else:
            messagebox.showerror("Error", f"Failed to switch branch:\n{msg}")
        self.refresh_repo_status()

    def prompt_create_branch(self):
        name = simpledialog.askstring("New Branch", "Enter new branch name:")
        if not name:
            return
        ok, msg = self.git_mgr.create_branch(name.strip(), checkout=True)
        self.log(msg)
        if ok:
            messagebox.showinfo("Success", f"Created and switched to branch: {name}")
        else:
            messagebox.showerror("Error", f"Failed to create branch:\n{msg}")
        self.refresh_repo_status()

    def prompt_delete_branch(self):
        branch = self.cb_branches.get()
        if not branch:
            return
        if messagebox.askyesno("Delete Branch", f"Are you sure you want to delete branch '{branch}'?"):
            ok, msg = self.git_mgr.delete_branch(branch, force=True)
            self.log(msg)
            if ok:
                messagebox.showinfo("Deleted", f"Deleted branch: {branch}")
            else:
                messagebox.showerror("Error", f"Failed to delete branch:\n{msg}")
            self.refresh_repo_status()

    def do_stash_save(self):
        ok, msg = self.git_mgr.stash_save("Stashed from Easy Push App")
        self.log(msg)
        if ok:
            messagebox.showinfo("Stash Saved", "Uncommitted changes saved to Git stash.")
        else:
            messagebox.showerror("Error", f"Failed to stash changes:\n{msg}")
        self.refresh_repo_status()

    def do_stash_pop(self):
        ok, msg = self.git_mgr.stash_pop()
        self.log(msg)
        if ok:
            messagebox.showinfo("Stash Popped", "Latest stashed changes applied back.")
        else:
            messagebox.showerror("Error", f"Failed to pop stash:\n{msg}")
        self.refresh_repo_status()

    def do_generate_gitignore(self):
        stack = self.cb_gitignore.get()
        ok = gitignore_templates.generate_gitignore(self.current_repo_path.get(), stack)
        if ok:
            self.log(f"Generated .gitignore for {stack}")
            messagebox.showinfo("Success", f"Created/Updated .gitignore for '{stack}' stack!")
            self.refresh_repo_status()
        else:
            messagebox.showerror("Error", "Failed to generate .gitignore file.")

    # GitHub Settings
    def do_test_github_connection(self):
        token = self.pat_token.get().strip()
        self.github_api.set_token(token)
        ok, msg, data = self.github_api.test_connection()
        self.log(msg)
        if ok and data:
            user = data.get("login", "")
            self.lbl_pat_status.config(text=f"Status: Connected as @{user}", fg=self.ACCENT_GREEN)
            messagebox.showinfo("GitHub Connected", f"Successfully authenticated with GitHub as:\n{user}")
        else:
            self.lbl_pat_status.config(text=f"Status: {msg}", fg=self.ACCENT_RED)
            messagebox.showerror("Authentication Error", msg)
