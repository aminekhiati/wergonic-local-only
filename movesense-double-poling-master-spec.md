# Movesense Double-Poling Trainer — Master Specification and Implementation Plan

**Version:** 1.0 (consolidating system design v1, development plan v1, and coaching prompt package v1)
**Status:** approved for build, Phase 0 pending
**Supersedes:** the three source documents as the single authoritative reference. Where they disagreed, the resolution is recorded in §0.3.

---

## 0. How to read this document

### 0.1 Document map

| Part | Sections | Audience |
|---|---|---|
| **I — What and why** | 1–2 | Everyone. Aim, scope, architecture. |
| **II — Measurement** | 3–9 | Signal processing, embedded. Sensors through per-cycle features. |
| **III — Interpretation** | 10–14 | Analysis, ML. Bands, live feedback, report, descriptor, coaching. |
| **IV — Product** | 15–17 | Mobile, design. Screens, data model, engineering practice. |
| **V — Programme** | 18–24 | Lead, research, advisory. Studies, regulatory, phases, risk. |

Sections 3–14 are the *specification*: they define behaviour precisely enough to implement and test. Sections 18–24 are the *plan*: sequencing, gates, and evidence requirements. Appendix A is the single unified threshold table — every number that gates a behaviour appears there and nowhere else as an authoritative value.

### 0.2 Governing principle

**Numbers in code, language in the model.** Every metric is computed and evaluated deterministically against a versioned configuration. The language model receives already-evaluated results, and its only jobs are phrasing, mechanism explanation, and continuity. It never computes, never chooses a threshold, and — after the revisions in §0.3 — never even sees a number that failed a quality gate.

A second principle follows from it: **the product must be able to run with the model switched off.** The deterministic report is complete on its own. The coaching layer is an enhancement with a fallback, not a dependency.

### 0.3 Resolved conflicts between source documents

| Conflict | Resolution | Rationale |
|---|---|---|
| Sync suppression threshold given as both 5 ms and 8 ms | **5 ms**, single value in config (`sync.max_residual_ms`) | Two thresholds for one condition guarantees divergence between the analysis layer and the prompt. |
| Priority-focus selection described as a model responsibility (prompt package §1) and a code responsibility (plan §4) | **Code-side.** Descriptor carries `priority_focus_fault`; the model phrases it. | Selection is a deterministic cascade with a tie-break. There is no reason to expose it to sampling variance. |
| Unreliable metrics "not commented on" by the model vs omitted from the descriptor | **Structurally omitted.** Suppressed metrics are listed by name in `suppressed_due_to_quality` with no values. | A constraint the model can violate is weaker than a number it never receives. |
| Model size "8–30B is sufficient" vs local-inference ambition | **Split target.** v1 server-side 8–30B class; v2 on-device 3–8B quantised, decided at Gate G5. | Ships now, keeps the GDPR-simplifying option open on evidence rather than aspiration. |
| Coaching scope during escalation left implicit | **`coaching_scope ∈ {full, conservative}`** in the descriptor; conservative drops `cue` and `drill` from the required schema. | Prevents the model from prescribing training on top of a "get this checked" card. |
| Continuity phrased from `previous_cue` text | **`previous_cue_outcome ∈ {improved, unchanged, worsened, not_measurable}`**, computed from the metric the cue targeted. | Otherwise continuity is a plausible-sounding guess about something the system can actually measure. |
| Adoption evaluated as raw change session *n* → *n+1* | **Within-athlete contrast:** change in the cued metric minus mean change in non-cued flagged metrics. | Removes regression to the mean. Suppressed faults supply the control set at no cost. |

---

# PART I — WHAT AND WHY

## 1. Aim and scope

### 1.1 Product aim

**A four-sensor Movesense system that measures double-poling technique well enough to show three trustworthy signals live, produce an honest after-session report, and deliver one grounded coaching cue per session.**

Each clause is load-bearing:

- *Four sensors* — donning time is the retention constraint, not measurement richness. Three minutes to dressed is the budget.
- *Three signals live* — the attention ceiling at threshold intensity, from the motor-learning literature, not a UI preference.
- *Honest* — every number is either defensible or visibly absent. A greyed-out metric with a stated reason builds more trust than a confident wrong one.
- *One cue* — an athlete given five cues adopts zero.

Everything else — more sensors, more techniques, richer feedback, coach dashboards — is an extension of a working core, not part of it.

### 1.2 Who it is for

Primary: the self-coached recreational-to-trained cross-country skier training double poling on an ergometer (stakmaskin/SkiErg), 2–5 sessions a week, Swedish or English speaking, who has no access to a technique coach and cannot see their own trunk.

Secondary (v1 supports, does not optimise for): a coach standing beside the machine; a club athlete whose coach reviews exported sessions.

Explicitly not the user: a patient in rehabilitation. See §19.

### 1.3 What the product promises, and what it does not

**Promises.** Trunk posture and lumbar loading pattern measured with published error bars; pole plant and release timing accurate to a stated tolerance; left–right symmetry with its uncertainty shown alongside; a report that distinguishes "your technique changed" from "the sensor slipped"; one actionable cue traceable through an auditable chain to a measured fault.

**Does not promise.** Injury prevention. Diagnosis. Treatment. Elbow joint angle in Tier A. Reliable skate-technique analysis. Anything on snow beyond passive recording in v1.

### 1.4 v1 scope boundary

| In | Out (v1) |
|---|---|
| Ergometer double poling (stakmaskin) | On-snow and roller-ski modes beyond passive recording |
| Tier A, 4 sensors, 52 Hz, IMU6 | Tier B/C sensor sets |
| Host-side Mahony | On-device fusion |
| Deterministic 8-section report | Technique auto-classification (rule-based logging only) |
| Live three-signal display + audio cues | Coach tablet view |
| LLM coaching with validator + fallback | Any injury-prevention or rehabilitation claim |
| Swedish and English | Further localisation |
| On-device storage, opt-in export | Multi-athlete cloud accounts, team features |

### 1.5 Definition of done for v1

An athlete can put on four sensors in under three minutes, pass calibration with clear feedback when they do not, train with three signals they can decode at intensity, and finish to a report where every number is defensible, every unreliable number is visibly absent, and the single coaching cue traces to a measured fault through an auditable chain — with a fixed, human-written safety net rendered above it all when the data says a professional should look.

Measurable form of the same statement, as acceptance criteria:

| Criterion | Target |
|---|---|
| Median donning + calibration time, experienced user | < 3:00 |
| Calibration first-pass rate, sessions 3+ | > 85% |
| Session capture completion (no data loss) | > 98% |
| Cross-sensor sync residual, 40-minute session | < 5 ms |
| Trunk / lumbo-pelvic angle RMSE vs mocap | < 5° (fallback rule at > 8°, §18) |
| Plant/release timing error | < ±10 ms |
| Validator rejection rate, steady state | < 2% |
| Clinical-language escapes | 0 |
| Live-signal comprehension in post-session interview | 3/3 signals correctly recalled by > 80% of pilot athletes |

### 1.6 Design principles

**Low sample rate is a hard budget, not a preference.** At 26–52 Hz, joint-angle *waveforms* reconstruct faithfully; *event timing* is the bottleneck. The system therefore puts primary metrics on angle estimates and recovers event timing by sub-sample interpolation rather than raw sampling resolution.

**Accelerometers are unreliable exactly when the movement matters most.** Pole plant produces multi-g transients. A naïve Mahony filter chases them and corrupts pitch precisely during the drive. Adaptive gain gating is a correctness condition, not an optimisation.

**Magnetometers are unreliable in the environment this app lives in.** A steel-framed ergometer in a gym is magnetically hostile, and the resulting heading error is *correlated with the movement itself* — the failure mode most easily mistaken for real technique variation. The system runs 6-DOF and treats heading as calibrated and drift-corrected, never measured.

**The athlete cannot process rich feedback at threshold.** Live display carries three signals. Everything else is terminal.

**Absence is a feature.** Any metric whose supporting data failed a quality gate is removed and named, not estimated. This is what makes the numbers that *do* appear worth believing.

---

## 2. System architecture

### 2.1 Pipeline

```
  4× Movesense                  Phone (host)                        Optional server
 ┌──────────────┐   BLE      ┌────────────────────────────────┐   ┌──────────────────┐
 │ S1 sternum   │──IMU6/52──▶│ L1  Transport & capture        │   │  LLM inference   │
 │    HR, RR    │──HR/RR────▶│     · per-sensor ring buffers  │   │  (pseudonymised  │
 │ S2 sacrum    │──IMU6/52──▶│     · clock model + sync tap   │   │   descriptor)    │
 │ S3 L forearm │──IMU6/52──▶│     · logbook reconciliation   │   └────────▲─────────┘
 │ S4 R forearm │──IMU6/52──▶│                                │            │
 │              │            │ L2  Orientation (Mahony)       │            │
 │ DataLogger   │◀─backfill──│     · adaptive Kp/Ki gating    │            │
 └──────────────┘            │     · functional-frame angles  │            │
                             │                                │            │
                             │ L3  Events & cycles            │            │
                             │     · 4-state machine / side   │            │
                             │     · sub-sample plant timing  │            │
                             │                                │            │
                             │ L4  Per-cycle features         │            │
                             │                                │            │
                             │ L5  Session aggregation        │            │
                             │     · quality gates            │            │
                             │     · fault engine             │            │
                             │     · baselines                │            │
                             │                                │            │
                             │ L6  Descriptor builder ────────┼────────────┘
                             │     · suppression              │            │
                             │     · priority cascade         │◀───JSON────┘
                             │     · coaching scope           │
                             │                                │
                             │ L7  Presentation               │
                             │     · live view (from L2/L3)   │
                             │     · report (from L5)         │
                             │     · coaching card (L6 + LLM) │
                             │     · validator + fallback     │
                             └────────────────────────────────┘
```

Live view is driven from L2/L3 with a hard latency budget (§11.2). Everything else runs post-session, unhurried.

### 2.2 The determinism boundary

The boundary sits between L6 and the model. Above it: measurement, evaluation, ranking, suppression, escalation — all deterministic, all versioned, all unit-tested. Below it: word choice.

Three structural defences enforce it, in order of strength:

1. **Structural suppression** — unreliable numbers are not in the descriptor. Cannot be discussed because they are not present.
2. **Code-side priority and escalation** — the model is told which fault to discuss and in which scope. It cannot promote, demote, or editorialise around an escalation it is not shown.
3. **Post-generation validation** — per-field numeric provenance, cardinality, hedging, clinical-language screen. Two failures fall back to the deterministic template.

### 2.3 Module inventory

| ID | Module | Responsibility | Pure? | Test strategy |
|---|---|---|---|---|
| M1 | `transport` | BLE lifecycle, subscriptions, reconnect, logbook fetch | No | Device matrix, fault injection |
| M2 | `timesync` | Clock model, tap fiducials, residual estimate | Yes | Golden traces + synthetic skew |
| M3 | `calibration` | 5-step protocol, pass/fail, calibration object | Yes | Recorded human sessions (n ≥ 5) |
| M4 | `orientation` | Mahony, adaptive gating, yaw anchoring, angles | Yes | Mocap-referenced replay |
| M5 | `events` | State machine, plant/release, cycle rejection | Yes | Force-referenced replay |
| M6 | `features` | Per-cycle feature extraction | Yes | Property + golden |
| M7 | `session` | Aggregation, thirds, ensemble curves, quality gates | Yes | Golden sessions |
| M8 | `faults` | Fault rule engine, ranking | Yes | Table-driven unit tests |
| M9 | `bands` | Versioned reference config loader | Yes | Schema validation |
| M10 | `descriptor` | Suppression, priority cascade, continuity, scope | Yes | Exhaustive path coverage |
| M11 | `coach` | Prompt assembly, inference call, validator, fallback | No (I/O) | Eval harness + adversarial set |
| M12 | `report` | Deterministic 8-section renderer, export | Yes | Snapshot tests |
| M13 | `live` | Three-signal view, audio cue scheduler | No | Manual + latency instrumentation |
| M14 | `store` | Local DB, retention, export, deletion | No | Migration tests |

"Pure?" matters: M2–M10 and M12 are deterministic functions over recorded input, which means the entire analysis chain is replayable from a raw archive. Build that replay harness in Phase 0 — it is what makes every later change safe.

### 2.4 Deployment topology

- **Default:** everything on the phone. Sessions never leave the device unless the athlete exports them.
- **Coaching inference (v1):** pseudonymised descriptor (2–5 kB, no raw signals, no name, opaque athlete key) to a server-side model. Disclosed in-app; disable-able in settings, in which case the deterministic template renders instead.
- **Coaching inference (v2 candidate):** 3–8B quantised model on-device. Decided at Gate G5 on pilot quality data with the DPIA on the table.
- **No account required for v1.** Optional export to file or a shareable session link generated on demand.

---

# PART II — MEASUREMENT

## 3. Sensors and placement

### 3.1 Tier A — core configuration (4 sensors, the shipping default)

| # | Site | Exact placement | Signals delivered |
|---|---|---|---|
| S1 | **Sternum** | Movesense HR+ in ECG chest belt, sensor at mid-sternum / xiphoid level, longitudinal axis superior–inferior | Thorax orientation, HR, RR intervals, ECG (optional), cadence–HR coupling |
| S2 | **Sacrum** | Over S1–S2, midline, narrow elastic waist belt or taped; no soft-tissue slack | Pelvis orientation → lumbo-pelvic angle (svank detection) |
| S3 | **Left forearm** | Dorsal surface, ~⅓ distal from elbow, over the ulnar border | Arm sweep, plant/release events, drive angular velocity |
| S4 | **Right forearm** | Mirror of S3 | As S3 |

**Delivers:** trunk-to-vertical angle and ROM, lumbar flexion/extension, plant and release timing, cycle rate, relative poling time, poling:recovery ratio, arm drive angular velocity, the complete left–right symmetry set, HR and HRV.

**Does not deliver:** true elbow flexion angle — that needs two segments spanning the joint. This is the one significant loss, and it is worth stating plainly because the literature identifies elbow *timing and angular velocity*, not elbow ROM, as the skill discriminator. Forearm angular velocity proxies the discriminating variable without the joint angle itself.

**Why forearm rather than upper arm** at one sensor per side: the plant impulse transmits hand → forearm with the sharpest jerk signature, giving the cleanest event detection; and the forearm sweeps a much larger angular range, giving better SNR for phase segmentation.

### 3.2 Tier B and C — deferred, specified for continuity

| Tier | Adds | Unlocks |
|---|---|---|
| B (6) | S5/S6 upper arms, lateral mid-humerus below deltoid insertion | Elbow angle at plant, minimum during drive, angle at release, flexion angular velocity; coarse humerothoracic elevation (report as ROM/change, never as an absolute target — IMU glenohumeral error is substantially larger than elbow error) |
| C (7) | S7 right thigh, lateral mid-femur | Hip/knee pumping, leg drive, kick identification, technique auto-classification |

The seventh-sensor identity is a real choice, not an oversight: **thigh** for technique breadth (and the literature's finding that hip/knee flexion discriminates skill where elbow ROM does not); **pole shaft below grip** for the cleanest possible plant detection on snow, useless on a SkiErg; **ski/boot** for glide-phase work. Deferred until an on-snow product is real (§23).

The standing argument, unchanged: **ship Tier A, instrument it well, and let validation data justify more sensors.** It is far easier to add sensors to a working system than to remove them from a product people have bought.

### 3.3 Coverage by tier

| Metric family | A (4) | B (6) | C (7) |
|---|---|---|---|
| Trunk angle, ROM, lean decay | ✅ | ✅ | ✅ |
| Lumbar flexion / svank | ✅ | ✅ | ✅ |
| Cycle rate, phase timing | ✅ | ✅ | ✅ |
| L/R symmetry (timing + kinematic) | ✅ | ✅ | ✅ |
| Arm drive angular velocity | ✅ | ✅ | ✅ |
| Elbow angle (plant / min / release) | ❌ | ✅ | ✅ |
| Shoulder elevation | ❌ | ⚠️ coarse | ⚠️ coarse |
| Leg drive / kick detection | ❌ | ❌ | ✅ |
| Technique auto-classification | Partial | Partial | ✅ |
| HR / HRV | ✅ | ✅ | ✅ |

### 3.4 Physical logistics — the retention risk

Wearables products die on straps and batteries, not on algorithms. Treated as a first-class workstream:

- **Straps:** chest belt (HR+), narrow sacral belt with a sensor pocket sized so the sensor cannot rotate, two forearm straps with a printed orientation arrow and an L/R colour. Sensor rotation inside the pocket is the single most common placement fault; the pocket geometry is the fix, and the software L/R swap (§15.2) is the cheap catch for the rest.
- **Battery:** CR2025, budgeted per §4.2. In-app per-sensor battery display with a "will not survive your usual session" warning computed from the athlete's median session length.
- **Identification:** sensors show their serial in-app; physical colour rings shipped in the box, mapped to sites in setup.
- **Measured in pilot:** support burden of logistics is an explicit pilot instrument (§20.7), not an afterthought.

---

## 4. Sampling and streaming

### 4.1 Rate selection

Double poling has a fundamental of roughly 0.65–1.35 Hz (40–80 cycles/min); joint-angle waveforms carry meaningful harmonic content to about the 8th–10th harmonic, i.e. ~10–13 Hz. Nyquist demands > 26 Hz; prudence demands ~4× the highest meaningful component.

| Mode | Rate | Use | Trade-off |
|---|---|---|---|
| **Standard** | **52 Hz** | Default for all technique sessions | 19.2 ms interval; sub-sample interpolation brings event timing to ~±4–6 ms |
| Endurance | 26 Hz | Long low-intensity sessions, battery-limited field days | 38.5 ms interval; angle waveforms still valid, symmetry-timing precision roughly halves |
| Validation | 104–208 Hz | Lab work against mocap, short bursts | Bandwidth and battery cost; not for routine use |

**52 Hz is the operating point.** 26 Hz is an explicit, labelled degradation — never a silent default. When active the UI widens the symmetry dead-band and suppresses the finest timing metrics rather than reporting them at false precision. Study 3 (§18) replaces this assumption with measured per-metric degradation.

### 4.2 Sensor configuration

- **Subscription:** `/Meas/IMU6/52` on all four. Magnetometer via `/Meas/Magn` at 13 Hz **only during calibration and quiet standing**, never as a continuous fusion input.
- **Accelerometer range: ±16 g.** Plant transients on a stiff ergometer clip at ±8 g on forearm sensors, and clipping is far worse than quantisation here because it silently biases the gravity estimate. Verified on hardware at Gate G0.
- **Gyroscope range: ±1000 dps.** Segment peaks are in the low hundreds of deg/s; the plant transient needs the headroom.
- **HR:** `/Meas/HR` plus `/Meas/RR`. `/Meas/ECG/128` optional for R-peak-accurate HRV or artefact review.
- **DataLogger:** enabled on every sensor for the full session, in parallel with streaming (§4.4).

### 4.3 BLE parameters

Four sensors at 52 Hz IMU6 is a light load — 6 floats × 4 bytes × 52 Hz ≈ 1.25 kB/s payload per sensor, ~1.5 kB/s with overhead, so ~6 kB/s aggregate for Tier A (~11 kB/s at Tier C). Comfortable, but configured deliberately:

- **2 M PHY** where the phone supports it.
- **Data Length Extension** on; Movesense batches samples per notification, so a larger ATT MTU directly reduces packet count.
- **Connection interval 15–30 ms.** Below 15 ms buys nothing at 52 Hz and increases contention across four links.
- **Concurrent links:** 4 is routine; 6–7 is achievable but chipset-dependent. Validated on the target device matrix at Gate G0 before any dependent code is written.

### 4.4 Onboard logging as the safety net

BLE *will* drop — arms sweep, bodies occlude, gyms are RF-noisy. DataLogger/Logbook runs on every sensor for the whole session. Post-session, the streamed record is reconciled against the logged record and gaps are backfilled.

Reconciliation rules:
1. Align logged and streamed records using the clock model (§5.1) and the sync-tap fiducials.
2. Where a streamed gap exceeds one sample interval, splice logged samples in; mark the range in `provenance_mask` as `logged`.
3. Recompute `dropout_pct` **after** backfill — it is the residual, not the raw BLE loss.
4. If a sensor's logbook is unreadable and its residual dropout exceeds the gate in Appendix A, its dependent metrics are suppressed for the session (§9.2).

This costs almost nothing and removes an entire class of "the session didn't record" failures.

---

## 5. Time synchronisation

Cross-sensor sync is the most under-appreciated requirement in the system, because **left–right timing offset is a headline metric and it lives in the 20–50 ms range** — the same order as uncorrected BLE arrival jitter.

### 5.1 Clock model per sensor

Record (device timestamp, host arrival time) pairs throughout the session. Fit a robust linear model — offset and skew — using **lower-envelope regression** on arrival times, which rejects the one-sided delay noise inherent to BLE (a packet can be late, never early). Update continuously; expose the current fit residual to L5.

```
t_host_true(i) ≈ α_s · t_device(i) + β_s
α_s : skew (ppm-scale), β_s : offset
Fit: minimise Σ ρ(residual) over the lower envelope of (t_device, t_arrival)
```

### 5.2 Sync tap

At session start and end, the athlete **taps the ergometer frame firmly three times with both hands** while wearing all sensors. The shared impulse gives a common fiducial across every accelerometer, independent of BLE.

Detection: band-passed accelerometer magnitude, three peaks within a 2.5 s window, peak prominence above a fixed multiple of the quiet-standing noise floor, consistent inter-tap spacing across sensors. The taps cross-check the clock model rather than replacing it — agreement within tolerance validates the fit; disagreement raises `sync_error_ms`.

The end-of-session tap is what turns sync from an assumption into a measurement, because it bounds drift across the whole session rather than at one instant. It is prompted, skippable, and its absence widens the reported sync uncertainty rather than failing the session.

### 5.3 Error budget and consequence

| Quantity | Target | If exceeded |
|---|---|---|
| Residual sync error (tap-validated) | **< 5 ms** | Timing-symmetry metrics suppressed for the session; symmetry bar driven by drive-velocity SI alone; report states why |

One threshold, stored once as `sync.max_residual_ms`, read by both the analysis layer and the descriptor builder. This supersedes the 5 ms / 8 ms split in the source documents (§0.3).

---

## 6. Calibration

Total protocol **60–90 seconds, five steps**. Every step has an explicit pass/fail so a bad calibration is caught before the session, not discovered in the report.

### 6.1 The five steps

**Step 1 — Gyroscope bias and static reference (10 s).**
Sensors worn, athlete stands motionless. Estimate per-axis gyro bias as the mean of the gyro signal; initialise each quaternion from the accelerometer gravity vector.
*Pass:* gyro SD < 1 deg/s on every axis; accelerometer magnitude within 1.0 ± 0.03 g. *Fail:* "stand still" and repeat.

**Step 2 — Upright anatomical pose (5 s).**
Athlete stands tall, feet hip-width, arms hanging straight, palms to thighs, facing the machine. This defines the longitudinal axis of each segment (aligned with gravity in this pose), the zero for trunk-to-vertical and pelvis-to-vertical, and the 180° elbow reference in Tier B.
*Pass:* segment longitudinal axes within 15° of gravity; no motion above the Step 1 noise floor.

**Step 3 — Functional axis identification (10–15 s).** *The critical step.*
Athlete performs 4–6 slow, exaggerated poling cycles — deliberately slow, full range, no force. For each sensor, take gyroscope samples during the movement and compute the **dominant rotation axis as the first principal component of the angular velocity vectors**. In predominantly sagittal motion that axis *is* the medio-lateral (flexion–extension) axis of the segment. Remaining axes follow by cross product with the Step 2 longitudinal axis.

This is what makes the system robust to real-world mounting. The sensor does not need to be aligned with the body — the misalignment is *measured* and corrected. It also solves the heading problem: the sagittal plane is defined functionally, per segment, with no magnetometer.

*Pass:* PC1 explains > 80% of angular velocity variance, **and** the resulting medio-lateral axis lies within 30° of perpendicular to the segment longitudinal axis. *Fail:* the movement was not planar enough, or the sensor has slipped — prompt and repeat, with the on-screen text naming which sensor failed.

**Step 4 — Personal ready position (5 s, optional).**
Athlete adopts their habitual start position at the machine. Stored as the personal catch-position baseline and used to personalise the trunk green zone where anthropometry or mobility makes population targets inappropriate.

**Step 5 — Verification pass (10 cycles, easy pace).**
Live angles with a confidence indicator. The system checks that the trunk trace is smooth and returns to a consistent recovery baseline (drift check), that left and right forearm traces are plausibly similar in shape (gross placement-error check), and that the lumbar angle sits near zero at the top of recovery.

Left/right baselines differing beyond a plausible margin almost always means a sensor is mounted rotated or on the wrong limb. Catching it here — and offering the one-tap software L/R swap — is worth more than any downstream cleverness.

### 6.2 Calibration object (persisted per session)

```json
{
  "calibration_id": "uuid", "created_at": "ISO8601", "protocol_version": "1.0",
  "sensors": {
    "S1": {
      "gyro_bias_dps": [0.42, -0.13, 0.07],
      "q_sensor_to_segment": [w, x, y, z],
      "axis_longitudinal": [x, y, z],
      "axis_mediolateral": [x, y, z],
      "pca_variance_explained": 0.87,
      "perpendicularity_deg": 11.4,
      "static_accel_norm_g": 1.004,
      "step_results": { "s1": "pass", "s2": "pass", "s3": "pass", "s5": "pass" }
    }
  },
  "personal_reference": { "trunk_ready_deg": 41.8, "recorded": true },
  "magnetic_disturbance_index": 0.06,
  "overall": "pass",
  "notes": ["S3 repeated once (PCA 0.74 on first attempt)"]
}
```

`calibration_ok` in the session descriptor is `overall == "pass"` **and** no unresolved slip flag (§6.3).

### 6.3 Recalibration triggers

- **Slip detection.** Each recovery phase contains a quasi-static instant. If the gravity direction in a segment's sensor frame shifts by more than ~8° from its calibrated baseline across consecutive quiet instants, without a corresponding real posture change, flag slip. Consequences: absolute-angle metrics for that segment are marked from the slip timestamp onward, the athlete is prompted mid-session (non-blocking), and the report shows the affected range explicitly rather than averaging across it.
- **Session length.** Prompt a 10-second re-zero every 45 minutes.
- **Re-attachment.** Any disconnect/reconnect forces Steps 1–3 for that sensor. No exceptions — a reconnected sensor has an unknown orientation.

### 6.4 Failure experience

Calibration failure is the highest-frequency friction point in the product, so its UX is specified, not left to implementation:

1. Name the sensor, not the abstraction ("Right forearm — try again"), with the site highlighted on the silhouette.
2. Name the likely cause in one clause ("the movement wasn't quite planar" / "the strap may have rotated").
3. Offer exactly one action, plus "skip this sensor" only where the session can proceed with a documented reduction in scope.
4. Never fail silently into a degraded session. If the athlete skips, the affected metrics are greyed with a reason for the whole session.

---

## 7. Orientation estimation

### 7.1 Mahony core

Mahony's complementary filter on SO(3), per sensor, at IMU rate. State: unit quaternion `q` (sensor → world) and gyro bias `b`. At each sample with gyro `ω` and accelerometer `a`:

**1. Estimated gravity direction in sensor frame** (third row of the rotation matrix from `q`):

```
v = [ 2(q1q3 − q0q2),  2(q0q1 + q2q3),  q0² − q1² − q2² + q3² ]
```

**2. Measured gravity direction:** `â = a / ‖a‖`

**3. Orientation error:** `e = â × v`

**4. Bias integration and corrected rate:**

```
b ← b + Ki · e · Δt
ω_corr = ω − b + Kp_eff · e
```

**5. Quaternion integration** (first-order is adequate at 52 Hz; use the exponential map below ~40 Hz):

```
q̇ = ½ · q ⊗ [0, ω_corr]
q ← normalise(q + q̇ · Δt)
```

### 7.2 The critical adaptation — adaptive accelerometer trust

This is where a textbook Mahony fails on this application. During the drive the forearm sees several g of linear acceleration; `â` is then not gravity at all, and the filter pulls pitch toward a meaningless direction *precisely during the phase you most want to measure*.

Gate the proportional gain on accelerometer plausibility:

```
r = | ‖a‖ − 1g | / 1g

if   r < 0.05:  Kp_eff = Kp_high                              # quasi-static: correct aggressively
elif r < 0.25:  Kp_eff = Kp_high · (1 − (r − 0.05)/0.20)       # linear fade
else:           Kp_eff = 0                                     # dynamic: pure gyro integration

Ki = 0 whenever Kp_eff = 0
```

**Freezing `Ki` matters as much as gating `Kp`.** An integrator that accumulates during a corrupted-reference window injects a persistent bias error that survives long after the transient — a slow, invisible corruption that looks exactly like a technique change.

The gyroscope carries the estimate through the drive; the recovery phase — roughly 70% of the cycle on snow, about 46% on the ergometer — supplies ample quasi-static windows for correction. **Effective correction bandwidth is governed by cycle rate, not sample rate**, which is the second reason 52 Hz suffices.

### 7.3 Gains

| Parameter | Start | Rationale |
|---|---|---|
| `Kp_high` | 1.0 rad/s | Corrects within one recovery phase without injecting noise |
| `Ki` | 0.02 | Slow bias tracking; static calibration has removed the bulk |
| Dead-band low | 0.05 g | Below typical recovery-phase residual acceleration |
| Dead-band high | 0.25 g | Above this, no useful gravity information remains |

Tune `Kp_high` empirically against mocap: raise until pitch noise becomes visible, then back off ~30%. Gains live in the versioned config (§10), not in code.

### 7.4 Heading strategy

**Do not run 9-DOF fusion continuously.** Hard- and soft-iron distortion from an ergometer frame, rebar flooring, and nearby equipment varies with position and posture, producing heading errors worse than gyro drift and correlated with the movement itself.

Heading is handled three ways instead:

1. **Inclination metrics need no heading.** Trunk-to-vertical and pelvis-to-vertical are angles with respect to gravity — fully observable in 6-DOF, and they are the most important signals in the system. This is a reason to *prefer* inclination-based metric definitions, not a workaround.
2. **Relative joint angles use the functional sagittal frame** from calibration Step 3. Because each segment's flexion axis was measured, relative angles are computed by projecting the relative rotation onto that axis — invariant to absolute heading.
3. **Residual yaw drift is corrected per cycle.** At the top of recovery, segment orientations are near-repeatable and quasi-static. Anchor each segment's yaw to its calibrated recovery reference with a slow correction, time constant ≈ 10 cycles — slow enough that the correction cannot mask real cycle-to-cycle variation.

The magnetometer is used only during calibration for an initial heading estimate, and to log a magnetic disturbance indicator (field-magnitude deviation from local expected) so hostile environments can be flagged in the report.

### 7.5 Quaternion to angles

| Metric | Definition | Convention |
|---|---|---|
| **Trunk-to-vertical** | Angle between thorax longitudinal axis and gravity | 0° upright, 90° horizontal |
| **Pelvis-to-vertical** | Same, sacrum sensor | 0° upright |
| **Lumbo-pelvic flexion** | Sagittal component of `q_pelvis⁻¹ ⊗ q_thorax`, projected on the functional flexion axis | Positive = flexion; **negative = lumbar extension (svank)** |
| **Forearm sweep** | Forearm longitudinal axis relative to vertical, sagittal component | Signed; forward of vertical positive |
| **Elbow flexion** (Tier B) | Between upper-arm and forearm longitudinal axes, on the functional elbow axis | 180° = full extension |
| **Shoulder elevation** (Tier B) | Between upper-arm and thorax longitudinal axes | Report as ROM/change, never absolute |
| **Angular velocities** | Calibrated gyroscope projected directly onto the functional flexion axis | **No numerical differentiation** |

That last row deserves emphasis: angular velocity comes straight from the gyroscope, so **velocity metrics are more accurate than angle metrics** — the opposite of an optical-mocap pipeline. Since the literature identifies angular velocity as a skill discriminator, the sensor modality is well matched to the question. Design metrics to exploit this rather than fighting it.

### 7.6 Host-side for v1

Stream raw IMU6 and run Mahony on the phone. Raw data is needed for mocap validation, gain tuning, and classifier training — do not discard it during the phase when the metrics themselves are still being decided. On-device fusion (custom `/Meas/Quaternion/52` provider, payload 24 → 16 bytes, meaningful CR2025 gain) is a v2 candidate with a permanent raw-streaming debug mode. Decision at Gate G5.

---

## 8. Event detection and cycle segmentation

### 8.1 State machine

Four states per side: `RECOVERY → CATCH → DRIVE → RELEASE → RECOVERY`.

**Pole plant / catch — two stage, coarse then fine:**

1. *Coarse gate:* forearm sagittal angular velocity crosses zero from the recovery direction into the drive direction.
2. *Fine timing:* within ±3 samples of the crossing, locate the maximum of accelerometer jerk magnitude `‖da/dt‖`. On a SkiErg, cord-tension onset produces a distinct jerk peak; on snow, pole impact does the same.
3. *Sub-sample refinement:* fit a parabola to the three jerk samples around the peak and take the vertex. This recovers timing to roughly ±4–6 ms at 52 Hz — a 3–4× improvement on the raw sample interval, and the reason 52 Hz supports symmetry metrics at all.

**Release / pole-off:** peak drive angular velocity followed by rapid deceleration, coinciding with the extremum of forearm sweep behind the body. Refined by parabolic interpolation on the angular-velocity derivative.

**Rejection rules.** Discard cycles with duration outside [0.45 s, 2.2 s]; plant-to-release below 0.15 s; plant jerk peak below a session-adaptive threshold (catches phantom detections during rest periods). Rejected cycles are counted and reported (§12), never silently dropped — a session with 30% rejection is a data-quality event, not a clean session with fewer cycles.

### 8.2 Per-cycle feature set

Stored one row per valid cycle. This table is the metric dictionary; the report, the fault engine, and the descriptor all draw from it and nothing else.

| Family | Feature | Unit | Notes |
|---|---|---|---|
| **Timing** | cycle_time | s | plant to plant |
| | cycle_rate | /min | 60/cycle_time |
| | poling_time | s | plant to release |
| | recovery_time | s | release to next plant |
| | poling_time_pct | % | headline; mode-dependent band |
| | poling_recovery_ratio | — | |
| **Trunk** | trunk_angle_at_plant | deg | |
| | trunk_max_lean | deg | headline |
| | trunk_flexion_rom | deg | |
| | trunk_angle_end_recovery | deg | drift/baseline check |
| | trunk_peak_flexion_velocity | deg/s | gyro-direct |
| **Lumbar** | lumbo_pelvic_min | deg | most negative = worst svank |
| | lumbar_extension_duration | s | time below 0 |
| | lumbar_peak_extension_rate | deg/s | |
| **Arms (per side)** | sweep_at_plant | deg | |
| | sweep_at_release | deg | |
| | sweep_rom | deg | |
| | peak_drive_velocity | deg/s | gyro-direct; skill discriminator |
| | time_to_peak_velocity | % of poling | |
| **Symmetry** | plant_timing_offset | ms | L−R, signed |
| | SI_drive_velocity | % | |
| | SI_sweep_rom | % | |
| **Coupling** | trunk_plant_phase_lag | ms | trunk flexion onset vs plant — the "arm-pulling vs whole-body drive" discriminator |

Tier B adds elbow angle at plant, minimum during drive, timing of minimum as % of poling phase, angle at release, and peak flexion angular velocity.

---

## 9. Session analysis

### 9.1 Aggregation

From the per-cycle table:

- **Session aggregates:** mean, SD, median, IQR per feature over valid cycles.
- **Thirds:** the same aggregates over the first, middle, and last third of valid cycles — the fatigue-drift substrate.
- **Ensemble curve:** cycles time-normalised 0–100%, mean ± SD band for trunk angle, lumbar angle, and left/right sweep. The SD band width is itself a metric (consistency), not decoration.
- **Cycle-to-cycle SD:** rising variability within a session is one of the earliest fatigue signatures and is often more informative than any mean.
- **Symmetry distributions:** timing-offset histogram and trend; SI trend per bilateral metric.

### 9.2 Data-quality gates and suppression policy

Gates are evaluated once, at session close, before anything is rendered or serialised.

| Gate | Condition | Suppressed | Live-view consequence |
|---|---|---|---|
| Sync | `sync_error_ms ≥ 5` | All left–right timing and timing-symmetry metrics | Symmetry bar driven by drive-velocity SI only |
| Calibration | `calibration_ok == false` | All absolute angle metrics; timing, rate, and within-session *trends* survive | Posture ring switches to ROM-relative mode |
| Dropout | `dropout_pct > 15` (post-backfill) | Fatigue-drift metrics | Thirds analysis absent from report |
| Slip | Slip flagged at time *t* | Affected segment's absolute angles from *t* onward | Ring greys for that segment |
| Rejection | `rejected_cycles_pct > 25` | Session flagged low-confidence; ensemble curve annotated | — |
| Rate mode | 26 Hz active | Finest timing metrics per Study 3 output | Wider symmetry dead-band |

**Suppression is structural, at two levels.** In the *report*, suppressed metrics are **greyed out with a stated reason, not hidden** — the athlete must be able to see that something was measured badly rather than not measured. In the *descriptor* fed to the coaching layer, they are **omitted entirely**, with only their names listed under `suppressed_due_to_quality`. The model cannot discuss a number it does not have.

Without §12's data-quality section and this policy, the athlete cannot distinguish "my technique changed" from "the sensor slipped", and every longitudinal analysis built on the data inherits that ambiguity.

### 9.3 Fault engine

Faults are rules over session aggregates and per-cycle features, defined in the versioned config, each with a name, condition, severity, and trainability tag.

| Fault | Condition (config-driven) | Trainability |
|---|---|---|
| `lumbar_extension` (svank) | extension episodes per 100 cycles above band | High — cue-responsive |
| `trunk_lean_decay` | last-third max lean below first-third by more than band | Low — endurance/strength |
| `over_flexion` | max lean above band, sustained | High |
| `early_release` | sweep at release below band | High |
| `incomplete_follow_through` | sweep ROM below band | High |
| `arm_dominant` | trunk–plant phase lag above band (trunk lags) | Medium |
| `high_rate_collapse` | cycle rate rising while arm ROM falls, both beyond bands, in the same window | Medium |
| `asymmetry_timing` | mean plant offset above band, sustained | Medium |
| `asymmetry_kinematic` | SI above 10% sustained | Medium |

Each fired fault carries: metric reference, magnitude, `delta_vs_baseline`, timestamped episode list, and a `data_quality_ok` flag. A fault whose supporting metric was suppressed **does not fire** — it is not "unknown", it is absent.

The classic degradation pattern — **rising cadence with falling ROM and increasing svank** — is called out explicitly as a composite when all three fire together, because the combination means something the parts do not.

### 9.4 Priority cascade (code-side)

Evaluated after the fault engine, emitted as `priority_focus_fault`:

```
a. lumbar_extension above band                    → priority
b. any fault above band AND worsening vs baseline → priority (highest severity first)
c. first fault in faults_ranked                   → priority
d. nothing above band                             → priority = null, coaching mode = "progression"
```

Tie-break on **trainability**: prefer the fault an athlete can change with a cue over one that needs months of strength work. Genuine ties are flagged `tie: true` and the model may choose between the two named candidates — the only selection decision it is ever given.

Case (d) matters: when nothing is wrong, the system must not manufacture a fault. It names what held up and offers a progression instead of a correction.

### 9.5 Baselines and longitudinal store

- **30-day rolling mean and SD** per metric, per mode, per athlete — the basis of `delta_vs_baseline`.
- **Personal best** per headline metric, defined conservatively (best session of ≥ 500 valid cycles).
- **Cue ledger:** every cue issued, the metric it targeted, and the outcome computed at the next session — the substrate for `previous_cue_outcome` and for the adoption evaluation in §14.7.
- Sessions failing quality gates are excluded from baseline updates for the affected metrics, and that exclusion is visible in the longitudinal view.

---

## 10. Reference-band configuration

### 10.1 Why it is a versioned artefact and not code

Reference targets **must** be per-mode: relative poling phase alone differs by roughly 20 percentage points between ergometer and snow, so one threshold set would mark correct ergometer technique as faulty. Beyond that, bands change as validation data arrives, and a band change must be traceable, reversible, and attributable to evidence.

**Every threshold in the system lives here** — quality gates, calibration criteria, fault definitions, Mahony gains, live-view zones, symmetry flags. One source of truth read by the analysis layer, the live view, the descriptor builder, and the validator. Appendix A is the human-readable rendering of this file.

### 10.2 Schema

```json
{
  "config_version": "2026.1",
  "effective_from": "2026-03-01",
  "modes": {
    "ergometer_double_poling": {
      "levels": {
        "trained": {
          "bands": {
            "trunk_max_lean_deg":            { "band": [70, 78], "provenance": "measured",
                                               "source": "…", "personalisable": true },
            "poling_time_pct":               { "band": [50, 56], "provenance": "measured",
                                               "source": "…" },
            "lumbar_extension_per_100":      { "band": [0, 1],   "provenance": "measured",
                                               "source": "…" },
            "trunk_plant_phase_lag_ms":      { "band": [-40, 40],"provenance": "heuristic",
                                               "source": "coaching convention" }
          }
        }
      }
    }
  },
  "gates": { "sync_max_residual_ms": 5, "dropout_max_pct": 15,
             "rejected_cycles_max_pct": 25, "slip_deg": 8, "rezero_interval_min": 45 },
  "symmetry": { "SI_flag_pct": 10 },
  "filter":   { "Kp_high": 1.0, "Ki": 0.02, "deadband_low_g": 0.05, "deadband_high_g": 0.25,
                "yaw_anchor_tau_cycles": 10 },
  "events":   { "cycle_min_s": 0.45, "cycle_max_s": 2.2, "min_drive_s": 0.15 },
  "calibration": { "gyro_sd_max_dps": 1.0, "accel_norm_tol_g": 0.03,
                   "pca_variance_min": 0.80, "perpendicularity_max_deg": 30 }
}
```

### 10.3 Provenance, and why it reaches the athlete

Each band is tagged `measured` (peer-reviewed biomechanics, with citation) or `heuristic` (coaching convention). This propagates all the way to the coaching text: measured findings are stated directly, heuristics are marked as convention ("coaches generally look for…") so the athlete knows how much weight to give them. It is one field in a config file and it changes what the product is honest about.

### 10.4 Personalisation

Bands tagged `personalisable` may be shifted by the athlete's calibration Step 4 reference or by their own distribution once ≥ 10 clean sessions exist, within a bounded offset from the population band. Personalisation is shown in the report ("your trunk band is set 4° lower than the population default, from your ready position") — never applied silently.

### 10.5 Change control

Config version bumps only; **no hot edits.** Every session records the config version it was analysed under. Longitudinal comparisons across a version boundary display a marker. Band changes require the evidence citation in the commit.

---

# PART III — INTERPRETATION AND FEEDBACK

## 11. Live feedback

### 11.1 The three-signal display

At threshold with cycle rates near 1 Hz, an athlete has perhaps 200–300 ms of usable glance time per cycle and a narrowed attentional field. The live display therefore carries **three signals maximum**, all pre-attentively decodable — colour and position, no reading.

**Primary — trunk posture ring.** A large arc whose fill position tracks live trunk-to-vertical angle.
- Green: within the personalised target band (population starting point ~42° at plant, up to ~75–78° max lean)
- Amber: approaching limits
- Red: over-flexion beyond target, **or any lumbar extension episode** — the safety signal overrides everything and turns the ring red regardless of trunk angle

**Secondary — symmetry bar.** Horizontal, centre-marked; the indicator deviates proportional to plant-timing offset and drive-velocity SI. **Dead-band set to the measurement uncertainty of the current sampling mode.** The bar must not twitch on noise, or the athlete learns to ignore it — and an ignored signal is worse than an absent one because it occupies attention.

**Tertiary — cycle rate.** One large number with a target band, **shown only when a cadence is prescribed**, otherwise hidden. It also carries the high-rate-collapse warning: if cadence rises while arm ROM falls, the number turns amber, because that combination is technique degradation masquerading as effort.

**Peripheral — heart-rate zone** as a thin coloured border. No numerals.

Everything else — elbow angles, curves, stick figures, per-cycle values — is deliberately absent.

**The screen budget is fixed.** Any proposal to add a live element must *displace* an existing one, not join it. This rule is in the spec because it is the rule that erodes first.

### 11.2 Latency and rendering budget

| Stage | Budget | Note |
|---|---|---|
| Sensor → host arrival | ≤ 30 ms | connection interval bound |
| Mahony + angle | ≤ 5 ms | per sample, 4 sensors |
| Event/state update | ≤ 5 ms | |
| Render | 1 frame | |
| **Glass-to-glass, posture ring** | **≤ 100 ms** | Beyond this the colour no longer maps to the felt movement |
| Svank audio cue, episode onset → tone | ≤ 150 ms | Safety cue; earliest useful moment |

Live view runs off L2/L3 only. It never waits on L5 aggregation.

### 11.3 Audio cues

Movesense has no haptic actuator, so cues come from the phone or, better, earbuds. Audio is right because gaze is fixed forward and the visual channel is loaded.

| Cue | Sound | Trigger |
|---|---|---|
| Over-flexion | Short low tone | Sustained beyond band |
| **Svank** | **Distinct double tone, different timbre** | Extension episode — must be unmistakable; this is the safety cue |
| Cadence | Soft click metronome | Only when prescribed |
| Asymmetry | Ascending/descending pan | Optional, off by default |

**Cue fading** is mandatory: high density for novices, decaying as performance stabilises, to avoid the dependency effect that concurrent feedback reliably produces. The fading schedule is exposed in settings so a coach can control it, and the current fading level is shown on the live screen ("audio cues on · fading 60%") so its behaviour is never mysterious.

### 11.4 Degraded modes on the live screen

| Condition | Live behaviour |
|---|---|
| 26 Hz endurance mode | Wider symmetry dead-band, labelled; finest timing metrics not displayed |
| Sensor dropped mid-session | Affected signal greys immediately with a small icon; session continues; logbook backfills after |
| Slip detected | Posture ring greys, one-line prompt, session continues |
| Calibration marked not-ok | Ring switches to ROM-relative zones rather than absolute |

Degradation is always *visible and labelled*. A silently degraded live signal teaches the athlete the wrong movement.

### 11.5 Coach view — specified, deferred

The attention constraint applies to the athlete, not to a coach standing beside the machine. A tablet second screen carries the rich display the athlete cannot use: live sagittal stick figure from segment quaternions, rolling trunk/left/right traces over the last 10 cycles, per-cycle feature table with green/amber/red cells, and an ensemble overlay building in real time against the reference band. This split resolves "the data is valuable" against "the athlete can't process it" without discarding either. **Out of scope for v1** (§1.4); the data plumbing is designed so it can be added without touching L1–L5.

---

## 12. After-session report

### 12.1 The eight sections

Rendered deterministically. No model output is required for any of it.

1. **Session summary.** Duration, total and valid cycles, work/distance if the ergometer is pairable, mean and peak cycle rate, HR zone distribution, HRV summary, technique modes detected with time in each.
2. **Ensemble-averaged cycle.** The centrepiece. Time-normalised 0–100% with mean ± SD band for trunk angle, lumbar angle, and left/right sweep, overlaid on the mode-appropriate reference band. The SD band width is the consistency metric.
3. **Consistency and variability.** Cycle-to-cycle SD per key feature, with within-session trend.
4. **Fatigue drift.** Key metrics against time and tabulated by thirds. Watch specifically: max trunk lean (declines as the core fatigues), cycle rate (rises), arm ROM (falls), lumbar extension episodes (increase). The composite pattern is called out explicitly when detected.
5. **Symmetry.** Timing-offset distribution and trend, SI trends per bilateral metric, flag above 10% sustained — **always with measurement uncertainty alongside.** A 6% asymmetry measured at 5 ms sync error is a finding; the same number at 20 ms is not, and the report must make that difference impossible to miss.
6. **Fault log.** Timestamped, counted, duration-weighted: svank episodes, over-flexion, early release, incomplete follow-through, arm-dominant cycles, high-rate-collapse windows — each linked to the moment in the session, so the athlete sees *when*, not only *how often*.
7. **Longitudinal comparison.** Versus previous session, 30-day rolling mean, and personal best; the two or three largest changes highlighted in either direction.
8. **Data quality.** Calibration residuals, sync error, dropout percentage (post-backfill), magnetic disturbance index, rejected-cycle count, slip events with timestamps, config version.

Section 8 is not a nicety. It is the section that lets the athlete distinguish a technique change from a sensor problem, and every longitudinal claim in sections 4 and 7 depends on it.

### 12.2 Greying rules

Metrics failing a quality gate are rendered **greyed with a one-line reason**, in place, never removed and never silently replaced by an estimate. The reason names the gate ("sync error 11 ms — timing symmetry not reportable this session"), because a stated limitation is a trust-building event and an unexplained gap is not.

### 12.3 Export

- **CSV/JSON** per-cycle feature table and time-normalised ensemble curves
- **Session descriptor** (§13) as JSON
- **Deterministic report** as PDF, for sending to a coach or physiotherapist
- **Raw IMU archive** — opt-in, per session, for research use and for the replay harness

All export is athlete-initiated. Nothing is uploaded by default.

---

## 13. Session descriptor — the contract

### 13.1 Design

A compact object, 2–5 kB, that is simultaneously the coaching layer's entire input, the audit record for every coaching claim, and the unit under test for the descriptor module. It carries **only** metrics that passed their quality gates.

```json
{
  "session_id": "uuid",
  "config_version": "2026.1",
  "mode": "ergometer_double_poling",
  "athlete_level": "trained",
  "athlete_language": "sv",
  "duration_s": 2400,
  "cycles_valid": 1980,
  "cycles_rejected_pct": 3.1,

  "data_quality": { "sync_error_ms": 3.2, "dropout_pct": 0.4, "calibration_ok": true },
  "suppressed_due_to_quality": [],

  "metrics": [
    { "name": "trunk_max_lean_deg", "value": 68.2, "sd": 4.1,
      "reference_band": [70, 78], "status": "below",
      "provenance": "measured", "delta_vs_baseline": -3.4 },
    { "name": "lumbar_extension_per_100", "value": 2.4,
      "reference_band": [0, 1], "status": "above",
      "provenance": "measured", "delta_vs_baseline": 1.8 },
    { "name": "poling_time_pct", "value": 53.1,
      "reference_band": [50, 56], "status": "within",
      "provenance": "measured", "delta_vs_baseline": 0.2 }
  ],

  "fatigue_drift": { "trunk_lean_thirds": [71.4, 68.0, 65.2],
                     "cycle_rate_thirds": [52, 55, 59],
                     "arm_rom_thirds": [88, 85, 79] },
  "symmetry": { "timing_offset_ms_mean": 22, "SI_drive_velocity_pct": 8.1 },

  "faults_ranked": ["lumbar_extension", "trunk_lean_decay"],
  "priority_focus_fault": "lumbar_extension",
  "priority_tie": false,
  "coaching_scope": "full",

  "history_summary": {
    "sessions_30d": 12,
    "previous_cue_metric": "sweep_at_release",
    "previous_cue_outcome": "improved"
  }
}
```

### 13.2 Field notes

| Field | Purpose |
|---|---|
| `suppressed_due_to_quality` | Names only. The model is told a family was unreliable, never what its value might have been. |
| `priority_focus_fault` | Computed by §9.4. The model phrases; it does not choose. |
| `priority_tie` | The single case where selection is delegated, between two named candidates. |
| `coaching_scope` | `conservative` drops `cue` and `drill` from the required output schema (§14.2). |
| `previous_cue_outcome` | Computed from the metric the previous cue targeted — grounded continuity, not a guess. |
| `config_version` | Makes every coaching claim reproducible against the bands in force at the time. |

The descriptor builder is its own module with exhaustive path coverage in test: every gate, every cascade branch, every scope, every continuity outcome.

---

## 14. LLM coaching layer

### 14.1 System prompt

```
You are the coaching voice of a cross-country skiing double-poling training
system. You write short, post-session feedback for an athlete who has just
finished a session recorded with body-worn motion sensors.

You are a technique coach. You are not a clinician. You do not diagnose
injury, pathology, or medical conditions, and you do not give treatment
advice.

## What you receive

A JSON session descriptor. Every metric in it has already been computed and
evaluated against reference bands by the analysis system. Each metric carries
value, sd, units, reference_band, status, provenance ("measured" from
peer-reviewed biomechanics, or "heuristic" from coaching convention), and
delta_vs_baseline.

Metrics whose data was unreliable have already been REMOVED from the
descriptor; their names appear in suppressed_due_to_quality. You do not know
their values and must not speculate about them. You may note in one clause
that a measurement was not reliable this session.

The descriptor also names priority_focus_fault. The analysis system has
already chosen it. Your job is to explain and phrase it, not to re-rank.

## Absolute constraints

1. NEVER state a number that does not appear in the descriptor. You may round
   a value it contains. You may not estimate, infer, average, convert units,
   or recall a typical value from your own knowledge. If you want to say
   "about 5 degrees low" and the descriptor does not contain that difference,
   say "slightly low".

2. NEVER diagnose. Describe movement patterns and their known mechanical
   consequences. Do not say the athlete has, or is developing, any injury or
   condition.

3. Discuss ONLY priority_focus_fault as the focus. If priority_tie is true,
   choose between the two named candidates, preferring the one an athlete can
   change with a cue. Other fired faults are named in `suppressed` and not
   discussed — athletes given multiple cues adopt none of them.

4. Provenance governs confidence. For "measured", state the point directly.
   For "heuristic", mark it as coaching convention — "coaches generally look
   for…" — so the athlete weighs it less. Never present a heuristic as an
   established finding.

5. If coaching_scope is "conservative", omit the cue and drill fields
   entirely. Describe what was observed, neutrally, and stop.

6. If priority_focus_fault is null, do not manufacture a fault. Say the
   session was technically sound, name what held up, and give a progression
   rather than a correction.

## Writing the cue

Use an EXTERNAL focus of attention — direct attention to the effect on the
equipment or the environment, not to the body part. External-focus cues
produce better motor learning than internal-focus ones.

  Good:  "drive your bodyweight down through the handles"
  Good:  "think about pushing the machine into the floor"
  Poor:  "contract your abdominals"
  Poor:  "engage your lats"

One sentence the athlete could repeat to themselves mid-set.

If athlete_language is "sv", write everything in Swedish using established
Swedish coaching vocabulary (stakning, svank, bålen, frånskjut, åkekonomi).
Do not translate cues literally from English — use the phrasing a Swedish
coach would actually say.

## Tone

Direct, warm, specific. You are talking to an adult who chose to train hard.
Do not inflate praise — if the session was mediocre, do not call it strong.
Do not soften a real problem into vagueness. No exclamation marks, no
motivational filler.

## Output

Return ONLY valid JSON matching the schema in the user message. No prose
before or after, no markdown fences.
```

Note what is *no longer* in the prompt relative to the source package: the priority-selection cascade (now code-side) and the per-gate suppression rules (now structural). Both moved from instruction to architecture, which is the general direction any constraint should travel when it can.

### 14.2 User message and output schema

```
<session_descriptor>
{ …the object from §13… }
</session_descriptor>

<mechanism_notes>
{ 3–6 short retrieved passages explaining WHY the flagged fault matters —
  mechanical consequence, not target values. Retrieved from the curated
  corpus, keyed on priority_focus_fault. }
</mechanism_notes>

Write the post-session feedback. Return only JSON:

{
  "went_well":      { "text": string, "metric_ref": string|null },
  "priority_focus": { "fault": string, "what_happened": string,
                      "why_it_matters": string, "cue": string,
                      "metric_ref": string },
  "drill":          { "name": string, "description": string, "target": string },
  "watch":          { "text": string, "metric_ref": string } | null,
  "suppressed":     [string],
  "continuity":     string | null
}
```

Under `coaching_scope: "conservative"`, `priority_focus.cue` and `drill` are removed from the required schema and rejected if present.

`mechanism_notes` sits in the user message, not the system prompt, so per-session retrieval varies without invalidating the prompt cache. The descriptor goes first — it is the bulk of the tokens.

**Corpus:** a few dozen curated documents — biomechanics references, Swedish federation coaching cues, the team's own coaching notes — versioned alongside the band config. A tight curated corpus beats a large scraped one here, because the failure mode is confident wrong advice, not insufficient coverage.

### 14.3 Validator

Not optional. This is where hallucination risk actually closes.

| # | Check | Rule | On fail |
|---|---|---|---|
| 1 | **Per-field numeric provenance** | Every numeral in a field must trace to the metric named in *that field's* `metric_ref`, within rounding tolerance, or appear on the whitelist (session duration, cycle count, set/rep counts from the drill library). Extraction handles both decimal point and Swedish decimal comma. | Reject |
| 2 | **Suppression compliance** | No output field mentions a metric family in `suppressed_due_to_quality`. Per-language keyword lists. Belt-and-braces now that suppression is structural. | Reject |
| 3 | **Schema and cardinality** | Valid JSON, required fields present, exactly one `priority_focus`, `cue` a single sentence, scope-appropriate fields | Reject |
| 4 | **Provenance hedging** | If `priority_focus.metric_ref` has `provenance: "heuristic"`, output must contain a hedging marker from the per-language phrase list | Reject |
| 5 | **Clinical language** | Reject on diagnostic vocabulary: injury names, "you have", "this is causing damage", "see a doctor" — the last because escalation is templated, never generated | Reject |

**On failure:** retry once with the specific violation appended to the user message. On second failure, render the deterministic template report. **Log every failure with its descriptor** — these logs are the most useful prompt-tuning data the programme will produce, and Phase 5 triages them weekly.

**Documented residual risk:** qualitative misrepresentation ("nearly doubled", "far above") passes all five checks. Accepted for v1, monitored through the human review set in §14.7. Stated here so it is a known limitation rather than a discovered one.

### 14.4 Fallback template

The deterministic coaching card, rendered whenever the model is unavailable, disabled, or twice-rejected. Same visual shape as the generated card, filled from the descriptor by string templates: the highest-priority fault, its magnitude and direction versus band, the library cue mapped to that fault, and the library drill. Blunter, never wrong. The athlete is told which they are seeing.

### 14.5 Escalation — non-LLM, above everything

Templated, fixed text, triggered by rule, never generated and never rewritten:

**Triggers**
- `lumbar_extension` above reference in ≥ 4 of the last 6 sessions
- Any athlete-reported pain entry
- A single session with lumbar-extension episodes far above the athlete's own distribution

**Behaviour**
- Fixed card renders **above** the coaching output
- Sets `coaching_scope: "conservative"` — cue and drill are dropped for that session
- Recommends assessment by a physiotherapist; states plainly that the system measures movement and does not assess backs
- Offers two actions: share session data, log pain
- **The model is not told the escalation fired** — otherwise it editorialises around it

The sentence "this app measures movement — it can't assess your back" is load-bearing for the regulatory position in §19 and is frozen text, changed only through the claims-review gate.

### 14.6 Model and inference settings

| Setting | Value | Why |
|---|---|---|
| Temperature | 0.3 | Enough variation to avoid identical phrasing session to session; low enough for consistency |
| Max tokens | ~800 | The schema is small; a cap prevents rambling |
| Response format | Structured output / JSON mode | Removes the parse-failure class entirely |
| Model size v1 | 8–30B class, server-side | The reasoning load is light: phrase a named fault into four short paragraphs. A frontier model buys little |
| Model size v2 | 3–8B quantised, on-device | Validator + fallback make the quality drop tolerable; decided at G5 |

Because the deterministic layer does all the analysis, the language task is genuinely small — which is what makes local inference viable, and local inference is what makes the GDPR question mostly disappear.

### 14.7 Evaluation harness

In rough order of how much each will bite:

1. **Numeric fidelity** — validator rejection rate. Target < 2% steady state. If it does not fall, the prompt is under-constrained; that is a prompt problem, not a model problem.
2. **Phrasing and mechanism accuracy** — 30–50 coach-labelled descriptors. Since priority is code-side, this reviews *how* the fault is explained, scored by rubric. Target median ≥ 4/5.
3. **Cue quality** — external-focus rate, single-sentence compliance, actionability. Cheap rubric scoring, separate Swedish and English sets. Swedish is scored by a Swedish-speaking coach, not by translation.
4. **Adoption, with control** — change in the cued metric from session *n* to *n+1*, **minus** the mean change in non-cued flagged metrics for the same athlete. The within-athlete contrast removes regression to the mean, and the suppressed faults supply the control set for free. This is the only evaluation that measures whether the coaching *works* rather than whether it *reads well*, and the sensors make it directly answerable, which is unusual and worth exploiting.

### 14.8 Worked example

Descriptor as §13.1 but with `athlete_language: "en"` and `previous_cue_outcome: "improved"`:

```json
{
  "went_well": {
    "text": "Your poling-to-recovery timing sat mid-band at 53.1 percent and barely moved from baseline — that rhythm is stable now.",
    "metric_ref": "poling_time_pct"
  },
  "priority_focus": {
    "fault": "lumbar_extension",
    "what_happened": "You dropped into lower-back extension 2.4 times per 100 cycles, up from your recent average.",
    "why_it_matters": "Arching at the catch takes load off the trunk muscles and puts it through the lower back, and it costs you the pre-tension you need to drive the handles down.",
    "cue": "At the top of each recovery, stay tall through the chest and let your bodyweight fall through the handles rather than reaching up for them.",
    "metric_ref": "lumbar_extension_per_100"
  },
  "drill": {
    "name": "Short-set catch reset",
    "description": "Four sets of 20 cycles at moderate pace, stopping completely between sets. Restart each set from a deliberate tall catch position.",
    "target": "Keep extension episodes at zero for all four sets."
  },
  "watch": {
    "text": "Your maximum forward lean fell from 71.4 to 65.2 degrees across the session, which usually means the trunk is tiring before the arms.",
    "metric_ref": "fatigue_drift.trunk_lean_thirds"
  },
  "suppressed": ["trunk_lean_decay"],
  "continuity": "The finish-past-the-hips cue from last session held — release position improved."
}
```

Note what the model did *not* do: it did not mention the 8.1% symmetry index (below the 10% flag, so not a fault), did not stack lean decay into the priority focus (it went to `watch`), and every numeral traces to a named field in the descriptor.

---

# PART IV — THE APPLICATION

## 15. Screens, flows, and interaction

### 15.1 Screen inventory

| # | Screen | Purpose | Source of truth |
|---|---|---|---|
| A1 | Home | Last session card, start button, sensor battery summary | Local DB |
| A2 | **Sensor setup / donning** | Body silhouette with four sites, per-sensor status, battery, L/R swap, sync-tap prompt | L1 transport |
| A3 | **Calibration** | Five steps, live pass/fail, repeat prompts | M3 |
| A4 | **Live session** | Three signals + peripheral HR + audio state | L2/L3 |
| A5 | Session pause / end | Confirm, end-of-session sync tap prompt | — |
| A6 | Processing | Logbook fetch, backfill, analysis progress | L5/L6 |
| A7 | **Session report — summary card** | Went well · one focus · drill · "N more items" | M12 + M11 |
| A7e | **Session report — escalation state** | Fixed referral card above conservative content | Escalation rule |
| A8 | Full report | The eight sections | M12 |
| A9 | History / trends | 30-day metrics, cue ledger, personal bests | Local DB |
| A10 | Settings | Cue fading, audio, language, rate mode, coaching on/off, data & privacy | — |
| A11 | Onboarding | Placement videos, first-session guided mode | — |

Bolded screens exist as mockups already and are specified below.

### 15.2 A2 — Sensor setup

Body silhouette with the four sites marked S1–S4 and labelled with site and strap type ("Sternum · chest belt", "Sacrum · waist belt, midline"). Per-sensor row beneath: status dot, serial, role, battery. Amber state for a connecting sensor; green when streaming.

Two details carry disproportionate weight:

- **Software L/R swap.** A one-tap control on the forearm rows. Wrong-limb mounting is common and this is the cheap fix; without it the athlete re-straps, and some fraction simply stops using the product.
- **Sync-tap instruction**, shown only when all four are green: *"tap the ergometer frame firmly 3 times with both hands to sync clocks."* Concrete, physical, unambiguous. Sync quality depends on this being done properly, so the instruction is a first-class UI element and not a tooltip.

Header states the tier and sensor count so the athlete always knows what configuration they are in.

### 15.3 A3 — Calibration

Step counter ("step 3 of 5"), a five-segment progress bar with per-step colour (passed / active / pending), the instruction in one sentence of plain language ("Do 5 slow, full-range poling cycles. No force — just the movement."), a live cycle counter, and a per-check result list (gyro bias · pass, upright pose · pass, axis variance 84% · measuring).

Showing the *variance percentage while measuring* rather than a spinner is deliberate: it makes the pass criterion legible, so a repeat feels like a near-miss rather than an arbitrary rejection. Footer carries the live sensor/sync status.

### 15.4 A4 — Live session

Dark background — the athlete is looking at this in peripheral vision under gym lighting. Top border coloured by HR zone. Posture ring dominant, with the target band drawn as a green arc segment and the current value as a filled marker; the numeric angle is present but secondary to the colour. Symmetry bar below with centre mark and dead-band. Cadence number large, with its target range as small text, only when prescribed. Audio state on one line at the bottom, including the current fading percentage.

Nothing else. Elapsed time and zone label are the only text permitted in the header.

### 15.5 A7 — Session report card

Three coloured blocks in fixed order — **went well** (green), **one focus** (amber, headed with the fault name in the athlete's language, e.g. "ONE FOCUS · SVANK"), **next drill** (neutral) — with the cue set apart in italic quotation inside the focus block, because the cue is the one line the athlete should be able to retain.

Below them, a single quiet line: *"2 more items in full report"* with a chevron. Suppressed faults are never expanded here. This is the rendering of §14.2's `suppressed` array, and its restraint is the whole point.

### 15.6 A7e — Escalation state

When the escalation rule fires, the card changes shape:

- A red-bordered **"worth getting checked"** block renders first, with the fixed template text, and two actions: *share session data* and *log pain*.
- The drill block is **replaced** by a dashed neutral block: *"No drill this week. Train easy and keep sessions short until you've been assessed."*
- The focus block becomes an observational **"what we saw"** block — no cue, no instruction.
- Went-well is retained: an athlete being told to see a physio still deserves to know what they did well.

The visual hierarchy is the safety mechanism. If a future design change moves the referral card below the coaching content, that is a regression in a safety behaviour, not a layout preference — flag it in review.

### 15.7 Settings

Cue fading schedule (auto/manual with level), audio cue toggles per cue type, cadence target, language (sv/en), sampling mode (52/26 Hz with the trade-off stated in one line), coaching layer on/off, escalation notifications, data and privacy (export, delete, raw-archive opt-in, coaching-inference disclosure).

### 15.8 Onboarding and first-session mode

Placement videos keyed to each site on the silhouette, watchable from setup at any time. First-session guided mode carries denser explanation of what each live signal means, fading over subsequent sessions on the same schedule as the audio cues. First report includes a short "how to read this" overlay, once.

### 15.9 Accessibility and localisation

Full Swedish and English across UI, report, coaching output, and validator phrase lists. Colour is never the sole carrier of state — every colour-coded element also carries position, shape, or text (the posture ring's marker position; the symmetry bar's offset; icons on report blocks). Dynamic type respected on all non-live screens; the live screen has a fixed large-type layout by design. Audio cues have a distinct-timbre requirement rather than distinct-pitch, which also serves hearing-impaired users better.

---

## 16. Data model and storage

### 16.1 Local schema

```
athlete            (id, level, language, created_at, settings_json)
sensor             (id, serial, site, last_seen, battery_pct, fw_version)
calibration        (id, athlete_id, created_at, protocol_version, json, overall)
session            (id, athlete_id, calibration_id, mode, rate_hz, config_version,
                    started_at, ended_at, duration_s, status)
cycle              (session_id, idx, side, t_plant_ms, t_release_ms, valid,
                    reject_reason, <feature columns…>)          -- the §8.2 table
session_metric     (session_id, name, value, sd, band_lo, band_hi, status,
                    provenance, delta_vs_baseline, suppressed, suppress_reason)
fault_event        (session_id, fault, t_start_ms, t_end_ms, magnitude)
quality            (session_id, sync_error_ms, dropout_pct, calibration_ok,
                    rejected_pct, magnetic_index, slip_events_json)
descriptor         (session_id, json, built_at)
coaching           (session_id, source ENUM(llm, fallback), json, validator_log,
                    attempts, model_id)
cue_ledger         (id, session_id, fault, metric, cue_text, outcome, evaluated_at)
baseline           (athlete_id, metric, mode, mean_30d, sd_30d, updated_at, n)
raw_archive        (session_id, sensor_id, path, retained_until)   -- opt-in only
```

`cycle` is the largest table: ~2,000 rows per session, ~40 columns. At 5 sessions/week that is comfortably within on-device SQLite for years, and it is what makes the replay harness and any future re-analysis possible.

### 16.2 Files

```
/sessions/<session_id>/
  raw/S1.bin S2.bin S3.bin S4.bin      # opt-in retention only
  logbook/…                            # fetched, deleted after reconciliation
  ensemble.json
  report.pdf                           # generated on demand
  descriptor.json
```

### 16.3 Retention, export, deletion

- Per-cycle and aggregate data retained indefinitely on device; raw archives default to 30 days unless pinned.
- Export is athlete-initiated: CSV/JSON, PDF report, or a single-session share.
- **Delete session** removes rows and files including the descriptor and coaching record; **delete all data** additionally clears baselines and the cue ledger. Both are one action with one confirmation, and both are exercised in the migration test suite.
- Coaching inference sends the descriptor only — never raw signals, never a name, with an opaque athlete key rotated on request.

---

## 17. Engineering practice

### 17.1 Stack

One codebase, strongly preferred at this team size: **Flutter or Kotlin Multiplatform**, decided in Phase 0 on the strength of the BLE abstraction each offers against the target device matrix. The signal-processing core (M2–M10, M12) is written once as a **pure, dependency-light module** — Dart or Kotlin respectively — with no I/O, no platform types, and no clock access, so it runs identically in the app, in tests, and in the offline replay harness.

### 17.2 Threading and pipeline

- BLE callbacks land on a transport isolate/thread and write into per-sensor ring buffers with device timestamps.
- A fixed-rate pump drains buffers, applies the clock model, and pushes aligned frames to L2.
- L2–L4 run on a single analysis isolate; live view subscribes to a throttled stream (≥ 20 Hz is ample for a colour ring).
- L5–L6 run once at session close, off the UI thread, with a progress screen (A6) because logbook fetch can take tens of seconds.
- Back-pressure policy: if the analysis isolate falls behind, live-view updates are dropped, never analysis frames. A stuttering ring is acceptable; a gap in the record is not.

### 17.3 Repository layout

```
/core          # pure analysis: timesync, calibration, orientation, events,
               # features, session, faults, bands, descriptor, report-model
/app           # UI, navigation, settings, localisation
/transport     # BLE, Movesense wrappers, logbook
/coach         # prompt assembly, inference client, validator, fallback templates
/config        # reference-band config, corpus, versioned, with CHANGELOG
/harness       # replay tool, golden sessions, eval runner
/studies       # analysis notebooks and scripts for Studies 1–4
```

### 17.4 Testing

| Level | What | Gate |
|---|---|---|
| Unit | Every pure module; table-driven for faults and gates | CI on every commit |
| Property | Angle conventions, symmetry sign, cycle segmentation invariants | CI |
| Golden replay | Fixed raw archives → expected features and report model, byte-comparable | CI; diffs require justification in the PR |
| Descriptor path coverage | Every gate × cascade branch × scope × continuity outcome | CI, 100% branch |
| Validator adversarial | Hand-built model outputs that *should* fail each of the five checks | CI |
| Device matrix | 3 phones minimum, 40-minute sessions, arm-sweep conditions | Nightly / pre-release |
| Fault injection | Sensor death, reconnect storm, logbook corruption, thermal throttle | Pre-release |

**The replay harness is built in Phase 0, not later.** It turns every subsequent algorithm change from a risk into a measurement.

### 17.5 Instrumentation

On-device diagnostic log (opt-in to share): gate outcomes, calibration attempts and failures per step, dropout and sync residual per session, validator failures with descriptors, live-view frame drops, session abandonment point. This is the data that tells you whether the product works in the field, and it is deliberately about the *system*, not the athlete.

### 17.6 Documentation as a deliverable

Because the bus factor is real (§21), three documents are maintained alongside code and are release-gating: this specification, the config CHANGELOG with evidence citations, and a user-facing **"what we measure and how accurately"** page derived directly from Studies 1–3. Publishing your own error bars is both honest and, in this market, a differentiator.

---

# PART V — PROGRAMME

## 18. Validation studies

Sequenced so each study gates what the product is allowed to claim. Run in parallel with build, from ~T0+12 weeks.

**Study 1 — Orientation accuracy (weeks 12–20).**
Movesense against optical mocap (or Xsens) during ergometer double poling at three intensities, n ≈ 10. Targets: trunk and lumbo-pelvic RMSE < 5°. Report **Bland–Altman limits of agreement**, not RMSE alone.
*Pre-committed consequence:* RMSE > 8° on any headline angle → live display switches from absolute-angle zones to ROM-relative zones and bands widen. This is a **config change, not a code change**, because bands live in the versioned config — which is the practical payoff of §10.

**Study 2 — Event timing (weeks 16–24).**
Ergometer cord tension or pole force as reference. Targets: plant/release within ±10 ms; L–R offset error < 8 ms.
*Consequence:* fail → timing symmetry demoted from headline to full-report-only, and the live symmetry bar driven by drive-velocity SI alone.

**Study 3 — Rate sensitivity (weeks 20–26).**
Record at 208 Hz, decimate to 104/52/26, quantify per-metric degradation.
*Output:* the empirical suppression list for 26 Hz mode, with error bars, written into the config. This turns the endurance mode from an assumption into a characterised trade-off.

**Study 4 — Learning and retention (months 7–12, after G4).**
Does one cue per session change technique, and does the change survive a no-feedback retention session? Randomise cue-delivery order across athletes where feasible. Primary outcome: the within-athlete non-cued-metric contrast from §14.7. The **no-feedback retention session is the honest test**, per the guidance hypothesis — concurrent feedback can produce performance that vanishes when the feedback does.

This is the study that determines whether the product *works*, as distinct from whether it *measures*.

**Ethics.** Studies 1–3 are method validation with healthy volunteers. Study 4 is an intervention with repeated health-adjacent data collection — budget time for ethical review (Etikprövningsmyndigheten, via an academic partner if run in Sweden) **before month 6**, because it sits on the critical path for a study that starts in month 7.

---

## 19. Regulatory, data protection, and AI transparency

### 19.1 Regulatory boundary

As designed — technique and performance feedback, no diagnosis, templated escalation to human professionals — the product sits in the fitness/wellness space outside EU MDR scope. That boundary is **claim-dependent and jurisdiction-dependent**, and it moves the moment marketing language implies injury prevention. Three standing rules keep it where it is:

1. **Marketing and UI copy never claim injury prevention, treatment, or diagnosis.** The escalation card's "this app measures movement — it can't assess your back" is load-bearing text, frozen and change-controlled.
2. **Any proposed claim touching injury or rehabilitation triggers a formal regulatory review before publication**, with the borderline analysis documented along MDCG 2019-11 lines.
3. **The svank signal is framed as a technique and load pattern, never as a pathology indicator** — in the UI, the report, the coaching corpus, and the marketing site alike.

This is a flagged boundary, not a regulatory determination; formal advice is budgeted in §22.

### 19.2 GDPR

HR/HRV and movement data tied to an identifiable athlete are health-adjacent. Architecture commitments, made in Phase 0 so nothing needs retrofitting:

- On-device storage by default; no account required.
- Export and any cloud inference use **pseudonymised descriptors only**, never raw signals.
- DPIA drafted in Phase 0 and maintained; the local-vs-cloud coaching decision at G5 is taken with it on the table.
- Retention and deletion controls in the app from v1, tested like any other feature.

### 19.3 AI Act

A wellness coaching feature of this kind is not high-risk under Annex III, but transparency obligations apply: the athlete is told the coaching text is AI-generated, and the deterministic fallback is disclosed and switchable. Document the classification rationale once; revisit if claims or scope change.

---

## 20. Implementation plan

**Timeline basis:** T0 = project start. Durations assume one full-time engineer plus part-time signal processing, design, and study coordination. Less capacity stretches the calendar proportionally; **the ordering and the gates do not change.**

### 20.1 Workstreams

| # | Workstream | Owner profile | Active |
|---|---|---|---|
| W1 | Sensor platform and BLE | Embedded/mobile | Phases 0–2, 6 |
| W2 | Signal processing (calibration, Mahony, events, features) | Biomech/DSP | Phases 0–3, validation |
| W3 | Mobile app | Mobile eng + designer | Phases 1–6 |
| W4 | Deterministic analysis and report | Backend/DSP | Phases 2–4 |
| W5 | LLM coaching layer | ML eng | Phases 4–5 |
| W6 | Validation studies | Research lead + lab partner | Parallel, gated |
| W7 | Data protection and regulatory | Advisory, part-time | Phases 0, 4, 6 |

### 20.2 Phase 0 — Foundations and de-risking (T0 → +6 weeks)

Retire the three risks that would invalidate everything downstream: BLE concurrency, time sync, clipping.

**W1 — Bench validation.** Procure 6 sensors (4 + 2 spares), HR+ belt, straps. Concurrent-link test: four sensors streaming IMU6/52 on the real device matrix (recent Android flagship, mid-range Android, iPhone), measured **under arm-sweep conditions at an actual ergometer, not on a desk**. Pass: < 2% packet loss over 30 minutes on all three. Confirm ±16 g takes effect and log raw plant transients to verify no forearm clipping. Enable DataLogger in parallel with streaming; verify Logbook readout and gap reconciliation on real dropouts.

**W2 — Sync pipeline.** Per-sensor clock model (offset + skew, lower-envelope regression) and sync-tap fiducial detection. Validate residual against tap fiducials at start *and* end of 40-minute sessions. Pass: **< 5 ms**.

**W2 — Replay harness.** Raw archive format, deterministic replay of the analysis chain, golden-session infrastructure. Built now because everything after depends on being able to change algorithms safely.

**W3 — App skeleton.** Flutter vs KMP decision; BLE abstraction; local session storage schema.

**W7 — Data protection groundwork.** Data inventory and DPIA draft: what is collected, where it lives, retention, athlete rights.

> **Gate G0 (week 6).** BLE concurrency pass on all three target devices **and** sync residual < 5 ms. Fail on BLE → drop to 3 concurrent links + logbook backfill for the fourth, or change target hardware — **before writing any dependent code.**

### 20.3 Phase 1 — Core capture (T0+4 → +12 weeks)

**W2 — Calibration protocol.** All five steps with explicit pass/fail and repeat prompts. Build the functional-axis step (Step 3) first and **test it on at least five different people**, because inter-individual movement style is what breaks planar assumptions and it will not surface on one developer's body. Slip detection during quasi-static recovery instants; 45-minute re-zero; forced recalibration on reconnect.

**W2 — Mahony, host-side.** Core filter with adaptive Kp gating and Ki freeze, unit-tested against the recorded plant transients from Phase 0. Quaternion-to-angle pipeline with the §7.5 conventions. Per-cycle yaw re-anchoring, τ ≈ 10 cycles.

**W3 — Setup and calibration UI.** Screens A2 and A3 per §15.2–15.3, including the software L/R swap and the sync-tap instruction.

> **Gate G1 (week 12).** A full 40-minute session captured end to end: calibration passes, angles are physiologically plausible, streamed and logged records reconcile, session persists and reloads. **No metrics yet** — just trustworthy signals.

### 20.4 Phase 2 — Metrics and deterministic report (T0+10 → +18 weeks)

**W2 — Event detection.** Four-state machine per side; two-stage plant detection with parabolic sub-sample refinement; release detection; rejection rules.

**W4 — Feature extraction.** The full §8.2 set. Per-cycle rows, session aggregates, thirds, cycle-to-cycle SD.

**W4 — Reference-band config.** The versioned object per §10, seeded from literature with honest provenance tagging, personalised from calibration Step 4 where recorded. **All thresholds move here in this phase** — this is the last comfortable moment to do it.

**W4 — Descriptor generator.** Its own tested module, carrying the four revisions: structural suppression, code-side priority, grounded continuity, coaching scope.

**W4 — Deterministic report.** All eight sections, rendered with no LLM. Greying rather than hiding. Export paths.

> **Gate G2 (week 18).** Ten sessions from ≥ 3 athletes produce reports a coach judges plausible and internally consistent; the descriptor generator passes its full path-coverage suite.

### 20.5 Phase 3 — Live feedback (T0+16 → +22 weeks)

**W3 — Three-signal display** per §11.1, with the latency budget instrumented and enforced in test, not assumed. 26 Hz mode as a labelled degradation.

**W3 — Audio cues** per §11.3, including the fading schedule and its settings exposure.

> **Gate G3 (week 22).** Athletes complete a hard session using only the live display and audio, and in interview correctly recall what each signal meant. **If they cannot decode it at intensity, simplify further** — that is the intended response, not a note for later.

### 20.6 Phase 4 — Coaching layer (T0+20 → +26 weeks)

**W5 — Prompt, corpus, contract** per §14.1–14.2; mechanism-notes retrieval keyed on the fault, injected in the user message for cache friendliness; corpus versioned alongside the band config.

**W5 — Validator** — all five checks, with per-field numeric provenance and both decimal conventions; retry-once then fall back; every failure logged with its descriptor.

**W5 — Deployment.** Server-side 8–30B class, pseudonymised descriptors, DPIA updated. On-device option specified but deferred to G5.

**W5 — Evaluation harness** per §14.7, with the coach-labelled descriptor set built during this phase.

**W7 — Regulatory checkpoint.** Escalation text frozen; claims reviewed against §19.1.

> **Gate G4 (week 26).** Validator rejection < 5% on the eval set; coach rubric ≥ 4/5 median on phrasing and cues; **zero clinical-language escapes**; escalation template renders correctly in every trigger path with conservative scope verified.

### 20.7 Phase 5 — Pilot (T0+26 → +34 weeks)

8–12 athletes, mixed recreational and trained, six weeks of self-directed use, ≥ 2 sessions/week.

Instrumented for: session completion rate, calibration first-pass rate, live-signal comprehension, validator failure rate in the wild, cue-adoption contrast, escalation trigger behaviour, and **the support burden of sensor logistics** — batteries, straps, pairing — which is where wearables products actually die.

Weekly triage of validator failure logs into prompt and config revisions. Config version bumped, never hot-edited.

> **Gate G5 (week 34).** Go/no-go on productisation, plus the four deferred decisions **with their evidence**: Tier A vs more sensors (Studies 1–2 + pilot demand; default is ship four); seventh-sensor identity (deferred until an on-snow product is real); on-device Mahony (earliest v2, after raw-data needs are satisfied); cloud vs local LLM (pilot quality + DPIA; local 3–8B is the target if quality holds).

### 20.8 Phase 6 — Hardening and v1 release (T0+34 → +42 weeks)

Stability: reconnection storms, battery death mid-session, logbook reconciliation edge cases, thermal throttling on long sessions. Accessibility and localisation, including per-language validator lists. Onboarding: strap-fitting and placement videos keyed to the donning screen; first-session guided mode. Documentation: the user-facing "what we measure and how accurately" page from Studies 1–3.

### 20.9 Schedule and critical path

| Phase | Weeks | Gate |
|---|---|---|
| 0 Foundations | 0–6 | G0 |
| 1 Core capture | 4–12 | G1 |
| 2 Metrics + report | 10–18 | G2 |
| 3 Live feedback | 16–22 | G3 |
| 4 Coaching layer | 20–26 | G4 |
| 5 Pilot | 26–34 | G5 |
| 6 Hardening | 34–42 | Release |
| Studies 1–3 | 12–26 | Feed config |
| Study 4 | months 7–12 | Post-release evidence |

**Critical path: G0 → G1 → G2 → G4.** Live feedback (Phase 3) and the validation studies parallelise off it. The two things most likely to move the end date are a G0 failure on BLE concurrency and ethics approval slipping for Study 4.

---

## 21. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| BLE concurrency unreliable on common phones | Med | High | G0 bench test before dependent work; logbook backfill as structural fallback; 3-link fallback configuration |
| Functional-axis calibration fails on diverse movers | Med | High | Test on ≥ 5 people in Phase 1; fallback to assumed-alignment mode with widened bands |
| Orientation accuracy misses the 5° target | Med | Med | Pre-committed consequence rule: ROM-relative zones, config-only change |
| Sensor slip mid-session unnoticed | Med | Med | Quasi-static slip detector, greyed metrics, data-quality section |
| One bad coaching report erodes trust | Low–Med | High | Structural suppression, per-field validator, deterministic fallback, weekly pilot log triage |
| Scope creep into medical claims | Med | High | Standing rules §19.1; claims review gate; escalation text frozen |
| Sensor logistics kill retention | High | Med | Pilot measures support burden explicitly; CR2025 life budget; donning UX investment |
| Single-engineer bus factor | High | Med | Pure core, config-driven thresholds, replay harness, versioned artefacts, this document |
| Ethics approval delays Study 4 | Med | Med | Submit before month 6; Study 4 sits outside the release path by design |
| Qualitative misrepresentation passes the validator | Med | Low–Med | Documented residual risk; human review set; monitored, not assumed away |

---

## 22. Resourcing

Minimum viable team: **1.0 FTE** engineer (mobile + pipeline), **0.4 FTE** signal processing/biomechanics, **0.2 FTE** design, **0.2 FTE** research coordination, plus advisory hours for regulatory and GDPR. Lab access for Studies 1–2 (mocap and a force reference) through an academic partnership.

Hardware is modest: ~10 sensors, straps, three phones for the device matrix, ergometer access. The real costs are lab time, ethics-review lead time, and the advisory hours — none of which compress well, which is why they start early.

Total to v1 release: **~42 weeks** at this capacity, with Studies 1–3 inside the envelope and Study 4 extending beyond it.

---

## 23. Open decisions

Deliberately unresolved, each with an owner, a decision point, and the evidence that will decide it.

| # | Decision | Decided at | Evidence | Default if evidence is ambiguous |
|---|---|---|---|---|
| 1 | Tier A vs adding sensors | G5 | Studies 1–2 accuracy; pilot demand for elbow feedback | **Ship Tier A.** Easier to add sensors to a working system than to remove them from a product people have bought |
| 2 | Seventh sensor: thigh vs pole | Deferred | Only meaningful once an on-snow product exists | Thigh — hip/knee flexion discriminates skill where elbow ROM does not |
| 3 | On-device vs host-side Mahony | G5 (earliest v2) | Battery data from pilot; whether raw-data needs (classifier, validation) are satisfied | Host-side. Do not discard raw data while metrics are still being decided |
| 4 | Cloud vs local LLM | G5 | Pilot quality data + DPIA | Local 3–8B if quality holds; the validator and fallback make the drop tolerable |
| 5 | Flutter vs Kotlin Multiplatform | Phase 0 | BLE abstraction quality on the device matrix | Whichever gives the better BLE story; one codebase either way |
| 6 | Ergometer pairing (work/distance) | Phase 2 | Availability of a usable SkiErg interface | Ship without it; the technique metrics do not depend on it |

---

## Appendix A — Unified threshold table

Every number that gates a behaviour. These live in the versioned config (§10) and nowhere else as authoritative values; this table is the human-readable rendering.

| Domain | Parameter | Value | Consequence if breached |
|---|---|---|---|
| Sampling | Standard rate | 52 Hz | — |
| | Endurance rate | 26 Hz | Wider symmetry dead-band, finest timing suppressed |
| | Accelerometer range | ±16 g | Clipping biases gravity estimate |
| | Gyroscope range | ±1000 dps | — |
| | Connection interval | 15–30 ms | — |
| Sync | Residual sync error | < 5 ms | Timing-symmetry metrics suppressed |
| Dropout | Post-backfill dropout | ≤ 15% | Fatigue-drift metrics suppressed |
| | Packet loss (G0 bench) | < 2% / 30 min | Gate G0 fails |
| Calibration | Gyro SD (Step 1) | < 1 deg/s | Repeat step |
| | Accel magnitude (Step 1) | 1.0 ± 0.03 g | Repeat step |
| | PCA variance (Step 3) | > 80% | Repeat step |
| | Axis perpendicularity (Step 3) | within 30° | Repeat step |
| | Slip threshold | ~8° | Flag slip, grey affected angles |
| | Re-zero interval | 45 min | Prompt |
| Filter | Kp_high | 1.0 rad/s | — |
| | Ki | 0.02 | — |
| | Accel dead-band low / high | 0.05 g / 0.25 g | Kp fades / Kp = 0, Ki frozen |
| | Yaw anchor time constant | ≈ 10 cycles | — |
| Events | Cycle duration bounds | 0.45–2.2 s | Cycle rejected |
| | Minimum plant-to-release | 0.15 s | Cycle rejected |
| | Rejected-cycle limit | ≤ 25% | Session flagged low-confidence |
| Bands (erg, trained) | Trunk max lean | 70–78° | Fault: over-flexion / lean decay |
| | Trunk at plant (start point) | ~42° | Personalisable from Step 4 |
| | Relative poling time | 50–56% | Mode-specific; snow ~27–32% |
| | Lumbar extension episodes | 0–1 per 100 cycles | Fault: svank |
| Symmetry | SI flag | > 10% sustained | Fault: kinematic asymmetry |
| Accuracy targets | Trunk / lumbo-pelvic RMSE | < 5° (fallback at > 8°) | ROM-relative zones |
| | Plant/release timing | ±10 ms | Timing demoted to full report |
| | L–R offset error | < 8 ms | Symmetry bar on SI only |
| Coaching | Validator rejection (steady state) | < 2% | Prompt work |
| | Escalation trigger | svank above band in ≥ 4 of last 6 sessions | Conservative scope, referral card |
| | Temperature | 0.3 | — |

## Appendix B — Glossary (SV/EN)

| Swedish | English | In this system |
|---|---|---|
| stakning | double poling | The technique family |
| stakmaskin | double-poling ergometer / SkiErg | The v1 mode |
| svank | lumbar extension / lower-back arch | The safety-relevant load pattern; **never** described as pathology |
| bålen | the trunk / core | Cue vocabulary |
| frånskjut | kick / leg push-off | Tier C only |
| åkekonomi | skiing economy | Coaching vocabulary |
| diagonalåkning | diagonal stride | Out of v1 scope |
| enkeldans / dubbeldans | skate V2 / V1 | Out of v1 scope; asymmetric by nature |

## Appendix C — Change log for this document

| Version | Date | Change |
|---|---|---|
| 1.0 | — | Consolidation of system design, development plan, and coaching prompt package; conflicts resolved per §0.3; app specification (§15–17) added; unified threshold table added as Appendix A |
