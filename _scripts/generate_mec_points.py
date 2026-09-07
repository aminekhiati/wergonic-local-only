from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
)

OUT = r"D:\Projects\Wergonic\Local Only\Audits\MEC_Points_To_Confirm_2026-09-07.pdf"

W, H = A4
M = 2 * cm

doc = SimpleDocTemplate(
    OUT, pagesize=A4, leftMargin=M, rightMargin=M,
    topMargin=1.8 * cm, bottomMargin=1.5 * cm,
    title="MEC - Points to Confirm",
    author="Wergonic",
)

s = getSampleStyleSheet()
PRIMARY = HexColor("#1a1a2e")
MUTED = HexColor("#666666")

s.add(ParagraphStyle("DocTitle", parent=s["Title"],
    fontSize=17, leading=21, spaceAfter=2, textColor=PRIMARY))
s.add(ParagraphStyle("Sub", parent=s["Normal"],
    fontSize=9.5, leading=13, spaceAfter=14, textColor=MUTED, alignment=TA_CENTER))
s.add(ParagraphStyle("ItemTitle", parent=s["Heading2"],
    fontSize=11, leading=14, spaceBefore=15, spaceAfter=5, textColor=PRIMARY))
s.add(ParagraphStyle("B", parent=s["Normal"],
    fontSize=9.5, leading=14, spaceAfter=5))
s.add(ParagraphStyle("Lead", parent=s["Normal"],
    fontSize=9.5, leading=14, spaceAfter=10, textColor=HexColor("#333333")))
s.add(ParagraphStyle("Row", parent=s["Normal"],
    fontSize=9.5, leading=14, spaceAfter=3, leftIndent=52, firstLineIndent=-52))
s.add(ParagraphStyle("Footer", parent=s["Normal"],
    fontSize=8, leading=10, textColor=HexColor("#999999"), alignment=TA_CENTER))


def hr(space=6):
    return HRFlowable(width="100%", thickness=0.5, color=HexColor("#dddddd"),
                      spaceBefore=space, spaceAfter=space)


def row(label, text):
    return Paragraph(f'<font color="#888888">{label}</font>&nbsp;&nbsp;{text}', s["Row"])


def item(n, title, scenario, today, propose, note=None):
    parts = [
        Paragraph(f"{n}. {title}", s["ItemTitle"]),
        row("Scenario", scenario),
        row("Today", today),
        row("Propose", propose),
    ]
    if note:
        parts.append(row("Note", note))
    return KeepTogether(parts)


story = [
    Paragraph("MEC &mdash; Points to Confirm", s["DocTitle"]),
    Paragraph("Wergonic &middot; 7 September 2026 &middot; for Farhad Abtahi", s["Sub"]),
    hr(2),
    Paragraph(
        "Six points found while going through the MEC calculation. Every scenario below was run "
        "through the real calculation code, so the numbers are what the product produces today. "
        "Please confirm whether the current behaviour is intended.", s["Lead"]),

    item(
        1, "Repetitive work above the line is not counted",
        "A worker sands a panel at shoulder height. His arm swings between 65 and 80 degrees, "
        "twice a second, for 10 minutes, and never comes down below 60. That is 1200 arm movements.",
        "<b>0 movements, 10 minutes held still.</b> A worker standing frozen with his arm at "
        "85 degrees for the same 10 minutes produces exactly the same report.",
        "Count the movements that happen inside the zone, not only the times the arm enters it.",
        "The height a lift must reach before it counts also shifts with how fast the worker moved. "
        "A fast lift to 65 degrees is counted, a slow lift to 75 is not.",
    ),

    item(
        2, "A reach held still is counted as many movements",
        "A worker leans over a bench with his hand 43 cm out from his body and holds it there, "
        "without moving, for 2 minutes.",
        "<b>24 movements.</b> He reached once. Twelve separate short reaches over the same "
        "2 minutes are counted correctly as 12, so only the held reach is wrong.",
        "Count reaches. Report time spent in the zone as time, not as a number of movements.",
    ),

    item(
        3, "Neck bending is missed when the head and body lean opposite ways",
        "A worker leans his body 12 degrees to the left and tilts his head 40 degrees to the right "
        "to see his work. His neck is bent 52 degrees. He holds it for 10 minutes.",
        "Recorded as 28 degrees, which is below the 30 degree line, so <b>nothing is recorded at "
        "all</b>. The 10 minutes come out as zero. When head and body lean the same way the "
        "calculation is correct.",
        "Subtract the two angles keeping their direction, then take the size. "
        "Today the directions are dropped before subtracting.",
    ),

    item(
        4, "Hand distance is too small when the arm is raised",
        "A worker holds his arm straight out in front of him, horizontal. His hand is 59 cm "
        "from his body.",
        "<b>Calculated as 32 cm.</b> The sensors report each segment's angle measured from "
        "vertical, but the formula adds the upper arm and forearm angles together, which would "
        "only be correct if the forearm angle were measured from the upper arm.",
        "Confirm the intended geometry. The same calculation is also used by the RAMP assessment "
        "and the session reports, not only by MEC.",
    ),

    item(
        5, "The working zone ignores the biggest reaches",
        "The same worker, arm straight out, hand 59 cm from his body.",
        "<b>Counted in neither the yellow nor the red zone.</b> The zone only applies when the "
        "upper arm is below 60 degrees and the elbow is opened past 60. A straight-armed reach "
        "fails both conditions, so the furthest reaches fall outside the assessment.",
        "Confirm which postures the working zone is meant to cover.",
    ),

    item(
        6, "One setting controls two unrelated things",
        "The ergonomist sets one value per body part, labelled Static/Dynamic Threshold. It "
        "decides both how much the angle may wander and still count as holding still, and how "
        "high a movement must reach before it is counted.",
        "Set it low for an honest definition of holding still, and every small lift starts "
        "counting as a movement. Set it high to count only real lifts, and an arm swinging "
        "20 degrees is recorded as held still. The default is 20 degrees, used in 63% of all "
        "assessments run so far.",
        "Split it into two separate settings.",
    ),

    Spacer(1, 16),
    hr(4),
    Paragraph("Wergonic &middot; internal &middot; MEC calculation review", s["Footer"]),
]

doc.build(story)
print("written:", OUT)
