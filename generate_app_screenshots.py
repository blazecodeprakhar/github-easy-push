import os
from PIL import Image, ImageDraw, ImageFont

def draw_software_screenshot(name, title_tab, content_type):
    width, height = 1100, 680
    img = Image.new('RGB', (width, height), color='#0F172A')
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_bold = ImageFont.truetype("arialbd.ttf", 15)
        font_normal = ImageFont.truetype("arial.ttf", 13)
        font_mono = ImageFont.truetype("consola.ttf", 12)
    except IOError:
        font_title = font_bold = font_normal = font_mono = ImageFont.load_default()

    # Colors
    BG_DARK = '#0B0F19'
    BG_HEADER = '#1E293B'
    ACCENT_CYAN = '#0891B2'
    ACCENT_BLUE = '#2563EB'
    ACCENT_GREEN = '#10B981'
    ACCENT_PURPLE = '#8B5CF6'
    TEXT_WHITE = '#F8FAFC'
    TEXT_MUTED = '#94A3B8'
    BORDER_COLOR = '#334155'

    # Top Header Bar
    draw.rectangle([0, 0, width, 55], fill=BG_HEADER)
    draw.ellipse([15, 18, 35, 38], fill=ACCENT_CYAN)
    draw.text((20, 20), "⚡", fill=TEXT_WHITE, font=font_normal)
    draw.text((45, 16), "GitHub Easy Push", fill=TEXT_WHITE, font=font_title)
    draw.text((240, 20), "Developer Workstation Engine | One Click Push | Self Analyzing", fill=TEXT_MUTED, font=font_normal)

    # Repository Bar
    draw.rectangle([0, 55, width, 105], fill=BG_DARK)
    draw.text((15, 72), "Repository Path:", fill=TEXT_MUTED, font=font_bold)
    draw.rectangle([140, 67, 720, 95], fill='#1E293B', outline=BORDER_COLOR)
    draw.text((150, 72), r"C:\Users\prakh\OneDrive\Desktop\researchs", fill=TEXT_WHITE, font=font_mono)

    # Top Action Buttons
    draw.rectangle([730, 67, 810, 95], fill='#334155')
    draw.text((745, 72), "Browse", fill=TEXT_WHITE, font=font_normal)

    draw.rectangle([820, 67, 920, 95], fill=ACCENT_PURPLE)
    draw.text((830, 72), "Self Analyze", fill=TEXT_WHITE, font=font_bold)

    draw.rectangle([930, 67, 1080, 95], fill=ACCENT_BLUE)
    draw.text((945, 72), "Refresh Status", fill=TEXT_WHITE, font=font_bold)

    # Notebook Tabs Bar
    draw.rectangle([0, 105, width, 145], fill='#1E293B')
    tabs = ["Dashboard", "Self Analysis", "Automatic Push", "Manual Push", "History & Undo", "Developer Tools"]
    x_offset = 15
    for tab in tabs:
        is_active = (tab == title_tab)
        bg = ACCENT_CYAN if is_active else '#334155'
        txt_col = '#000000' if is_active else TEXT_WHITE
        tw = len(tab) * 9 + 20
        draw.rectangle([x_offset, 112, x_offset + tw, 140], fill=bg)
        draw.text((x_offset + 10, 116), tab, fill=txt_col, font=font_bold)
        x_offset += tw + 10

    # Main Tab Content Area
    draw.rectangle([15, 160, width - 15, height - 40], fill='#0F172A', outline=BORDER_COLOR)

    if content_type == "dashboard":
        # Status Cards Grid
        card_w = 250
        draw.rectangle([30, 180, 30 + card_w, 260], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((40, 190), "ACTIVE BRANCH", fill=TEXT_MUTED, font=font_mono)
        draw.text((40, 215), "main", fill=ACCENT_GREEN, font=font_title)

        draw.rectangle([300, 180, 300 + card_w, 260], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((310, 190), "PENDING CHANGES", fill=TEXT_MUTED, font=font_mono)
        draw.text((310, 215), "2 File(s) Modified", fill=ACCENT_CYAN, font=font_title)

        draw.rectangle([570, 180, 570 + card_w, 260], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((580, 190), "LATEST VERSION TAG", fill=TEXT_MUTED, font=font_mono)
        draw.text((580, 215), "v1.2.0", fill=ACCENT_PURPLE, font=font_title)

        draw.rectangle([840, 180, 840 + card_w, 260], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((850, 190), "REMOTE ORIGIN", fill=TEXT_MUTED, font=font_mono)
        draw.text((850, 215), "Connected", fill=ACCENT_GREEN, font=font_title)

        # Quick Actions Box
        draw.rectangle([30, 280, 1070, 480], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((45, 295), "⚡ Quick Workstation Actions", fill=TEXT_WHITE, font=font_title)

        draw.rectangle([45, 335, 300, 385], fill=ACCENT_GREEN)
        draw.text((65, 350), "🚀 One Click Smart Push", fill='#000000', font=font_title)

        draw.rectangle([320, 335, 550, 385], fill=ACCENT_BLUE)
        draw.text((340, 350), "⬇️ Pull Latest Changes", fill=TEXT_WHITE, font=font_title)

        draw.rectangle([570, 335, 800, 385], fill='#334155')
        draw.text((590, 350), "🔍 Self Analyze Repo", fill=TEXT_WHITE, font=font_title)

        # Remote URL setter
        draw.text((45, 415), "Set GitHub Remote Origin URL:", fill=TEXT_MUTED, font=font_bold)
        draw.rectangle([260, 410, 930, 440], fill='#0F172A', outline=BORDER_COLOR)
        draw.text((270, 415), "https://github.com/blazecodeprakhar/github-easy-push.git", fill=ACCENT_CYAN, font=font_mono)
        draw.rectangle([940, 410, 1050, 440], fill=ACCENT_BLUE)
        draw.text((955, 418), "Save Origin", fill=TEXT_WHITE, font=font_bold)

    elif content_type == "self_analysis":
        draw.text((30, 175), "🔍 Repository Self Analysis & Lineage Inspection", fill=TEXT_WHITE, font=font_title)

        # Lineage Box
        draw.rectangle([30, 210, 530, 470], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((45, 225), "Commit Parent Lineage Graph", fill=ACCENT_CYAN, font=font_bold)
        draw.text((45, 255), "• Hash: a1b2c3d | Merge pull request #4 from origin/main", fill=TEXT_WHITE, font=font_mono)
        draw.text((45, 280), "  └── Parent: 9f8e7d6 (Author: Prakhar Yadav)", fill=TEXT_MUTED, font=font_mono)
        draw.text((45, 305), "• Hash: 9f8e7d6 | Fix single portable executable build script", fill=TEXT_WHITE, font=font_mono)
        draw.text((45, 330), "  └── Parent: 5a4b3c2 (Author: Prakhar Yadav)", fill=TEXT_MUTED, font=font_mono)

        # Gitignore Protection Box
        draw.rectangle([550, 210, 1070, 470], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((565, 225), ".gitignore Protection Audit", fill=ACCENT_GREEN, font=font_bold)
        draw.text((565, 255), "[PROTECTED] .env file is safely ignored", fill=ACCENT_GREEN, font=font_mono)
        draw.text((565, 280), "[PROTECTED] node_modules/ directory is safely ignored", fill=ACCENT_GREEN, font=font_mono)
        draw.text((565, 305), "[PROTECTED] __pycache__/ directory is safely ignored", fill=ACCENT_GREEN, font=font_mono)
        draw.text((565, 330), "[PROTECTED] dist/ & build/ binaries are safely ignored", fill=ACCENT_GREEN, font=font_mono)

    elif content_type == "auto_push":
        draw.text((30, 175), "🚀 One Click Smart Automatic Push Engine", fill=TEXT_WHITE, font=font_title)

        draw.rectangle([30, 210, 1070, 470], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((45, 230), "Automatic Version Bump Mode:", fill=TEXT_MUTED, font=font_bold)

        draw.rectangle([45, 260, 200, 290], fill=ACCENT_CYAN)
        draw.text((60, 268), "✔ Patch (+0.0.1)", fill='#000000', font=font_bold)

        draw.rectangle([220, 260, 360, 290], fill='#334155')
        draw.text((235, 268), "Minor (+0.1.0)", fill=TEXT_WHITE, font=font_normal)

        draw.rectangle([380, 260, 520, 290], fill='#334155')
        draw.text((395, 268), "Major (+1.0.0)", fill=TEXT_WHITE, font=font_normal)

        draw.text((45, 320), "Generated Smart Commit Note Preview:", fill=TEXT_MUTED, font=font_bold)
        draw.rectangle([45, 345, 1055, 395], fill='#0B0F19', outline=BORDER_COLOR)
        draw.text((60, 360), "[v1.2.1] Updated 2 file(s) (main.py, app_gui.py) (2026-08-25 16:30)", fill=ACCENT_CYAN, font=font_mono)

        draw.rectangle([45, 415, 400, 455], fill=ACCENT_GREEN)
        draw.text((70, 428), "AUTO COMMIT AND PUSH TO GITHUB", fill='#000000', font=font_title)

    elif content_type == "history_undo":
        draw.text((30, 175), "↩️ Commit History & Undo Engine (Revert / Reset)", fill=TEXT_WHITE, font=font_title)

        draw.rectangle([30, 210, 1070, 470], fill='#1E293B', outline=BORDER_COLOR)

        # History list
        draw.rectangle([45, 230, 750, 450], fill='#0F172A', outline=BORDER_COLOR)
        draw.text((60, 245), "Commit History Timeline", fill=TEXT_MUTED, font=font_bold)
        draw.text((60, 275), "▶ [Selected] a1b2c3d | Fix single portable executable build script (v1.2.0)", fill=ACCENT_CYAN, font=font_mono)
        draw.text((60, 305), "  9f8e7d6 | Add dark theme landing page website & downloads", fill=TEXT_WHITE, font=font_mono)
        draw.text((60, 335), "  5a4b3c2 | Initial release of GitHub Easy Push Workstation", fill=TEXT_WHITE, font=font_mono)

        # Action Buttons
        draw.rectangle([770, 230, 1055, 275], fill=ACCENT_CYAN)
        draw.text((785, 245), "Soft Revert Selected Commit", fill='#000000', font=font_bold)

        draw.rectangle([770, 290, 1055, 335], fill='#EF4444')
        draw.text((785, 305), "Hard Reset to Selected Commit", fill=TEXT_WHITE, font=font_bold)

        draw.rectangle([770, 350, 1055, 395], fill='#334155')
        draw.text((785, 365), "Paste Commit Hash", fill=TEXT_WHITE, font=font_normal)

    elif content_type == "dev_tools":
        draw.text((30, 175), "🛠️ Developer Power Tools (Branches, Stashes, .gitignore)", fill=TEXT_WHITE, font=font_title)

        draw.rectangle([30, 210, 360, 470], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((45, 225), "Branch Manager", fill=ACCENT_CYAN, font=font_bold)
        draw.text((45, 255), "Current: main", fill=ACCENT_GREEN, font=font_mono)
        draw.rectangle([45, 285, 345, 315], fill='#0F172A', outline=BORDER_COLOR)
        draw.text((55, 292), "feature/new-engine", fill=TEXT_MUTED, font=font_mono)
        draw.rectangle([45, 330, 180, 360], fill=ACCENT_BLUE)
        draw.text((60, 338), "Create Branch", fill=TEXT_WHITE, font=font_bold)

        draw.rectangle([380, 210, 710, 470], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((395, 225), "Stash Manager", fill=ACCENT_PURPLE, font=font_bold)
        draw.text((395, 255), "Saved Stashes: 0", fill=TEXT_MUTED, font=font_mono)
        draw.rectangle([395, 290, 520, 320], fill=ACCENT_PURPLE)
        draw.text((410, 298), "Stash Changes", fill=TEXT_WHITE, font=font_bold)

        draw.rectangle([730, 210, 1070, 470], fill='#1E293B', outline=BORDER_COLOR)
        draw.text((745, 225), ".gitignore Generator", fill=ACCENT_GREEN, font=font_bold)
        draw.text((745, 255), "Templates: Python, Node, C++, Go", fill=TEXT_MUTED, font=font_normal)
        draw.rectangle([745, 290, 950, 320], fill=ACCENT_GREEN)
        draw.text((760, 298), "Generate .gitignore", fill='#000000', font=font_bold)

    # Bottom Status Bar
    draw.rectangle([0, height - 35, width, height], fill=BG_HEADER)
    draw.text((15, height - 25), "Execution Console Log | Ready", fill=ACCENT_GREEN, font=font_normal)
    draw.text((width - 240, height - 25), "Developed by blazecodeprakhar", fill=ACCENT_CYAN, font=font_normal)

    save_path = os.path.join(r"c:\Users\prakh\OneDrive\Desktop\researchs", name)
    img.save(save_path)
    print(f"[OK] Rendered software screenshot: {save_path}")

def generate_all():
    draw_software_screenshot("screenshot_dashboard.png", "Dashboard", "dashboard")
    draw_software_screenshot("screenshot_self_analysis.png", "Self Analysis", "self_analysis")
    draw_software_screenshot("screenshot_auto_push.png", "Automatic Push", "auto_push")
    draw_software_screenshot("screenshot_history_undo.png", "History & Undo", "history_undo")
    draw_software_screenshot("screenshot_dev_tools.png", "Developer Tools", "dev_tools")

if __name__ == "__main__":
    generate_all()
