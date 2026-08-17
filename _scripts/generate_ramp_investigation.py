from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
)

OUT = r"D:\Projects\Wergonic\Local Only\Tasks\RAMP_MEC_Scoring_Investigation.pdf"

W, H = A4
M = 2 * cm

doc = SimpleDocTemplate(
    OUT, pagesize=A4, leftMargin=M, rightMargin=M,
    topMargin=1.8 * cm, bottomMargin=1.5 * cm,
    title="RAMP / MEC Scoring - Investigation Task",
    author="Wergonic",
)

s = getSampleStyleSheet()
PRIMARY = HexColor("#1a1a2e")

s.add(ParagraphStyle("DocTitle", parent=s["Title"],
    fontSize=17, leading=21, spaceAfter=2, textColor=PRIMARY))
s.add(ParagraphStyle("Sub", parent=s["Normal"],
    fontSize=9.5, leading=13, spaceAfter=14, textColor=HexColor("#666"),
    alignment=TA_CENTER))
s.add(ParagraphStyle("S1", parent=s["Heading1"],
    fontSize=12.5, leading=15, spaceBefore=16, spaceAfter=7, textColor=PRIMARY))
s.add(ParagraphStyle("ItemTitle", parent=s["Heading2"],
    fontSize=10.5, leading=13, spaceBefore=13, spaceAfter=4, textColor=HexColor("#2d3436")))
s.add(ParagraphStyle("B", parent=s["Normal"],
    fontSize=9.5, leading=14, spaceAfter=5))
s.add(ParagraphStyle("BL", parent=s["Normal"],
    fontSize=9.5, leading=14, spaceAfter=4, leftIndent=16, bulletIndent=4))
s.add(ParagraphStyle("Ask", parent=s["Normal"],
    fontSize=9.5, leading=14, spaceAfter=4, leftIndent=10,
    textColor=HexColor("#444"), fontName="Helvetica-Oblique"))
s.add(ParagraphStyle("Footer", parent=s["Normal"],
    fontSize=8, leading=10, textColor=HexColor("#999"), alignment=TA_CENTER))


def hr(space=6):
    return HRFlowable(width="100%", thickness=0.5, color=HexColor("#ddd"),
                      spaceBefore=space, spaceAfter=space)


def p(t):
    return Paragraph(t, s["B"])


def bul(t):
    return Paragraph(t, s["BL"], bulletText="\u2022")


def ask(t):
    return Paragraph("<b>Answer:</b> " + t, s["Ask"])


def item(title, body_paras):
    return KeepTogether([Paragraph(title, s["ItemTitle"])] + body_paras)


story = []

story.append(Paragraph("RAMP / MEC Scoring &ndash; Investigation Task", s["DocTitle"]))
story.append(Paragraph("Wergonic &nbsp;&middot;&nbsp; 17 August 2026", s["Sub"]))

story.append(Paragraph("What this is", s["S1"]))
story.append(p(
    "Several RAMP and MEC numbers disagree with each other across the phone app, the web app "
    "and the Word report. We do not currently know which side is right, and most of these have "
    "only been argued from memory, never checked against the official RAMP document."
))
story.append(p(
    "<b>This is an investigation task, not a fix task.</b> Do not change behaviour unless a point "
    "below explicitly says to fix it. For every other point, the deliverable is a short written "
    "answer: what the code actually does today, what the official source says, and what you would "
    "change. We decide after that, you do not need to make any product call yourself."
))

story.append(Paragraph("Start here", s["S1"]))
story.append(p(
    "Find the official RAMP documentation the scoring was based on. Almost every point below is "
    "an open argument that nobody has settled with the source in hand. Write down the page number "
    "for each answer so it stops being an opinion."
))

story.append(Paragraph("To check and report back", s["S1"]))

story.append(item("1. Head bending backwards is measured three different ways", [
    p("The threshold is &minus;10&deg; in the risk verdict and the Word report, and &minus;5&deg; on the "
      "phone and in RAMP. The same worker gets a different answer depending on where you look. "
      "Farhad ruled &minus;5 in writing on 3 August; the code was never changed."),
    p("Trunk backwards stays at &minus;10&deg;. That one is deliberate &ndash; do not merge the two."),
    p("There is also a test in the repo claiming &minus;10 was &ldquo;confirmed by the team&rdquo;. "
      "Find out who wrote it and who &ldquo;the team&rdquo; was."),
    ask("what the official table says, and every place in the code the threshold is written."),
]))

story.append(item("2. Is a RAMP score of 1.5 valid?", [
    p("Head-backwards is the only one of the six posture scores built with 5 steps instead of 7, "
      "and the only one that ever outputs 1.5 or 6. Two other questions already output 0.5, so "
      "fractional scores do exist somewhere in our code."),
    p("A code comment says someone rewrote this ladder &ldquo;to match the official RAMP table&rdquo;. "
      "Find out who, and against what."),
    ask("the official step values for this question, checked one by one, with the page number."),
]))

story.append(item("3. The same score gets two different colours", [
    p("Two separate pieces of code decide the colour of a score and they disagree. A 1.5 is yellow "
      "on the compare-assessments table and green on the single results page. Separately, a score "
      "of 1 is green everywhere except question 1.8, where it is yellow."),
    ask("what the correct colour rule is according to the source. Then fix it so there is one "
        "rule used everywhere."),
]))

story.append(item("4. Hand distance ignores the selected task", [
    p("A RAMP for one task should only look at that task's time. Five of the six posture measures "
      "do. Hand distance uses the whole recording instead, so a result labelled as one task is "
      "mixed with the rest of the day."),
    p("Be careful, this is bigger than it looks: that number is calculated once when the recording "
      "is uploaded and stored as a session total. It probably cannot be filtered afterwards, it has "
      "to be recalculated."),
    ask("why it works this way, and an estimate of the change. Do not start before we see it."),
]))

story.append(item("5. Hand distance is a guess presented as a measurement", [
    p("There is no sensor on the hand &ndash; the position is estimated from the arm angles and the "
      "length of the arm. The assessor can type the worker's arm and forearm length when running "
      "an assessment. MEC uses what they typed. RAMP ignores it and always uses 32&nbsp;cm and "
      "27&nbsp;cm, hardcoded, so the two assessments can disagree about the same worker."),
    ask("confirm this, then fix: make RAMP use the entered lengths, and label the number as an "
        "estimate."),
]))

story.append(item("6. Trunk and head percentiles never reach the Word report", [
    p("They are calculated and stored correctly, then dropped at the last step because the report "
      "table only knows how to print arm rows."),
    ask("confirm, then fix: add forward and backward bending rows for trunk and head. Side bending "
        "stays out, Farhad says it is not accurate enough to publish."),
]))

story.append(item("7. A perfect result looks the same as no result", [
    p("If a worker never bends past the threshold, RAMP questions 1.1 and 1.2 show nothing at all &ndash; "
      "no score, no colour. That looks exactly like a question where the sensor was missing. "
      "Questions 1.3 to 1.6 show a green 0 in the same situation, which is correct."),
    ask("confirm, then fix: make 1.1 and 1.2 show the green 0 too, and check it is counted in the "
        "green total at the top of the page."),
]))

story.append(item("8. RAMP question 1.5 shows the wrong question", [
    p("The heading is about upper arm posture, hand in or above shoulder height. The question "
      "printed underneath asks about bending the upper body forwards or to the side &ndash; that is "
      "question 1.3's text, copied word for word. So the ergonomist is asked about the back while "
      "the score underneath is about the arm. The help text is correct, only the question is wrong."),
    ask("fix it, in all five languages."),
]))

story.append(item("9. RAMP sub-rows are all numbered 1.1", [
    p("Inside every RAMP item the rows restart at 1.1, so &ldquo;1.1&rdquo; appears under item 1.1, again "
      "under 1.2, again under 1.3, and so on. They are not sub-questions, they are what we measured: "
      "forward bending, side bending, backward bending."),
    ask("fix it: name them instead of numbering them."),
]))

story.append(item("10. What is MEC question 11 supposed to measure?", [
    p("The screen calls it &ldquo;Neck bending&rdquo;. The code calculates it as the head angle minus the "
      "body angle. The backend's internal name says it should be the head's own angle. Both are "
      "defensible &ndash; do not pick one."),
    p("Same block of code has a second problem: the head and trunk readings are matched by their "
      "position in the list instead of by time. If either sensor drops a reading, everything after "
      "it compares the head at one moment against the trunk at another, and the extra readings are "
      "silently thrown away. Everywhere else in the system matches by time."),
    ask("document what it does today and what the source expects, and find out why the earlier "
        "attempt at fixing the time matching was reverted."),
]))

story.append(item("11. MEC questions 12.1 and 12.2 are dead", [
    p("They are listed in the backend but never calculated, and nothing on the web side reads them. "
      "No screen has a place for them, so no customer has ever seen a blank."),
    ask("confirm that, and tell us whether to delete them or build them."),
]))

story.append(item("12. The AI section of the report can disappear silently", [
    p("If the AI call fails, the report is still generated, just without that section."),
    ask("confirm this is what the code does now, and whether the user gets any indication at all. "
        "No change yet."),
]))

story.append(Spacer(1, 18))
story.append(hr())
story.append(Paragraph(
    "Send back one short answer per point. Anything you cannot settle from the source, "
    "say so and stop there &ndash; do not guess.", s["Footer"]))

doc.build(story)
print("written:", OUT)
