# Accumulated Feedback — Answers to the Six Decisions

**Wergonic · Mobile**
19 August 2026 · in reply to *Six Decisions Before We Build*, 18 August 2026
Against *Accumulated Feedback — Feature Description*, draft v1.3 (31 July 2026)

---

## Summary of what changed

Two things in this reply are larger than the six questions.

**The arm is not a RAMP item.** It runs on the Lund action levels (AMM Syd, Report 18/2017), which
measure upper-arm elevation from vertical by inclinometry — the same quantity our sensors produce, by
the same method. RAMP II item 1.5 uses hand height because that is what a human observer can judge
reliably across a workshop; the RAMP manual states plainly that the item concerns load from *upper arm
position*, and that hand height is a general correlate of it. So hand-above-shoulder is RAMP's
observational stand-in for the exposure we measure directly. We are not approximating RAMP on the arm.
RAMP 1.5 is out of scope because it is a coarser route to the same construct, not because we failed to
reach it.

**The trunk remains a RAMP proxy**, on items 1.3 and 1.4, and stays described as a RAMP-aligned sensor
proxy pending observational validation. There the sensor genuinely stands in for the observation.

That asymmetry is deliberate and should be stated wherever the feature is described. The blanket
"RAMP-aligned sensor proxy" wording in v1.3 is now correct for the trunk and wrong for the arm.

**Breaks are not excluded from the count.** Both source instruments define their thresholds against a
whole working day that includes breaks and non-productive time, and that time functions as recovery.
Removing it would make us stricter than either source intends.

---

## 1. Duration bands for trunk and head — RESOLVED

**Voice and accumulated feedback cover arms and trunk only.** Head is out of the live feature entirely,
which disposes of the concern about two body parts on one screen being scored two different ways.

**Trunk runs on RAMP II items 1.3 and 1.4, read cumulatively.** The form's wording is "moderate bending
… or more", so any trunk angle at or above 20° accumulates against 1.3, and time above 45° accumulates
against **both** 1.3 and 1.4. Two nested accumulators; one sample can increment both. The trunk
therefore holds two colours, and the worse of them is the one that speaks.

Tables verified against the RAMP II v1.03b workbook (sheet *1 Postures*):

| Item | Green | Yellow | Red |
|---|---|---|---|
| **1.3 Trunk, moderate bending (≥20°)** | < 60 min | 60 min | 120 min |
| **1.4 Trunk, considerable bending (≥45°)** | < 30 min | 30 min | 60 min |

In practice 1.4 drives nearly every warning, since it turns yellow at 30 minutes while 1.3 is still
green at an hour. 1.3 becomes the louder of the two only when there is substantial time in the
20–45° range specifically.

**Backward bending is report-only and is not RAMP.** Our threshold is >5° backward, which is a Wergonic
measure — RAMP folds backward bending into 1.4 at a far larger angle. It must not be coloured with the
1.4 table or labelled as RAMP-aligned. It appears in the report as a separate quantity under its own
name.

**Twist is not measured.** RAMP 1.4 includes torso twisting >30° and side bending; the sensor set
captures neither, so the proxy systematically under-counts 1.4. Documented deviation, not a defect to
fix later.

**Colours only.** Green, yellow and red are the entire output. RAMP's numeric scores are used
internally to select the colour and are not surfaced in the app, the voice, or the report.

**Head, for the record.** Item 1.1 (head forward/side >30°) has a verified table — yellow at 60 min,
red at 120 min — available if you ever want it in the report, but it drives nothing live. Item 1.2
(head backwards) is out: it is the strictest table in the set, yellow at 5 minutes and red at 30, and
too sensitive for feedback.

---

## 2. Arm elevation — RESOLVED

**Source: Lund action levels (AMM Syd 18/2017), elevation relative to vertical.** No RAMP item number
appears anywhere in the arm's report output. Two nested accumulators, ≥30° and ≥60°; time above 60°
also counts toward the 30° band, so the arm holds two colours and the worse speaks.

**Denominator: the full 8-hour working day, 480 minutes.** Lund's percentages are shares of the working
day as measured — whole days, equipment left on, breaks included. Converting them against an
active-time denominator would silently make them stricter than published.

**Reds are Lund's published action levels. Yellows are ours, at half the red onset.**

| Accumulator | Yellow | Red |
|---|---|---|
| **Arm ≥30°** (includes all time above 60°) | 120 min · 25% of shift | 240 min · 50% of shift |
| **Arm ≥60°** | 24 min · 5% of shift | 48 min · 10% of shift |

Red at ≥30° is Lund's median-load level (exposure exceeded more than half the working day); red at ≥60°
is the peak-load level (more than a tenth of the day).

**Why yellow sits at half of red.** RAMP's own duration bands are built that way. Across every item in
or near scope, yellow onset is exactly half of red onset:

| RAMP item | Yellow | Red | Ratio |
|---|---|---|---|
| 1.1 Head forward | 60 min | 120 min | 0.50 |
| 1.3 Trunk moderate | 60 min | 120 min | 0.50 |
| 1.4 Trunk considerable | 30 min | 60 min | 0.50 |
| 1.5 Upper arm | 30 min | 60 min | 0.50 |

So the rule is not invented for the arm — it is RAMP's internal band structure, transferred to a
Lund-sourced item. Applied to the trunk it reproduces RAMP's published values exactly, so nothing is
overridden anywhere and one sentence describes the whole system.

**How to describe yellow in writing.** A coaching band positioned by structural analogy to RAMP's band
spacing. Not an epidemiological claim that risk changes at that point — no one has evidence for a
half-of-action-level threshold. Yellow means *approaching the action level*, never *moderate risk*.
This constrains the voice copy directly.

**Provenance is printed per item in the report**, e.g.:

> Arm ≥60° — red 48 min (AMM Syd 18/2017, peak-load action level, 10% of 8 h day);
> yellow 24 min (Wergonic, half of action level per RAMP band structure).

**Sanity check on the arm's numbers.** Lund's 48-minute red at ≥60° lands close to RAMP 1.5's 60-minute
red, from two independent methods on the same construct. Worth stating in the validation write-up.

**Unsupported arms — an inherited limitation, not a Wergonic one.** RAMP scores time without support;
Lund's 30° level carries the same condition in footnote d. Neither the inclinometer nor RAMP's observer
distinguishes a resting forearm from a held one. Belongs in the deviations list phrased as inherited.

**Elbow angle is a non-question.** Nothing in the arm logic depends on where the hand is, so there is no
elbow assumption to document. The requirement in v1.3 for each variable to declare it does not apply
to the arm.

---

## 3. Synthetic voice and the sentences — RESOLVED

**Yes to TTS**, replacing the nine recorded MP3s per language.

**The voice speaks colour, direction and limb. No numbers.** No minute counts, no percentages. This
removes the ambiguity that would otherwise arise from speaking a projected whole-day figure to a worker
forty minutes into a recording, who would reasonably hear it as time already spent.

*Consequence worth noting:* without live numbers the message set is finite again and could in principle
be pre-recorded. TTS remains the choice — it makes the survey cheap to iterate and keeps localisation
open — but it is now a deliberate choice rather than a technical necessity. If synthetic Swedish sounds
wrong in testing, falling back to recordings is available.

**Wording is written in-house, three alternatives per message in English and Swedish, decided by
survey.**

**Brief for whoever writes them:**
- Yellow means approaching the action level, not moderate risk.
- Green with a rising direction must sound like encouragement, not warning, or the feature nags from
  the first interval.
- Swedish needs a native ergonomics voice, not a translation of the English.

**Limb selection.** The voice reports the worst limb. The other arm may be used for positive feedback
when it has improved. Neither affects the report.

**Still to size before copy is commissioned:** whether the voice names the band (arm ≥30° vs ≥60°,
trunk 1.3 vs 1.4 — four sources) or rolls up per limb and reports the worse of each pair (three
sources); and how many direction states exist (rising / steady / improving). At three limbs × three
colours × three directions × three alternatives, that is 81 sentences per language — worth fixing the
shape first.

---

## 4. How a break is logged — RESOLVED, opposite to the default

**Breaks are not excluded from the count.** Both RAMP and Lund set their thresholds against a whole
working day that includes breaks and non-productive time, and that time is itself recovery — it reduces
risk for the limb. Subtracting it would raise the exposure proportion and make us stricter than either
source intends.

**A break marker silences the voice. It does not stop the clock.** No pause semantics, no exclusion from
the denominator. Break minutes stay in as low-exposure time, contributing exactly the recovery effect
the source instruments assume.

**Dropout remains the only exclusion**, on different grounds: an absent sensor means the posture is
*unknown*, not known to be at rest.

**Document amendment required.** v1.3 defines valid time as elapsed minus logged breaks minus dropout.
It becomes **elapsed minus dropout**. Worth correcting in the document itself, since that line will be
implemented from the spec long after this exchange is forgotten.

---

## 5. What fills the rest of the shift — RESOLVED

**Accumulated feedback is a projection throughout, not a running tally.** The measured proportion of
session time in a posture is scaled onto the 480-minute day and compared against the fixed thresholds.
The recording is treated as representative of the whole workday. Colour reflects estimated whole-day
exposure from the first feedback onwards.

**The denominator is elapsed session time including breaks** — see question 4. Nothing is subtracted
except dropout.

**Accumulated feedback is always whole-session, never per-task.** Work tasks structure the recording;
they do not partition the accumulation.

**The minimum-data guard already exists in settings.** *Accumulated feedback first delay* (typically 5
or 10 minutes, user-adjustable) governs when feedback starts, which prevents the early instability
where two minutes of arm-up at minute four would project to 240 minutes and turn red. Nothing new to
build.

**Task-specific sessions: voice disabled, accumulated feedback still computed** over the whole session.
Only the coaching layer is suppressed.

**Note a conflict to resolve.** v1.3 specifies a ten-minute interval, at most six per hour. The app's
*feedback interval* setting ranges 2–30 minutes with a **default of 5**. At five minutes it is twelve
per hour. This matters for band width: the arm ≥60° yellow band spans 24 minutes of projected exposure,
which at a 5-minute interval gives a few utterances before red and at 30 minutes gives none. The
sentence set should be written for the interval that actually ships.

---

## 6. The report — RESOLVED

**End-of-session accumulated feedback matches the report.** Same numbers, one definition of valid time
across live view and report — elapsed minus dropout, breaks included.

**The report is unchanged by the voice's limb selection.** The voice picks the worst limb and may use
the improved arm for encouragement; the report is not affected by either.

**New metadata on the session and report**, to let a reader interpret what they are looking at:
- whether accumulated feedback was enabled
- whether voice feedback was enabled
- the intervals at which the worker actually received feedback

This matters because a report from a session where the worker was being coached every five minutes
describes a different thing from one where feedback was off.

---

## Still open

| # | Item | Why it matters |
|---|---|---|
| 1 | **Instantaneous vs projected colour.** Does the existing live posture indicator (30–60° yellow, >60° red) coexist with the projected accumulated colour? | If both run, the arm carries two colours simultaneously and the voice needs to know which it reports. |
| 2 | **Voice matrix shape.** Band-level or limb-level; number of direction states. | Determines how many sentences get written and surveyed. |
| 3 | **Feedback interval.** Document says 10 min / max 6 per hour; app default is 5. | Changes how many utterances fit inside a yellow band. |
| 4 | **Labelling of the projection** in app and report. | A projection from a short or task-specific recording must never read as a measured shift. |
| 5 | **Head 1.1 in the report?** | Table is verified and available; drives nothing live. |

---

## Amendments to Feature Description v1.3

1. **Valid time** — remove the subtraction of logged breaks. Elapsed minus dropout.
2. **"RAMP-aligned sensor proxy"** — now applies per body part. Trunk yes; arm is Lund-sourced and
   direct, and must not carry the RAMP label or item numbers.
3. **Per-item threshold storage** — extend to store the *source* per item, not only the table, and print
   it in the report.
4. **Feedback interval** — reconcile the ten-minute figure with the app's 5-minute default.
5. **Elbow-angle assumption** — drop for the arm; no longer applicable.
6. **Deviations list** — add: trunk rotation and side bending not measured (under-counts RAMP 1.4);
   arm support not detectable (inherited from both RAMP and Lund, not introduced by us).

---

## Sources

- RAMP II v1.03b, sheet *1 Postures*, items 1.1–1.5, and the RAMP manual text on item 1.5.
- Arvidsson I, Dahlqvist C, Enquist H, Nordander C. *Åtgärdsnivåer mot belastningsskada.*
  Arbets- och miljömedicin Syd, Report 18/2017, 2017-11-13.
