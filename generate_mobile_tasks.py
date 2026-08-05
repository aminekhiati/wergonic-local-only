from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

W, H = A4
M = 2 * cm
AVAIL = W - 2 * M

doc = SimpleDocTemplate(
    "/Users/mac/Projects/Wergonic/Local Only/Mobile_Improvement_Tasks.pdf",
    pagesize=A4, leftMargin=M, rightMargin=M,
    topMargin=1.8 * cm, bottomMargin=1.5 * cm,
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("DocTitle", parent=styles["Title"],
    fontSize=18, leading=22, spaceAfter=2, textColor=HexColor("#1a1a2e")))
styles.add(ParagraphStyle("Sub", parent=styles["Normal"],
    fontSize=10, leading=14, spaceAfter=12, textColor=HexColor("#666"), alignment=TA_CENTER))
styles.add(ParagraphStyle("S1", parent=styles["Heading1"],
    fontSize=14, leading=17, spaceBefore=18, spaceAfter=8, textColor=HexColor("#1a1a2e")))
styles.add(ParagraphStyle("S2", parent=styles["Heading2"],
    fontSize=11.5, leading=14, spaceBefore=12, spaceAfter=5, textColor=HexColor("#2d3436")))
styles.add(ParagraphStyle("B", parent=styles["Normal"],
    fontSize=9.5, leading=14, spaceAfter=5, alignment=TA_JUSTIFY))
styles.add(ParagraphStyle("BL", parent=styles["Normal"],
    fontSize=9.5, leading=14, spaceAfter=4, leftIndent=16, bulletIndent=4))
styles.add(ParagraphStyle("BL2", parent=styles["Normal"],
    fontSize=9, leading=13, spaceAfter=3, leftIndent=32, bulletIndent=20))
styles.add(ParagraphStyle("Ctx", parent=styles["Normal"],
    fontSize=9, leading=13, spaceAfter=6, textColor=HexColor("#555"),
    leftIndent=16, fontName="Helvetica-Oblique"))
styles.add(ParagraphStyle("TC", parent=styles["Normal"],
    fontSize=8.5, leading=11, wordWrap='CJK'))
styles.add(ParagraphStyle("TCB", parent=styles["Normal"],
    fontSize=8.5, leading=11, fontName="Helvetica-Bold", wordWrap='CJK'))
styles.add(ParagraphStyle("Footer", parent=styles["Normal"],
    fontSize=8, leading=10, textColor=HexColor("#999")))

HEADER_BG = HexColor("#e8eaf6")
ROW_ALT = HexColor("#f8f8f8")
PRIMARY = HexColor("#1a1a2e")

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=HexColor("#ddd"), spaceBefore=6, spaceAfter=6)

def b(text):
    return Paragraph(text, styles["BL"], bulletText="\u2022")

def b2(text):
    return Paragraph(text, styles["BL2"], bulletText="\u2013")

def ctx(text):
    return Paragraph(text, styles["Ctx"])

def table(headers, rows, widths):
    hdr = [Paragraph(h, styles["TCB"]) for h in headers]
    body = [[Paragraph(str(c), styles["TC"]) for c in r] for r in rows]
    data = [hdr] + body
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#ccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t = Table(data, colWidths=widths, repeatRows=1, splitInRow=True)
    t.setStyle(TableStyle(cmds))
    return t

story = []

# ── Title ────────────────────────────────────────────────
story.append(Paragraph("Mobile App \u2014 Improvement Tasks", styles["DocTitle"]))
story.append(Paragraph("Wergonic Flutter App", styles["Sub"]))
story.append(Paragraph("June 2026", styles["Sub"]))
story.append(hr())

# ── PHASE 1 ──────────────────────────────────────────────
story.append(Paragraph("Phase 1: Terminology Alignment", styles["S1"]))
story.append(Paragraph(
    "Rename UI labels across all 5 translation files (en, de, nl, sv, es) and any hardcoded Dart strings. "
    "These are display-only changes \u2014 do not rename database fields, API payloads, or model classes.",
    styles["B"]))

term_rows = [
    ["\u201cWork Task\u201d (in free sessions)", "\u201cActivity\u201d", "Setup wizard, recording screen, session history, anywhere outside Work Cycles"],
    ["\u201cWork Label\u201d", "\u201cCondition\u201d", "Add label screen, session metadata, history"],
    ["\u201cWork Break\u201d / \u201cbreakSession\u201d", "\u201cBreak\u201d", "Recording screen, session history"],
    ["\u201cVirtual Coach\u201d (settings section)", "\u201cFeedback Settings\u201d", "Settings screen section header"],
    ["\u201cFinish measurement\u201d", "\u201cEnd Measurement\u201d", "Recording screen button"],
    ["\u201cLeave measurement\u201d", "\u201cDiscard &amp; Exit\u201d", "Recording screen button"],
    ["\u201cInstant feedback refresh rate\u201d", "\u201cFeedback interval\u201d", "Settings"],
]
story.append(table(["Current", "New", "Where"],
    term_rows, [4.2*cm, 3.5*cm, 7.8*cm]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>No change needed:</b> \u201cMeasurements\u201d (list title), \u201cNew measurement\u201d (home), "
    "\u201cWork Task\u201d inside Work Cycles \u2014 these are already correct.", styles["B"]))

# ── PHASE 1b: Backend ────────────────────────────────────
story.append(Paragraph("Phase 1b: Backend APIs (required for Phase 2)", styles["S1"]))
story.append(Paragraph(
    "The mobile app needs these endpoints to support conditions and activities. "
    "The data structures already exist in the web prototype.", styles["B"]))
story.append(b("<b>Activity list endpoint</b> \u2014 fetch the org\u2019s activity groups and their activities (closed list the user picks from during recording)"))
story.append(b("<b>Condition groups endpoint</b> \u2014 fetch the org\u2019s condition groups with selection type (single-choice / multi-choice) and their values"))
story.append(b("<b>Extend sync payload</b> \u2014 the measurement sync must include the selected condition values so they are stored on the backend"))

# ── PHASE 2 ──────────────────────────────────────────────
story.append(Paragraph("Phase 2: Measurement Setup Flow Redesign", styles["S1"]))

# 2.1 Home
story.append(Paragraph("2.1 Home Screen", styles["S2"]))
story.append(ctx(
    "Currently the home screen is nearly empty \u2014 just a FAB and sensor status. "
    "80% of app opens are repeat setups. The home should make repeating fast."))
story.append(b(
    "<b>Quick Start card</b> \u2014 shows the last measurement setup. "
    "If last was a Work Cycle: \u201cRecord [Worker] at [Station]?\u201d. "
    "If last was free: \u201cRecord [Worker]?\u201d. "
    "One tap reconnects sensors, recalibrates, and starts recording."))
story.append(b("<b>Sync banner</b> \u2014 \u201c3 measurements waiting to sync\u201d with a sync button. Only visible when there are pending measurements."))
story.append(b("<b>Recent measurements</b> \u2014 last 3\u20135 as compact cards (worker name, date, duration, sync status). Tap to view or sync."))
story.append(b("<b>Sensor status row</b> \u2014 battery levels and connection state for cached sensors. Always visible so the ergonomist is never surprised by a dead sensor."))

# 2.2 Worker selection
story.append(Paragraph("2.2 Worker Selection Step", styles["S2"]))
story.append(ctx("Currently just a search field. Most ergonomists work with the same 5\u201310 workers repeatedly."))
story.append(b("<b>Recent workers</b> \u2014 show the last 5 used workers as avatar chips at the top. One tap to select."))
story.append(b("Search bar below for other workers"))
story.append(b("\u201cNew Worker\u201d button at the bottom"))

# 2.3 Conditions
story.append(Paragraph("2.3 Conditions Step (NEW)", styles["S2"]))
story.append(ctx(
    "Conditions are whole-measurement metadata (e.g., Shift Type, Environment). "
    "They are defined per org in the Work Library. The mobile app currently has no support for conditions."))
story.append(b("Add a new step after worker selection, before work setup"))
story.append(b("Show each of the org\u2019s condition groups as a visual selector:"))
story.append(b2("<b>Single-choice groups</b> (e.g., Shift Type) \u2192 horizontal chip row \u2014 tap one"))
story.append(b2("<b>Multi-choice groups</b> (e.g., Environment) \u2192 toggleable chips \u2014 tap to select multiple"))
story.append(b("If the org has no conditions configured, skip this step automatically"))
story.append(b("Ask at the start of the measurement, not the end \u2014 conditions are known upfront (shift, weather) and asking at the end risks being skipped"))

# 2.4 Work setup
story.append(Paragraph("2.4 Work Setup Step", styles["S2"]))
story.append(ctx(
    "Currently the user picks between \u201cWork Task\u201d and \u201cWork Cycle\u201d \u2014 confusing terminology and forced choice. "
    "This step should adapt to what the org actually has configured."))
story.append(b("If org has <b>only Work Cycles</b> \u2192 go straight to the hierarchy picker (Factory \u2192 Line \u2192 Station \u2192 Operator \u2192 Model). Show recently used cycles at the top."))
story.append(b("If org has <b>only Activities</b> (no Work Cycles) \u2192 show the org\u2019s activity list. Let the user check which activities they expect to record. These become quick-switch buttons during recording."))
story.append(b("If org has <b>both</b> \u2192 show a simple choice: \u201cFollow a Work Cycle\u201d or \u201cFree Measurement.\u201d"))
story.append(b("This replaces the current \u201cWork Task / Work Cycle\u201d toggle with something that makes sense to the user."))

# 2.5 Pairing
story.append(Paragraph("2.5 Pairing Improvements", styles["S2"]))
story.append(b("If sensors are cached from last measurement, auto-reconnect and show progress per sensor"))
story.append(b("Limb-specific status: \u201cReconnecting Left Arm\u2026\u201d instead of generic \u201cConnecting\u2026\u201d"))
story.append(b("Show battery level and signal strength per sensor during pairing"))
story.append(b("If all sensors reconnect successfully, <b>auto-advance to calibration</b> without requiring the user to tap Next"))

# 2.6 Calibration
story.append(Paragraph("2.6 Calibration Improvements", styles["S2"]))
story.append(ctx("The current calibration flow with videos works well. Only small additions:"))
story.append(b("Add step progress: \u201cCalibrating 2 of 3\u201d"))
story.append(b("After the last calibration succeeds, <b>auto-advance to recording</b> \u2014 one less tap"))

# ── PHASE 3 ──────────────────────────────────────────────
story.append(Paragraph("Phase 3: Recording Screen Overhaul", styles["S1"]))

story.append(Paragraph("3.1 Risk-Colored Limb Tiles", styles["S2"]))
story.append(ctx(
    "Currently the tiles show raw numbers (32\u00b0, 45\u00b0/s) which require expertise to interpret. "
    "The user needs to know one thing: is this good or bad?"))
story.append(b("Change tile backgrounds to <b>green / yellow / red</b> based on standard ergonomic angle thresholds (ISO 11226, EN 1005-4 \u2014 the same ranges referenced by RAMP, RULA, and REBA)"))
story.append(b("Example: arm elevation &lt;30\u00b0 = green, 30\u201360\u00b0 = yellow, &gt;60\u00b0 = red"))
story.append(b("These thresholds are universal across all assessment methods and safe to apply for any org"))
story.append(b("Keep the numbers visible but make them secondary \u2014 the color is the primary information"))

story.append(Paragraph("3.2 Top Bar: Current Activity + Time", styles["S2"]))
story.append(b("Show which activity/task is being recorded and elapsed time"))
story.append(b("Work Cycle: \u201cTask 3/7: Quality Check \u00b7 02:15\u201d"))
story.append(b("Free: \u201cLifting \u00b7 12:34\u201d"))

story.append(Paragraph("3.3 Work Cycle: Task Timeline Bar", styles["S2"]))
story.append(ctx("The current auto/manual toggle works well. These additions give the user more context and control:"))
story.append(b("Horizontal progress bar below the tiles showing all tasks as proportional segments (completed = solid, current = highlighted, upcoming = dimmed)"))
story.append(b("<b>Auto mode:</b> show countdown for current task (\u201cNext in 0:45\u201d). Add an \u201cExtend 30s\u201d button when nearing zero. Show a brief notification when task advances: \u201cNow: [Next Task]\u201d"))
story.append(b("<b>Manual mode:</b> show elapsed vs expected time as a reference (\u201c2:15 / 3:00\u201d). Make the \u201cNext Task\u201d button bigger and more prominent."))

story.append(Paragraph("3.4 Free Session: Activity Bar", styles["S2"]))
story.append(b("Show current activity as a chip at the bottom of the recording screen"))
story.append(b("\u201cSwitch\u201d button \u2192 shows the activities pre-selected in the setup step as quick-switch buttons"))
story.append(b("\u201c+\u201d button \u2192 full activity list for adding one not pre-selected"))
story.append(b("Starting a new activity automatically ends the previous one \u2014 no extra tap needed"))

story.append(Paragraph("3.5 Break Behavior", styles["S2"]))
story.append(b("Adding a break should auto-pause the measurement"))
story.append(b("Ending the break should auto-resume"))
story.append(b("Breaks appear as distinct segments in the task timeline"))

# ── PHASE 4 ──────────────────────────────────────────────
story.append(Paragraph("Phase 4: Completion + Measurements List", styles["S1"]))

story.append(Paragraph("4.1 Completion Screen", styles["S2"]))
story.append(ctx("Currently the summary after recording is minimal. The user has no confirmation that all metadata was captured."))
story.append(b("After recording ends, show a <b>completion checklist</b>: worker \u2713, duration \u2713, limbs recorded \u2713, activities \u2713, conditions \u2713"))
story.append(b("If conditions were not set during setup, prompt here: \u201cNo conditions set \u2192 Add now\u201d"))
story.append(b("\u201cSync Now\u201d as primary action, \u201cSave &amp; Sync Later\u201d as secondary"))

story.append(Paragraph("4.2 Measurements List", styles["S2"]))
story.append(b("Add filter chips above the list: All / Synced / Pending / Today / This Week"))
story.append(b("Richer cards: worker name, date, duration, activity count, sync status"))
story.append(b("Better empty state: illustration + \u201cNo measurements yet\u201d + CTA button"))
story.append(b("Swipe left to delete"))

# ── PHASE 5 ──────────────────────────────────────────────
story.append(Paragraph("Phase 5: Settings + Onboarding + Work Library", styles["S1"]))

story.append(Paragraph("5.1 Settings Restructure", styles["S2"]))
story.append(ctx("Currently all settings are in one long scrollable page with technical labels."))
story.append(b("Reorganize into groups: <b>Sensors &amp; Hardware</b>, <b>Feedback During Recording</b>, <b>Measurement Defaults</b>, <b>Organization</b>, <b>Work Library</b> (read-only), <b>App</b>"))
story.append(b("Add short descriptions under each section header (e.g., \u201cControl how the app alerts you during recording\u201d)"))
story.append(b("Hide advanced/developer settings completely for normal users"))

story.append(Paragraph("5.2 Work Library (Read-Only)", styles["S2"]))
story.append(b("Add a section in settings where the ergonomist can view the org\u2019s Work Library:"))
story.append(b2("Activities \u2014 activity groups and their activities"))
story.append(b2("Conditions \u2014 condition groups and their values"))
story.append(b2("Work Cycles \u2014 the hierarchy (Factory \u2192 Line \u2192 Station\u2026)"))
story.append(b("Read-only \u2014 editing happens on the web"))

story.append(Paragraph("5.3 Onboarding", styles["S2"]))
story.append(b("3 screens for first-time users:"))
story.append(b2("Screen 1: \u201cWergonic measures how your workers move\u201d"))
story.append(b2("Screen 2: \u201cSet up sensors, record a measurement, get risk insights\u201d"))
story.append(b2("Screen 3: \u201cLet\u2019s start your first measurement\u201d \u2192 straight into the setup wizard"))

# ── DO NOT TOUCH ─────────────────────────────────────────
story.append(Paragraph("Do Not Change", styles["S1"]))
story.append(b("<b>BLE / sensor layer</b> \u2014 just stabilized after the native Kotlin migration"))
story.append(b("<b>Sync mechanism</b> \u2014 works, don\u2019t refactor"))
story.append(b("<b>Calibration logic and videos</b> \u2014 working well, only add UI around them"))
story.append(b("<b>Database fields / API payloads</b> \u2014 all renames are UI-only, backend migration is separate"))
story.append(b("<b>Dark theme</b> \u2014 keep it, works for industrial environments"))
story.append(b("<b>\u201cWork Task\u201d inside Work Cycles</b> \u2014 stays as is"))

story.append(Spacer(1, 16))
story.append(hr())
story.append(Paragraph("June 2026 \u2014 Wergonic", styles["Footer"]))

doc.build(story)
print("PDF generated.")
