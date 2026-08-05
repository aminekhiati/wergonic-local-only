from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)

WIDTH, HEIGHT = A4
MARGIN = 2 * cm

doc = SimpleDocTemplate(
    "/Users/mac/Projects/Wergonic/Local Only/Sidali_Bedrani_Evaluation_May_Jun_2026.pdf",
    pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=MARGIN,
)

styles = getSampleStyleSheet()

# Custom styles
styles.add(ParagraphStyle(
    "DocTitle", parent=styles["Title"],
    fontSize=18, leading=22, spaceAfter=4,
    textColor=HexColor("#1a1a2e"),
))
styles.add(ParagraphStyle(
    "DocSubtitle", parent=styles["Normal"],
    fontSize=10, leading=14, spaceAfter=16,
    textColor=HexColor("#555555"), alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    "SectionHead", parent=styles["Heading2"],
    fontSize=13, leading=16, spaceBefore=18, spaceAfter=8,
    textColor=HexColor("#1a1a2e"), borderPadding=(0, 0, 2, 0),
))
styles.add(ParagraphStyle(
    "SubHead", parent=styles["Heading3"],
    fontSize=11, leading=14, spaceBefore=12, spaceAfter=6,
    textColor=HexColor("#2d3436"),
))
styles.add(ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=9.5, leading=13.5, spaceAfter=6,
    alignment=TA_JUSTIFY,
))
styles.add(ParagraphStyle(
    "BodyBold", parent=styles["Normal"],
    fontSize=9.5, leading=13.5, spaceAfter=6,
    alignment=TA_JUSTIFY, fontName="Helvetica-Bold",
))
styles.add(ParagraphStyle(
    "BulletCustom", parent=styles["Normal"],
    fontSize=9.5, leading=13.5, spaceAfter=3,
    leftIndent=14, bulletIndent=0,
    bulletFontName="Helvetica", bulletFontSize=9.5,
))
styles.add(ParagraphStyle(
    "SmallNote", parent=styles["Normal"],
    fontSize=8, leading=10, spaceAfter=4,
    textColor=HexColor("#888888"),
))

PRIMARY = HexColor("#1a1a2e")
HEADER_BG = HexColor("#e8eaf6")
ROW_ALT = HexColor("#f5f5f5")

def make_table(headers, rows, col_widths=None):
    data = [headers] + rows
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), PRIMARY),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(style_cmds))
    return t

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=HexColor("#dddddd"),
                       spaceBefore=6, spaceAfter=6)

# ── Build story ──────────────────────────────────────────────
story = []

story.append(Paragraph("Developer Evaluation Report", styles["DocTitle"]))
story.append(Paragraph("Sidali Bedrani — Mobile Developer (Flutter / BLE)", styles["DocSubtitle"]))
story.append(Paragraph("Period: May 1 – June 22, 2026 &nbsp;|&nbsp; Prepared: June 22, 2026 &nbsp;|&nbsp; Wergonic", styles["DocSubtitle"]))
story.append(hr())

# ── 1. Scope ─────────────────────────────────────────────────
story.append(Paragraph("1. Scope & Methodology", styles["SectionHead"]))
story.append(Paragraph(
    "This evaluation covers the period May 1 – June 22, 2026. It is based on three data sources: "
    "(1) task records exported from the project management tool, including logged hours and task IDs; "
    "(2) the full Git history of the <b>wergonic-flutter</b> repository (all branches, primarily <i>dev</i> and <i>new_refactoring</i>); "
    "(3) commit diffs measuring the actual code changes per task. "
    "Tasks were classified as <i>research/investigation</i> (no code deliverable expected) or <i>coding</i> "
    "(a commit is expected). Each coding task ID was cross-referenced against commit messages.", styles["Body"]))
story.append(Paragraph(
    "It is important to note that much of the coding work in this period was done using Claude Code (AI-assisted coding). "
    "This is an approved workflow. However, it changes the expected time-to-output ratio: tasks that would normally "
    "take a developer several hours of manual coding can now be completed in significantly less time. "
    "Time estimates should reflect the actual work performed — prompting, reviewing AI output, testing on hardware — "
    "not what the task would have taken without AI assistance.", styles["Body"]))

# ── 2. Summary Numbers ──────────────────────────────────────
story.append(Paragraph("2. Summary Numbers", styles["SectionHead"]))

summary_data = [
    ["Employment", "Full-time, 40 h/week"],
    ["Expected hours (leave-adjusted)", "304 h (2 sick days taken)"],
    ["Logged hours", "229.95 h"],
    ["Utilization", "75.6 %"],
    ["Total tasks", "~88"],
    ["Research / investigation tasks", "~24 tasks — 87.5 h (38 % of total)"],
    ["Coding tasks", "~64 tasks — 142.5 h"],
    ["Non-merge commits", "75"],
]
story.append(make_table(["Metric", "Value"], summary_data,
                         col_widths=[5.5 * cm, 10 * cm]))

# ── 3. Commit Coverage ──────────────────────────────────────
story.append(Paragraph("3. Commit Coverage", styles["SectionHead"]))
story.append(Paragraph(
    "The majority of coding tasks have properly tagged commits (e.g. <font face='Courier' size='8'>fix: [WH-296]</font>). "
    "This is good practice and makes traceability straightforward. "
    "However, the following coding tasks have <b>no identifiable commit</b> on any branch:", styles["Body"]))

missing_data = [
    ["WH-218", "4 h", "May 7", "fix cascading by pausing stream"],
    ["WH-219", "3 h", "May 7", "change pause by widening radio bandwidth"],
    ["WH-223", "4 h", "May 8", "optimize the pause to reduce data loss"],
    ["WH-224", "2 h", "May 8", "structural pause (noted: broke the flow)"],
    ["WH-225", "1 h", "May 8", "cubit-side paused flag"],
    ["WH-226", "3 h", "May 8", "reduce data loss to 3 s"],
    ["WH-336", "3 h", "Jun 3", "make RSSI live in pairing/calibration/recording"],
    ["WH-337", "1 h", "Jun 3", "fix live RSSI interfering with battery"],
    ["WH-207", "2 h", "May 6", "guard isWaitingForAdapter reset"],
]
story.append(make_table(
    ["Task", "Hours", "Date", "Description"], missing_data,
    col_widths=[1.8 * cm, 1.4 * cm, 1.8 * cm, 10.5 * cm]))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Total: 23 hours of coding work with no commit.</b> "
    "The May 7–8 block (17 h across 6 tasks) is the most notable gap — two full working days of reported feature/bug work "
    "without a single commit on any branch. Even exploratory or failed attempts should normally produce at least a WIP commit.", styles["Body"]))
story.append(Paragraph(
    "Note: WH-336/337 may have been rolled into the WH-335 commit from June 5. "
    "WH-448 and WH-454 (2.5 h, June 19) are recent and in Testing status — they may be work-in-progress not yet pushed.", styles["SmallNote"]))

# ── 4. Time vs Output ───────────────────────────────────────
story.append(Paragraph("4. Time vs. Code Output", styles["SectionHead"]))
story.append(Paragraph(
    "Some tasks show a significant gap between logged hours and the size of the actual code change. "
    "While BLE/hardware work involves build-deploy-test cycles that don't show up in diffs, "
    "the following stand out — particularly in an AI-assisted workflow where code generation itself is fast:", styles["Body"]))

time_data = [
    ["WH-296", "3 h", "10 lines", "Stuck connecting status fix — small logic change"],
    ["WH-297", "3 h", "22 lines", "Reconnect delay — minor parameter adjustment"],
    ["WH-251", "3 h", "31 lines", "Calibration reload fix"],
    ["WH-246", "3 h", "~10 lines\n(+pubspec.lock)", "Calibration disconnect — actual code minimal"],
    ["WH-264", "4 h", "68 lines", "Skip wrist calibration — single conditional block"],
    ["WH-389", "2 h", "11 lines", "Stream resubscribe after reconnect"],
]
story.append(make_table(
    ["Task", "Logged", "Change Size", "Notes"], time_data,
    col_widths=[1.8 * cm, 1.4 * cm, 2.5 * cm, 9.8 * cm]))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "These tasks average roughly 1 h of realistic effort each (prompt, review, deploy to device, verify). "
    "The logged times suggest the estimates were not adjusted for AI-assisted development speed.", styles["Body"]))

# ── 5. Research time ─────────────────────────────────────────
story.append(Paragraph("5. Research & Investigation Time", styles["SectionHead"]))
story.append(Paragraph(
    "38 % of all logged time (87.5 h) was spent on research or investigation tasks. "
    "These produce no code artifact and are inherently difficult to verify. "
    "Some level of research is expected and necessary in BLE/embedded work — debugging on physical hardware, "
    "analyzing sensor logs, reverse-engineering SDKs. However, the proportion is notably high.", styles["Body"]))

research_data = [
    ["WH-418", "13 h", "Verify CSV expected_rows vs rows_written"],
    ["WH-313", "11 h", "Check why hand/forearm disconnect and don't reconnect"],
    ["WH-18 (parent)", "10.25 h", "CSV/ZIP file verification (on top of 10.25 h coding)"],
    ["WH-390", "6 h", "Hard test the native BLE migration"],
    ["WH-243", "5 h", "Full test round"],
    ["WH-316 + WH-314", "8 h", "Investigate MDS stream disconnects (two sub-tasks, same issue)"],
    ["WH-332", "4 h", "Check code for non-reconnection triggers"],
    ["WH-327", "4 h", "Full test round before pushing"],
]
story.append(make_table(
    ["Task", "Hours", "Description"], research_data,
    col_widths=[2.5 * cm, 1.5 * cm, 11.5 * cm]))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "A typical ratio for this type of work would be 20–25 % research vs. coding. "
    "Going forward, research tasks above 4 h should include a written summary of findings, "
    "even if brief, to provide traceability and demonstrate the investigation was thorough.", styles["Body"]))

# ── 6. Strengths ─────────────────────────────────────────────
story.append(Paragraph("6. Strengths", styles["SectionHead"]))
bullets = [
    "<b>BLE domain expertise</b> — The native Kotlin BLE engine migration (WH-349 and sub-tasks) was the most complex "
    "initiative in this period. It required reverse-engineering a closed-source AAR, designing a hybrid architecture, "
    "and migrating scanning, connection, streaming, battery telemetry, RSSI, and DFU flows. This demonstrates real depth.",
    "<b>Commit discipline</b> — Task IDs are consistently tagged in commit messages. The PR flow through dev/new_refactoring "
    "is clean. This makes code review and traceability straightforward.",
    "<b>Output volume</b> — 75 non-merge commits across ~7 weeks. The RSSI feature (WH-335 family) and native migration "
    "were both delivered end-to-end.",
    "<b>Progressive complexity</b> — Work progressed from BLE bug fixes to a new feature (RSSI monitoring) to a full "
    "architectural migration (native engine). This shows growth over the period.",
    "<b>Hardware-validated work</b> — BLE sensor work can't be faked. Pairing, calibration, and recording either work on "
    "real sensors or they don't. The deployed tasks passed real-device testing.",
]
for b in bullets:
    story.append(Paragraph(b, styles["BulletCustom"], bulletText="•"))

# ── 7. Areas for improvement ─────────────────────────────────
story.append(Paragraph("7. Areas for Improvement", styles["SectionHead"]))
bullets2 = [
    "<b>Time estimates must reflect AI-assisted speed.</b> When Claude Code generates the code, the developer's work is "
    "prompting, reviewing, and testing — not writing every line manually. Logged hours should match this reality. "
    "A 10-line fix should not take 3 hours regardless of the tooling used for the fix itself.",
    "<b>Every coding task needs a commit.</b> 23 hours of coding work had no corresponding commit on any branch. "
    "Even failed experiments or iterative approaches should be committed (on a feature branch) so that work is visible "
    "and reviewable. The May 7–8 gap of 17 hours is the clearest example.",
    "<b>Research tasks need deliverables.</b> At 38 % of total time, investigation tasks are a large investment. "
    "Tasks above 4 h should produce a brief written finding — a comment on the task, a markdown file, or structured notes. "
    "This helps the team and makes the time investment verifiable.",
    "<b>Utilization gap.</b> 229.95 h logged against 304 h expected (75.6 %). The remaining ~74 h (over 9 working days) "
    "are unaccounted for beyond 2 sick days. Time tracking should cover the full working week, including meetings, "
    "code reviews, and other activities.",
    "<b>Task descriptions should be in your own words.</b> Several task descriptions — particularly in the native migration "
    "— read as AI-generated text. While using AI tools for coding is encouraged, task descriptions should reflect "
    "the developer's own understanding in plain language. This helps the team assess comprehension, not just output.",
]
for b in bullets2:
    story.append(Paragraph(b, styles["BulletCustom"], bulletText="•"))

# ── 8. Expectations ──────────────────────────────────────────
story.append(Paragraph("8. Expectations Going Forward", styles["SectionHead"]))
fwd = [
    "All coding tasks must have at least one commit, tagged with the task ID. No exceptions.",
    "Time logs should be adjusted to reflect AI-assisted workflows. If Claude Code generates the code in minutes, "
    "log the actual time spent: prompting, reviewing, testing, iterating.",
    "Research/investigation tasks above 4 hours must include a written summary of findings attached to the task.",
    "Full-time hours (40 h/week) should be accounted for. If time is spent on activities not captured in tasks "
    "(meetings, reviews, setup), those should be logged separately.",
    "Task descriptions should be written by the developer, not generated by AI tools.",
]
for i, f in enumerate(fwd, 1):
    story.append(Paragraph(f"<b>{i}.</b> {f}", styles["Body"]))

story.append(Spacer(1, 12))
story.append(hr())
story.append(Paragraph(
    "This report is based on objective data (Git history, task exports, diff analysis). "
    "It is intended as constructive feedback to align on expectations and improve collaboration.",
    styles["SmallNote"]))

# ── Build PDF ────────────────────────────────────────────────
doc.build(story)
print("PDF generated successfully.")
