# Accumulated Feedback — Feature Description

**Status:** Draft v1.3 · 2026-07-31
**Owner:** Wergonic R&D
**Related:** `Mobile App V1.odt` (use cases), `90.6 Ergonomic Methods/RAMP/` (RAMP I & RAMP II)
**Changes in v1.1:** separated the four exposure quantities (§3); corrected the projection formula
(§3.4); demoted the 10/30 % bands from "RAMP equivalent" to training thresholds (§3.6); added the
sensor-proxy section (§3.7); made task scope first-class (§3.3); added confidence states (§4.3);
added the full voice-feedback design (§6); revised cycle handling (§7).
**Changes in v1.2:** separated the screen and voice cadences — the screen is near real-time, only the
voice is gated by *Y* (§4.0); defined what the voice reports when the level changed between ticks
(§4.0.1); added screen dwell (§4.0.2) and the two resolved-excursion message templates (§6.3);
changed the voice tone from command to suggestion and added per-body-part technique phrases (§6.3).
**Changes in v1.3:** added §11 — Coaching Message Libraries, a future feature letting each
organisation's ergonomists author and assign their own message sets per line, task or worker group.

---

## 1. Summary

**Accumulated Feedback continuously measures the exposure a worker has accumulated so far, and
estimates end-of-shift exposure if the observed work pattern continues. For selected
duration-based variables, that estimate is mapped to RAMP-informed risk levels and reported at a
fixed interval by voice and on screen.**

It is a **RAMP-informed Wergonic extension**, not a live implementation of RAMP II. RAMP II also
scores force, repetition, recovery and perceived discomfort, none of which reduce to a percentage
of time, and RAMP defines no method for extrapolating partial-shift sensor data.

---

## 2. Instant vs. Accumulated Feedback

| | **Instant Feedback** | **Accumulated Feedback** |
|---|---|---|
| **Question answered** | "Is my posture bad *right now*?" | "Have I spent *too much time* in a demanding posture?" |
| **Input** | Instantaneous angle / movement sample | Time-integrated exposure over valid measured time |
| **Trigger example** | Upper-arm elevation > 30° | Projected 1 h 40 min with hand at/above shoulder height |
| **Latency** | Sub-second | Screen: near real-time. Voice: every *Y* min after warm-up (§4.0) |
| **Underlying model** | Angle thresholds | RAMP-informed duration bands |
| **Primary channel** | Tactile / vibration (per limb) | Voice + visual |
| **Purpose** | Correct the movement in the moment | Manage cumulative dose across the shift |

```
                Instant                          Accumulated
   angle ┐                            projected ┐
      60°┤   ╭─╮      ╭╮   ╭─╮           4h ────┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  RED
         │  ╱   ╲    ╱  ╲ ╱   ╲                 │            ╭─────────
      30°┤ ╱     ╲──╱    ╳     ╲           1h ──┤ ─ ─ ─ ╭────╯           YELLOW
         │╱       ▲      ▲      ╲               │╭──────╯
         └─────────────────────────► t          └──────────────────────► t
           buzz    buzz   buzz                   ▲     ▲     ▲     ▲
                                                 X    X+Y  X+2Y  X+3Y
```

---

## 3. The four quantities

The single most important correction over v1.0: **"accumulated exposure", "exposure rate",
"projected exposure" and "risk level" are four different quantities.** Only the first is truly
accumulated and can never decrease. Conflating them makes the UI look broken when a colour improves
while measured minutes have not gone down.

| # | Quantity | Symbol | Unit | Monotonic? | Audience |
|---|---|---|---|---|---|
| 1 | **Exposure condition** | `c` | boolean | — | Definition only |
| 2 | **Observed exposure** | `E_v,c(t)` | minutes | ✅ never decreases | Worker + report |
| 3 | **Exposure rate** | `r_v,c(t)` | % of valid time | ❌ can fall | Ergonomist |
| 4 | **Projected daily exposure** | `Ê_v,c,day(t)` | hours | ❌ can fall | Worker + report |
| 5 | **Risk level** | `L_v,c(t)` | 🟢🟡🔴 | ❌ can improve | Everyone |

### 3.1 Exposure condition, not "risk zone"

v1.0 accumulated "time in risk zone green/yellow/red", which was circular — the colours are the
*output*. Replace with:

```
c        : an exposure condition, e.g. "hand at or above shoulder height"
E_v,c(t) : total valid time condition c has been true for body part v
```

Note that Wergonic's *instant* feedback zones are also colour-named (e.g. yellow zone = 30–60°).
Those are **posture zones** and are a separate concept from the **risk level** produced here. The
two must never share a label in the UI or the data model.

### 3.2 Exposure rate

```
                E_v,c(t)
r_v,c(t) =  ──────────────
             T_valid(t)
```

`T_valid` is **valid measured working time in seconds** — elapsed time minus logged breaks minus
periods with no valid sensor sample. Time with a dropped sensor must leave the denominator, not be
counted as low-exposure.

All computation is on **elapsed valid duration, never on sample counts**, so a change of sampling
rate or a partial dropout cannot alter the result.

### 3.3 Scope: session or task

The rate is computed independently at two scopes. These are not competing modes — both run at once.

| Scope | `T_valid` | Question answered | Drives |
|---|---|---|---|
| **Session** | Valid working time since session start | "Where is the whole shift heading?" | Primary risk level, report |
| **Task** *k* | Valid time within the current task | "How demanding is *this* task?" | Secondary indicator, coaching, redesign |

Task scope is the honest answer to a heterogeneous workday, and it is what makes the projection
defensible. It is a first-class calculation, not a mitigation.

### 3.4 Projected daily exposure — additive form

v1.0 used `Ê = r × D` with `T_valid` excluding breaks but `D` = 8 h *including* breaks. **That was
wrong** — it assumes continuous work for the whole shift and systematically overestimates.

Use the additive form: what has already happened, plus a forecast for what remains.

```
Ê_v,c,day(t)  =  E_v,c(t)  +  Σ_k ( r_v,c,k × D_k,remaining )
                 └────────┘     └──────────────────────────┘
                  measured              forecast
```

| Term | Meaning |
|---|---|
| `E_v,c(t)` | Exposure already measured — fixed, never revised downward |
| `r_v,c,k` | Observed rate during task *k* |
| `D_k,remaining` | Planned remaining **active working time** in task *k* (breaks excluded) |

Session-scope fallback when no task plan exists:
`Ê = E_v,c(t) + r_v,c(t) × D_active,remaining`

**Why not simply put breaks in the denominator.** That alternative makes the projection *fall
during a lunch break*, which is the exact confusion §5 of the review warns about. The additive form
avoids it: a break adds nothing to `E`, and only shortens `D_remaining` if it eats into planned
work. Posture during a break is never counted as occupational exposure under either form.

Worked example, task scope:

| Task | Rate above threshold | Planned remaining | Forecast contribution |
|---|---|---|---|
| A — overhead assembly | 40 % | 2.0 h | 0.80 h |
| B — bench work | 5 % | 6.0 h | 0.30 h |
| Already measured | — | — | 0.20 h |
| **Projected day** | | | **1.30 h** 🔴 |

Compare with the naive v1.0 method applied to task A's first 20 minutes: 40 % × 8 h = 3.2 h — an
overestimate by a factor of ~2.5.

### 3.5 Risk level from RAMP-informed bands

`L = threshold-map(Ê_day)`. Colour comes from the **projection**, because a worker can only be
warned in time if the estimate looks ahead; observed minutes are always displayed alongside it so
the two are never confused.

RAMP II item **1.5 — upper arm posture, hand at or above shoulder height** (verified from the RAMP
II user guide, v2015-11-25, p. 10):

| Duration per workday | Score | RAMP colour | % of an 8 h day |
|---|---|---|---|
| < 5 min | 0 | 🟢 Green | < 1.0 % |
| 5 – < 30 min | 1 | 🟢 Green | 1.0 – 6.3 % |
| 30 min – < 1 h | 2 | 🟡 Yellow | 6.3 – 12.5 % |
| 1 – < 2 h | 3 | 🔴 **Red** | 12.5 – 25 % |
| 2 – < 3 h | 5 | 🔴 Red | 25 – 37.5 % |
| 3 – < 4 h | 7 | 🔴 Red | 37.5 – 50 % |
| ≥ 4 h | 10 | 🔴 Red | ≥ 50 % |

**Colour bands are item-specific.** Item 1.6 (hand in/outside the outer work area) shares this score
ladder, but other items do not. The threshold table must be stored per item, never globally.

### 3.6 Two threshold sets — clearly labelled

| Set | Source | Use | Label in UI |
|---|---|---|---|
| **RAMP-informed** | Per-item RAMP II duration bands | Assessment, reporting | "RAMP-informed risk level" |
| **Training thresholds** | Configurable, e.g. 10 % / 30 % | Coaching, technique training | "Training thresholds (custom)" |

The 10 % / 30 % bands proposed in v1.0 **must not be described as RAMP equivalents.** For item 1.5
they are far more permissive: RAMP is already yellow at 30 min (6.3 %) and red at 1 h (12.5 %),
whereas a 30 % boundary corresponds to 2.4 h. They remain useful as deliberately looser coaching
thresholds — but only under an honest label.

### 3.7 Sensor-to-RAMP mapping is a proxy

RAMP II item 1.5 is defined by **hand height** — "hand at or above shoulder height (about
130–150 cm)", assessing "the total time the hand, forearm or upper arm is at or above shoulder
height". Wergonic measures **upper-arm elevation angle**. These are related but not equivalent,
because elbow flexion changes hand height at a constant arm angle.

Every variable must therefore document four layers:

| Layer | Item 1.5 example |
|---|---|
| Sensor-native variable | Upper-arm elevation angle from IMU |
| Derived exposure condition | Estimated hand at/above shoulder height |
| RAMP item approximated | 1.5 Upper arm posture |
| Assumptions / calibration | Subject height, elbow-angle assumption, sensor placement |

Until validated against observation, output must be described as a **RAMP-aligned sensor proxy**.
RAMP II contains no upper-arm-angle item at all — only 1.5 (hand height) and 1.6 (outer work area).

---

## 4. Timing and confidence

### 4.0 Two independent cadences

**The screen and the voice run on different clocks.** This is a defining property of the feature,
not an implementation detail.

| | **Screen** | **Voice** |
|---|---|---|
| Recomputed | Continuously (≈ 1 Hz) | Continuously — but only *spoken* at ticks |
| Updated / spoken | Immediately, near real-time | At *t = X, X+Y, X+2Y, …* |
| Shows | The state **now** | The state **at the tick** |
| Purpose | Live truth for worker and ergonomist | Periodic, non-intrusive intervention |

All four quantities in §3 are evaluated continuously. Only the *announcement* is gated by *Y*.

Consequently the screen can pass through states the voice never mentions:

```
  level ┐
    RED ┤          ╭───────────╮
        │          │           │
 YELLOW ┤   ╭──────╯           ╰────────────────
        │   │
  GREEN ┤───╯
        └───┬──────┬────────────┬──────────┬────► t
            X     X+2          X+6        X+Y
         first   screen      screen      voice speaks:
         voice   turns RED   back to     state is YELLOW
                 (no voice)  YELLOW      — not RED
```

This is intended. The screen is the live instrument; the voice is a periodic intervention that
would become nagging if it fired on every excursion.

### 4.0.1 What the voice reports at a tick

The announcement states the **current** level — but the **inter-tick history** classifies the event.
This converts the timing mismatch into the most valuable message type available:

| Level at last tick | Peak between ticks | Level at this tick | Event | Voice |
|---|---|---|---|---|
| 🟡 | 🔴 | 🟡 | **IMPROVED** | "Right arm was red, now back to yellow. Good." |
| 🟢 | 🟡 | 🟢 | **IMPROVED** | "Good — right arm settled back down." |
| 🟡 | 🔴 | 🔴 | WORSENED | Red, new |
| 🟡 | 🟡 | 🟡 | SUSTAINED | Yellow, sustained |

Rules:
- **Never announce a level the worker is no longer in.** Warning about a resolved excursion trains
  people to distrust the voice.
- **A resolved excursion is praise, not silence.** It is the clearest evidence the worker corrected
  something, and under §6.4 improvement messages always speak.
- The peak between ticks is always written to the session record even when it is never spoken.

### 4.0.2 Screen flicker

Because the projection is volatile early in a session, the raw level can oscillate on a threshold
boundary. Apply a light dwell to the *displayed* colour — it must hold for ≥ 5 s before the display
follows — and show a trend arrow (↑ ↓ →) rather than letting the badge flap. Dwell affects display
only; the underlying value and the session record are never smoothed.

### 4.1 Settings

| Setting | Symbol | Purpose | Default |
|---|---|---|---|
| Warm-up — session | *X* | Valid working time before first **voice** announcement | 10 min |
| Voice interval | *Y* | Announcement cadence | 10 min |
| Screen evaluation rate | — | Recompute + display refresh | 1 Hz |
| Screen colour dwell | — | Minimum hold before display follows a level change | 5 s |
| Warm-up — task, time | *X_t* | Minimum valid task time | 2 min |
| Warm-up — task, cycles | *N_c* | Minimum completed cycles, when detectable | 3 |
| Planned shift / active time | `D` | Horizon for the projection | 8 h / 7 h |

### 4.2 Task warm-up is a dual criterion

A fixed number of minutes is the wrong gate. Require **both** a minimum valid duration **and** a
minimum number of completed cycles where cycles are detectable — two minutes is plenty for a
20-second cycle and meaningless for a 15-minute task. For very short tasks, report **after task
completion** rather than mid-task.

### 4.3 Confidence states

| State | Condition | Screen | Voice |
|---|---|---|---|
| **Collecting** | Below warm-up thresholds | Grey, no colour | Silent |
| **Provisional** | Warm-up met | Colour + "provisional" | Hedged wording; no red escalation |
| **Stable** | ≥ 3×*X* valid time or ≥ 10 cycles, and rate change < 5 pp over last two ticks | Colour, no qualifier | Full ladder |

```
 session
 start        warm-up X            Y         Y         Y
   │◄──────────────────────►│◄───────►│◄───────►│◄───────►│
   ├────────────────────────┼─────────┼─────────┼─────────┼──►  t
   │      COLLECTING        │   PROVISIONAL     │      STABLE
   │      grey · silent     │   hedged voice    │   full voice ladder
   │◄── instant feedback active throughout (independent) ──────►
```

Breaks do not advance the *Y* counter, so no announcement lands during a break.

---

## 5. On-screen presentation

Show the measured and the projected value together, always. This is what prevents "the colour got
better but I haven't done anything" confusion.

```
┌──────────────────────────────────────────┐
│  RIGHT UPPER ARM                🟡 YELLOW│
│                                           │
│  Measured so far      18 min             │
│  Rate, current task   45 %               │
│  Projected day        1 h 35 min         │
│                                           │
│  Confidence  ●●○  provisional            │
└──────────────────────────────────────────┘
```

| Indicator | Basis | Audience |
|---|---|---|
| **Primary colour** | Projected shift exposure (additive form) | Worker |
| **Secondary task indicator** | Current-task rate and colour | Worker + ergonomist |
| **Analyst metric** | Active-work rate, breaks excluded | Ergonomist, report |

---

## 6. Voice feedback design

### 6.1 Governing principles

| # | Principle | Rationale |
|---|---|---|
| 1 | **One message per interval — never two** | Stacked warnings are unusable by voice and read as nagging |
| 2 | **One subject: the highest-risk body part** | Method-consistent — RAMP itself scores only the arm/hand with the highest score ("only the arm with the highest score is used") |
| 3 | **Positive feedback is earned, not filler** | Praise for an actual improvement carries weight; a periodic "all good" becomes noise |
| 4 | **Never more than 2 consecutive corrective messages** | The third must escalate to a concrete remedy or fall silent |
| 5 | **Quote measured minutes, not percentages** | Minutes never decrease — no "why did it go down?" confusion by voice |
| 6 | **≤ 12 words, ~4 seconds** | Anything longer is not heard on a shop floor |
| 7 | **Every corrective message ends in a technique suggestion** | "Try to raise your arm less" beats "your arm is too high" |
| 8 | **Suggest, never command** | "Try to …" / "See if you can …" — an order the worker cannot obey is heard as blame. No urgency words; this risk is cumulative over hours, never urgent by the second |

### 6.2 Selection algorithm

```
at each tick (t = X, X+Y, X+2Y, …):

  if on break OR data invalid OR confidence = Collecting      → SILENT
  if a vibration alert fired in the last 10 s                 → defer 10 s

  candidates ← body parts with confidence ≥ Provisional
  if left and right of a pair are the same level
     and their rates differ by < 10 pp                        → merge into "both arms"

  subject ← max by (risk level, then projected exposure, then fixed priority order)

  # level_now drives WHAT is said; the inter-tick peak drives HOW it is framed (§4.0.1)
  if   level_now > level_at_last_tick                 → event ← WORSENED
  elif peak_since_last_tick > level_now               → event ← IMPROVED
  elif level_now < level_at_last_tick                 → event ← IMPROVED
  elif level_now = GREEN                              → event ← STABLE_GREEN
  else                                                → event ← SUSTAINED

  if event = STABLE_GREEN and a green message was spoken in the last 3 ticks → SILENT
  if corrective_streak ≥ 2 and event ≠ IMPROVED                → use ESCALATED template

  speak exactly one template; update streak counters
```

Fixed priority order for ties (worst consequence first): back → neck → right arm → left arm.

### 6.3 Message templates

Anatomy: **Subject → State → Evidence → Suggestion.** Evidence and suggestion may be dropped to stay
inside the word budget; subject and state never are.

**Tone: suggestion, not command.** The voice is a coach, not a supervisor. Corrective messages are
phrased as *"try to …"* or *"see if you can …"*, and they point at **technique** rather than at the
person. Never *"lower your work now"* — the worker usually knows the posture is awkward and often
cannot change it instantly; an order they cannot obey is heard as blame. Urgency words ("now",
"immediately", "stop") are reserved for nothing at all in this feature: the risk being managed is
cumulative over hours, so nothing is ever urgent by the second.

#### 🔴 Red

| Event | Template | Example |
|---|---|---|
| New red | `{part}. {evidence}. Try to {technique}.` | "Right arm. Quite a lot of time above shoulder. Try to raise your arm less." |
| Sustained (2nd) | `{part} still high — {minutes}. See if you can {technique}.` | "Right arm still high — 35 minutes. See if you can bring the work lower." |
| Sustained (3rd+) — **escalated** | `{part} could use a rest. Maybe {recovery}.` | "Right arm could use a rest. Maybe a short break, or switch task." |
| Both sides | — | "Both arms are high. Try keeping the work closer to elbow height." |

#### 🟡 Yellow

| Event | Template | Example |
|---|---|---|
| New yellow (from green) | `{part} is climbing. Try to {technique}.` | "Right arm is climbing. Try to raise your arm a bit less." |
| Sustained yellow | `{part} still up — {minutes}. Try to {technique} when you can.` | "Right arm still up — 20 minutes. Try working a bit lower when you can." |
| **Improved** from red | `Better — {part} is down to yellow. Keep going.` | — |
| **Excursion resolved** — red between ticks, yellow now | `{part} was red, now back to yellow. Good.` | — |

#### Technique phrases by body part

The `{technique}` slot is a per-variable phrase, written by an ergonomist — not a generic
"reduce your exposure".

| Body part / condition | Technique phrase | Recovery phrase |
|---|---|---|
| Upper arm — above shoulder height | "raise your arm less" / "bring the work lower" | "a short break, or switch task" |
| Upper arm — outside work area | "keep the work closer to your body" | "reposition the bin or fixture" |
| Back — forward bending | "bend less, and lift more with your legs" | "a few upright steps" |
| Back — twisting | "turn your feet instead of twisting" | "reposition so you face the work" |
| Neck — forward / down | "bring the work up towards eye level" | "look up and around for a moment" |
| Wrist — bent | "keep your wrist straighter" | "shake the hands out" |

#### 🟢 Green

| Event | Template | Example |
|---|---|---|
| **Recovery** — first green after yellow/red | `Good — {part} is back in the green.` | "Good — right arm is back in the green." |
| **Excursion resolved** — yellow/red between ticks, green now | `Good — {part} settled back down.` | — |
| Sustained green (max every 3rd tick) | `Nice work. Everything is on track.` | — |
| All green from session start | *silent* — nothing has been earned yet | — |

#### Confidence hedging (Provisional only)

| Level | Hedged form |
|---|---|
| Red | Downgrade to heads-up: "Early reading — right arm looks high. Worth watching." |
| Yellow | "Early reading — right arm is trending up." |
| Green | Silent |

### 6.4 Positive-feedback budget

The corrective/positive balance is enforced, not left to chance:

| Rule | Value |
|---|---|
| Max consecutive corrective messages before escalation-or-silence | 2 |
| Minimum interval between "sustained green" confirmations | 3 ticks |
| Improvement messages | Always spoken, never suppressed — highest-value event |
| Max voice messages per hour | 6 (cap, configurable) |

**Improvement is the only event that always speaks.** If a worker corrects a posture and hears
nothing, the feedback loop is broken; if they hear a warning three times running, they stop
listening.

### 6.5 Wording rules

| Do | Don't |
|---|---|
| "Try to raise your arm less" | "Lower your work now" — a command the worker may be unable to obey |
| "See if you can bring the work lower" | "Stop", "immediately", "you must" |
| "Try bending less, and lift more with your legs" | "Reduce your exposure", "your posture is wrong" |
| "Right arm", "lower back", "neck" | "Upper arm elevation variable", "segment 3" |
| Name the **technique** to change | Name the **person** as the problem |
| Vary phrasing from a per-slot pool | Repeat the identical sentence every 10 min |
| Same voice, same speaking rate throughout | Signal urgency by tone or volume |

### 6.6 Channel separation

| Channel | Carries |
|---|---|
| **Vibration** | Instant posture only — per limb, distinct yellow/red patterns |
| **Voice** | Accumulated state only |
| **Screen** | Both, with all four quantities visible |

Never let both fire within 10 seconds — the worker cannot attribute two simultaneous signals to two
different causes.

---

## 7. Cycle handling

Do **not** drive feedback from the current or last single cycle — one abnormal cycle would dominate.

| Statistic | Use |
|---|---|
| Rolling mean over the last *N* cycles (default *N* = 5) | Drives task-scope colour |
| Cumulative mean for the current task | Task summary, report |
| Last completed cycle | Display only, explicitly labelled |
| Recent *N* vs. earlier task mean | Trend arrow |

**The session accumulator continues across cycles and tasks** even when the task or cycle display
resets. Resetting the display must never reset `E_v,c`.

---

## 8. Settings summary

| Setting | Type | Default |
|---|---|---|
| Accumulated feedback | on / off | off |
| Warm-up *X* (session) | minutes | 10 |
| Update interval *Y* | minutes | 10 |
| Task warm-up — time / cycles | minutes / count | 2 / 3 |
| Planned shift `D` / active time | hours | 8 / 7 |
| Threshold set | RAMP-informed / training / custom | RAMP-informed |
| Per-item threshold table | duration bands | per RAMP II item |
| Primary colour source | projected / observed | projected |
| Voice feedback | on / off | on |
| Sustained-green confirmations | on / off | on |
| Max voice messages per hour | count | 6 |
| Rolling cycle window *N* | count | 5 |

---

## 9. Open questions

| # | Question | Notes |
|---|---|---|
| 1 | Which variables ship in v1, and their per-item threshold tables | Not yet decided |
| 2 | Validation of the arm-angle → hand-height proxy | Required before calling any output RAMP-informed (§3.7) |
| 3 | Source of `D_k,remaining` | Needs a task plan or shift schedule; fall back to session scope if absent |
| 4 | Automatic task segmentation vs. manual logging | Task scope is only as good as the segmentation |
| 5 | Per-limb vs. worst-limb in the **report** | RAMP uses worst-limb; the report may want both |
| 6 | Reconciliation with the end-of-session report | Break handling and denominators must match exactly |
| 7 | Voice message pool — final wording and localisation | Swedish and English at minimum |

---

## 10. Relation to the documented use cases

From `Mobile App V1.odt`:

| Use case | Accumulated feedback role |
|---|---|
| Risk Assessment (no feedback) | Not active — computed post hoc in the report only |
| Risk Assessment + Coaching | Active, visual; ergonomist uses it as a live coaching aid |
| Work-Technique Training — voice | **Primary mechanism** — see §6 |
| Work-Technique Training — tactile | Not used; vibration stays instant-only |

---

## 11. Future feature — Coaching Message Libraries

> **Status: future scope. Not part of the first release.** v1 ships a single Wergonic-authored
> message set (§6.3). This section describes how that becomes customer-editable.

### 11.1 Problem

The technique phrases in §6.3 are written for generic manual handling. They will be wrong, or simply
odd, in most real deployments:

| Setting | Why the default phrasing fails |
|---|---|
| Automotive assembly line | "Bring the work lower" is meaningless — the car body height is fixed; the real advice is "use the lift table" |
| Warehouse picking | The relevant remedy is pick-face height and pallet position, not arm angle |
| Healthcare / patient transfer | Lifting technique advice differs completely and is governed by local protocol |
| Food processing | Hygiene rules constrain which postures are even available |
| Non-English site | Voice must be in the worker's language, with local terms for equipment |

Only the customer's own ergonomist knows the right sentence. The product should carry the *structure*
of good feedback and let them supply the *content*.

### 11.2 Concept

A **Coaching Message Library** is a named, versioned, reviewable collection of message content that
an organisation's ergonomist authors and assigns to specific work.

```
   Wergonic baseline library  (shipped, read-only)
            │  fork / inherit
            ▼
   Organisation library        "Volvo Torslanda — general"
            │
            ├── Site / line library      "Line 4 — final assembly"
            │        │
            │        └── Task library     "Underbody bolting"
            └── Training library          "New-starter onboarding"
```

Resolution is **most-specific-wins with inheritance**: any slot a child library does not define
falls through to its parent, and ultimately to the Wergonic baseline. A partial library is therefore
always safe to publish — it can never leave a message slot empty.

### 11.3 What is editable — and what is not

The separation matters. Message libraries change **what is said**, never **what is measured**.

| Editable by the org ergonomist | Fixed by the product |
|---|---|
| Technique phrases per body part / condition | Risk thresholds and RAMP band tables |
| Evidence phrasing ("35 minutes" vs "over half an hour") | The selection algorithm (§6.2) |
| Praise and recovery phrasing | One-message-per-interval rule |
| Escalation wording | Worst-body-part-only rule |
| Body-part names and local equipment terms | Positive-feedback budget floors (§6.4) |
| Locale and voice | Confidence gating |
| Optional extra message variants for variation | Channel separation (§6.6) |

**Rationale:** if customers could edit thresholds through the message layer, two sites would report
"red" for different exposures and the data would stop being comparable. If they could edit the
selection rules, they could re-enable simultaneous warnings — the exact failure mode §6.1 exists to
prevent. Thresholds remain a separate, separately governed artefact (§3.6).

### 11.4 Content model

A library is a set of **slots**, each holding a **pool** of one or more phrasings. The engine picks
from the pool at random-without-repeat, which is what gives natural variation over a shift.

| Slot | Example pool entry | Required |
|---|---|---|
| `part.{id}` | "right arm", "höger arm" | ✅ |
| `technique.{condition}` | "use the lift table", "try to raise your arm less" | ✅ |
| `recovery.{condition}` | "swap to the sub-assembly bench for a while" | ✅ |
| `evidence.{level}` | "quite a lot of time above shoulder" | ✅ |
| `praise.improved` | "nice — that's better", "good, that helped" | ✅ (≥ 2 entries) |
| `praise.sustained_green` | "all looking good" | ✅ |
| `escalation.{condition}` | "worth a word with your team leader about the fixture height" | optional |

Every message the engine can emit must resolve. Publishing is blocked while any required slot is
unresolved anywhere in the inheritance chain.

### 11.5 Authoring guardrails

The editor validates on save. These encode §6.1 and §6.5 so a customer cannot accidentally build a
nagging or blaming voice.

| Check | Rule | Severity |
|---|---|---|
| Length | Rendered message ≤ 12 words **and** ≤ 4.0 s measured at the configured TTS rate | ❌ Block |
| Imperative / urgency | Flags "now", "immediately", "stop", "you must", bare imperatives | ⚠️ Warn |
| Blame | Flags second-person fault constructions ("you are doing it wrong") | ❌ Block |
| Positive coverage | `praise.improved` must have ≥ 2 entries | ❌ Block |
| Slot coverage | All required slots resolve through the chain | ❌ Block |
| Medical claims | Flags diagnosis or injury-prediction language | ❌ Block |
| Personal data | Message text must contain no names or worker IDs | ❌ Block |
| Duplicate pool entries | Identical phrasings within one pool | ⚠️ Warn |

Length is validated on **measured TTS duration**, not word count — a compound Swedish or German noun
can blow the budget at eight words.

### 11.6 Lifecycle and governance

```
  Draft ──► In review ──► Published ──► Superseded
    ▲           │             │
    └───────────┘             └──► Rolled back (one click, to any prior version)
```

| Role | Can |
|---|---|
| **Org ergonomist (author)** | Create and edit drafts, run previews and dry-runs |
| **Org ergonomist (approver)** | Publish, assign to work, roll back |
| **Wergonic admin** | Maintain the baseline library; cannot see customer libraries |
| **Worker** | Nothing — libraries are never worker-editable |

Every published version is immutable and stamped with author, approver, and timestamp. **Each
session records the library ID and version that was active**, so a report from eighteen months ago
can still be explained.

### 11.7 Assignment

A library is bound to work, not to a device.

| Assignment scope | Example | Precedence |
|---|---|---|
| Organisation | Default for all sites | lowest |
| Site / production line | "Line 4 — final assembly" | ↓ |
| Work task template | "Underbody bolting" | ↓ |
| Worker group | "New starters — first 4 weeks" | ↓ |
| Session override | Ergonomist picks a library when starting a session | highest |

Task-scope assignment pairs naturally with the task segmentation in §3.3: when the worker moves from
task A to task B, the library can change with it, so the advice matches the work actually being done.

### 11.8 Testing before it reaches a worker

Three levels, in increasing confidence:

| Tool | What it does |
|---|---|
| **Preview** | Plays any single message through the configured TTS voice, in the target locale |
| **Dry-run** | Replays a recorded session against the draft library and lists every message that *would* have been spoken, with timestamps — no worker involved |
| **Shadow mode** | Runs the draft live alongside the published library, logging what it would have said without speaking it |

Dry-run against a real recorded session is the important one: it exposes nagging, repetition and
bad phrasing before anyone hears it.

### 11.9 Effectiveness analytics

Because every message is logged with its library version, the obvious question becomes answerable:
**did saying this actually change anything?**

| Metric | Definition |
|---|---|
| **Response rate** | Share of messages after which the subject's exposure rate fell over the next 10 min |
| **Message effectiveness** | Response rate per individual phrase, ranked |
| **Habituation curve** | Response rate as a function of how many times a worker has heard that phrase |
| **Nag index** | Corrective messages per hour, and consecutive-corrective streaks |
| **Silence share** | Share of ticks that produced no message — a health indicator, not a failure |

This closes the loop: ergonomists can retire phrases that never work and promote those that do.
Habituation in particular is worth measuring — it is the strongest argument for maintaining variant
pools rather than a single fixed sentence per slot.

### 11.10 Starter libraries

Wergonic curates baseline libraries per sector — assembly, warehouse and logistics, sorting, food
processing, healthcare — which customers fork rather than start from an empty editor. Libraries can
be exported and imported between an organisation's own sites. **Sharing between organisations is
off by default**, since phrasing can encode confidential process detail.

### 11.11 Phasing

| Phase | Scope | Depends on |
|---|---|---|
| **A** | Org-level override of `technique` and `recovery` phrases only; single locale; no approval workflow | §6 shipped |
| **B** | Full slot model, inheritance, guardrails, versioning, approval, preview + dry-run | A |
| **C** | Site / line / task / group assignment, multi-locale, shadow mode | B, task segmentation (§3.3) |
| **D** | Effectiveness analytics, curated sector libraries | C, message logging |

Phase A alone removes most of the pain in §11.1 and is small. It is the right first cut.

### 11.12 Open questions

| # | Question |
|---|---|
| 1 | Does the library also govern **on-screen** text, or voice only? Screen text has a different length budget and no TTS cost |
| 2 | Should a library be able to *disable* a body part's messages entirely (e.g. wrist not relevant on this line), or only rephrase them? |
| 3 | Offline behaviour — the device must cache the assigned library and its version, and must refuse to fall back silently to the baseline mid-session |
| 4 | Who owns translation quality? A poor translation is worse than English for safety-adjacent content |
| 5 | Does the ergonomist need a per-phrase "do not vary" flag for phrases mandated by a local safety protocol? |
