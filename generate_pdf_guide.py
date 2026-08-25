import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_pdf(filename="Software_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0B0F19")
    ACCENT_CYAN = colors.HexColor("#0891B2")
    ACCENT_BLUE = colors.HexColor("#2563EB")
    TEXT_DARK = colors.HexColor("#1F2937")
    BG_LIGHT = colors.HexColor("#F3F4F6")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=ACCENT_CYAN,
        alignment=TA_CENTER,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4B5563"),
        alignment=TA_CENTER,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=ACCENT_BLUE,
        spaceBefore=14,
        spaceAfter=8
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=ACCENT_CYAN,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK,
        spaceAfter=6,
        alignment=TA_LEFT
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#111827"),
        backColor=BG_LIGHT,
        borderColor=colors.HexColor("#E5E7EB"),
        borderWidth=1,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=8
    )

    story = []

    # Title Banner
    story.append(Paragraph("GitHub Easy Push", title_style))
    story.append(Paragraph("Official Illustrated User Guide & Developer Manual", subtitle_style))
    story.append(Paragraph("Created by Prakhar Yadav (@blazecodeprakhar)", ParagraphStyle('Author', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=10, textColor=ACCENT_CYAN)))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_CYAN, spaceAfter=15))

    # Overview Section
    story.append(Paragraph("1. Executive Overview", h1_style))
    story.append(Paragraph(
        "GitHub Easy Push is an automated desktop application designed to streamline software deployment, commit formatting, version tagging, and repository maintenance for Windows developers. It removes manual command line complexity while providing advanced self analysis and commit rollback tools.",
        body_style
    ))

    # Features Table
    data = [
        [Paragraph("<b>Feature Module</b>", body_style), Paragraph("<b>Function & Benefit</b>", body_style)],
        [Paragraph("One Click Smart Push", body_style), Paragraph("Scans changed files, generates timestamped update notes, stages, commits, and pushes in 1 click.", body_style)],
        [Paragraph("Manual Push & Versioning", body_style), Paragraph("Individual file staging table with automatic semantic version bumping (Patch, Minor, Major).", body_style)],
        [Paragraph("History & Undo Engine", body_style), Paragraph("Visual commit history viewer with Soft Undo (revert) and Hard Reset to target commit hash.", body_style)],
        [Paragraph("Self Analyzing Engine", body_style), Paragraph("Inspects Git repositories, commit parent lineage graphs, and .gitignore rule protection.", body_style)],
        [Paragraph("Developer Power Tools", body_style), Paragraph("Branch manager, stash manager, and ready to use .gitignore stack templates.", body_style)]
    ]
    t = Table(data, colWidths=[150, 380])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D1D5DB")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Illustrated Guide Sections with Embedded Real Screenshots
    base_dir = r"c:\Users\prakh\OneDrive\Desktop\researchs"
    images_dir = os.path.join(base_dir, "assets", "images")

    story.append(Paragraph("2. Illustrated Step by Step Guide", h1_style))

    # Step 1: Dashboard
    story.append(Paragraph("Module 1: Main Dashboard & Repository Connection", h2_style))
    story.append(Paragraph(
        "Select your project directory or click Browse. Paste your GitHub remote link into Set GitHub Remote Origin URL and click Save Origin. If your folder is not a Git repo yet, GitHub Easy Push will prompt to initialize Git for you automatically.",
        body_style
    ))
    dash_img = os.path.join(images_dir, "screenshot_dashboard.png")
    if os.path.exists(dash_img):
        story.append(Image(dash_img, width=460, height=270))
        story.append(Spacer(1, 12))

    # Step 2: Self Analysis
    story.append(Paragraph("Module 2: Workspace Self Analysis Engine", h2_style))
    story.append(Paragraph(
        "Click Self Analyze to inspect parent child commit lineage, audit .gitignore security protection rules for sensitive files (.env, build directories), and monitor commit divergence.",
        body_style
    ))
    sa_img = os.path.join(images_dir, "screenshot_self_analysis.png")
    if os.path.exists(sa_img):
        story.append(Image(sa_img, width=460, height=270))
        story.append(Spacer(1, 12))

    # Step 3: Automatic Push
    story.append(Paragraph("Module 3: One Click Smart Automatic Push", h2_style))
    story.append(Paragraph(
        "Select your automatic version bump preference (Patch +0.0.1, Minor +0.1.0, Major +1.0.0). Click AUTO COMMIT AND PUSH TO GITHUB to stage all changes, format update notes, and push instantly.",
        body_style
    ))
    ap_img = os.path.join(images_dir, "screenshot_auto_push.png")
    if os.path.exists(ap_img):
        story.append(Image(ap_img, width=460, height=270))
        story.append(Spacer(1, 12))

    # Step 4: History & Undo
    story.append(Paragraph("Module 4: Commit History Timeline & Undo Engine", h2_style))
    story.append(Paragraph(
        "Inspect recent commit history. Use Soft Revert to create an inverse commit while keeping local edits, or Hard Reset to restore repository state back to any commit hash.",
        body_style
    ))
    hu_img = os.path.join(images_dir, "screenshot_history_undo.png")
    if os.path.exists(hu_img):
        story.append(Image(hu_img, width=460, height=270))
        story.append(Spacer(1, 12))

    # Step 5: Dev Tools
    story.append(Paragraph("Module 5: Developer Power Tools", h2_style))
    story.append(Paragraph(
        "Manage branches, stash uncommitted working edits, and generate ready to use .gitignore templates for Python, Node, C++, Java, and Go.",
        body_style
    ))
    dt_img = os.path.join(images_dir, "screenshot_dev_tools.png")
    if os.path.exists(dt_img):
        story.append(Image(dt_img, width=460, height=270))
        story.append(Spacer(1, 12))

    # Section 3: Build Instructions
    story.append(Paragraph("3. Compiling Standalone Executables", h1_style))
    story.append(Paragraph(
        "To compile a new standalone executable file from Python source code, run:",
        body_style
    ))
    story.append(Paragraph("python build_exe.py", code_style))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB"), spaceAfter=8))
    story.append(Paragraph("GitHub Easy Push Official Guide | Created by Prakhar Yadav (@blazecodeprakhar)", ParagraphStyle('FooterText', alignment=TA_CENTER, fontName='Helvetica', fontSize=8, textColor=colors.HexColor("#9CA3AF"))))

    doc.build(story)
    print(f"[OK] Generated illustrated PDF guide: {filename}")

if __name__ == "__main__":
    create_pdf("Software_Guide.pdf")
    create_pdf("GitHub_Easy_Push_Guide.pdf")
    # Also save in assets/docs/
    os.makedirs(r"c:\Users\prakh\OneDrive\Desktop\researchs\assets\docs", exist_ok=True)
    create_pdf(r"c:\Users\prakh\OneDrive\Desktop\researchs\assets\docs\Software_Guide.pdf")
