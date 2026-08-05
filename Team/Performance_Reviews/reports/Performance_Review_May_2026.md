# Performance Review

## Period: 2026-03-30 to 2026-05-01 (25 weekdays / 5 weeks)
## Generated: 2026-05-05
## Team: 3 active members (Assia Madani, Khadidja Cheurfi, Sidali Bedrani)
## Repos: wergonic-flutter, wergonic-web-apps, wergonic-django-backend, wergonic-landing-page (all `dev` branch + all branches via `--all`)

> Note: Abdelkader Barhoumi appears as assignee on 12 tasks early in the period (last activity 2026-04-03) but is **not in the TEAM MEMBERS section** of the export — likely no longer with the company. His tasks/commits are summarized at the end for context but he is not included in the active team review.

---

## Executive Summary

**Team health: Concerning, driven almost entirely by Assia.** Sidali is the only active developer whose declared hours, task list, and code commits line up cleanly. Khadidja's design output exists but is poorly scoped and her hour gap is large. Assia's situation is the most serious finding of this period: she logged ~85 tasks across 3 repos but **only 7 unique tasks (≈9%) have commits that can be traced to them**. At least one task (WH-179 "Remove db.sqlite3") is marked Ready to Deploy but the file is verifiably still in the repo on every branch.

**Top concerns:**
1. **Assia: 91% of her code tasks have no traceable commit** — 75 declared code tasks vs. 12 commits across all 3 backend/web/landing repos, only 7 of which are WH-tagged. Either the work is not happening, is being done locally without push, or is logged without being implemented. WH-179 is provable evidence of the latter.
2. **Khadidja: 22.5h unexplained gap** beyond reasonable meeting time. She also splits design work into many 1–3h granularity items with vague titles ("updated the landing page assets", "finished updating landing page" same day) — pattern consistent with artificial splitting under the 4h-cap rule.
3. **Sidali: high file-level churn on BLE infrastructure** — `ble.data.repository.dart` modified in 15 commits in 5 weeks, plus 9 commits on `sensor_connection_cubit.dart`. This continues the pattern from the March audit. He is a clear bus-factor-of-1 risk on the BLE stack.
4. **Backfill / batch-creation pattern in Assia's task list** — 18 tasks created on a single day (2026-04-30) covering supposed earlier work, and a separate batch of 13 tasks created on 2026-04-08 with `latest_log_date` of 2026-03-30. This is consistent with end-of-period catch-up logging rather than real-time tracking.

**Standout positive:** Sidali's WH-165 commit (`40cf2dcf`) introduces a new BLE connection state machine with proper enum types, separated services, and **396 lines of unit tests** — significantly above the team's typical test discipline. This is the kind of work the 4h-task system makes hard to capture; he should be credited for it.

---

## Team Overview

### Hours & Attendance

| Name | Type | Weekly Hrs | Expected | Leave-Adj. | Logged | Missing | Reasonable Mtg. | Unexplained Gap | Flag |
|---|---|---|---|---|---|---|---|---|---|
| Sidali Bedrani | Full-time | 40 | 200 | 176 | 165.5 | 10.5 | 10.0 | **0.5** | ✓ |
| Assia Madani | Full-time | 30 | 150 | 132 | 114.75 | 17.25 | 7.5 | **9.75** | ⚠️ |
| Khadidja Cheurfi | Part-time | 20 | 100 | 100 | 72.5 | 27.5 | 5.0 | **22.5** | ⚠️⚠️ |

Reasonable meeting time = 5 weeks × 2h/week, scaled by `weekly_hours / 40`. Khadidja's leave_balance is **-7 days** (she has used more leave than she has accrued historically — unrelated to this period but worth flagging in her review).

### Process Compliance

| Name | Code Tasks (non-research, non-design) | Tasks w/ Linked Commits | Compliance % | Commits w/o WH-ID | Type Accuracy |
|---|---|---|---|---|---|
| Sidali Bedrani | 23 | 16 | **70%** | 1 of 25 (4%) | Mostly OK; 1 typo (WH-130 ≠ existing task) |
| Assia Madani | ~75 | ~7 tagged (10–17 if untagged commits inferred) | **9–22%** | 5 of 12 (42%) | Many `improvement` typed tasks should be `bug` (e.g. WH-115, WH-116) |
| Khadidja Cheurfi | 0 (design-only) | N/A | N/A | N/A | OK (all `improvement` is correct for design iteration) |

### Scoring Summary (1–10, 7 = mid-level expectation)

| Name | Code Quality | Bug Rate / Output Quality | Time Justification | Process Discipline | Overall |
|---|---|---|---|---|---|
| Sidali Bedrani | 7 | 5 (high churn, but complex domain) | 8 | 6 | **6.5** |
| Assia Madani | 7 (where visible) | N/A insufficient data | **3** | **2** | **3.5** |
| Khadidja Cheurfi | N/A | 5 (vague task descriptions) | **4** | 5 | **4.5** |

---

## Sidali Bedrani — Mobile Lead

### Hours Analysis
- Expected (leave-adj.): 176h. Logged: 165.5h. Missing: 10.5h.
- Reasonable meeting time at full-time × 5 weeks = 10h. **Unexplained gap: 0.5h. On target.** ✓
- Took 3 "other" leave days in the period.

### Task Summary
- 35 tasks total. Type breakdown: 11 bug, 13 improvement, 9 research, 2 feature.
- Total hours declared on his tasks: ~135h (across all his tasks visible in CSV). The remainder of his 165.5h logged is presumably on items not in this Testing/Ready-to-Deploy/Deployed slice (e.g. ongoing work still in earlier statuses).
- Workload is heavily BLE / sensor connection oriented, which is consistent with him being the mobile lead and with the March audit's finding.

### Commits & Process Compliance
- 25 non-merge commits in `wergonic-flutter`. 23 contain a `[WH-xxx]` tag (92% commit-level compliance — good).
- 1 commit without WH-ID: `a9764095` "feat: sentry on blind spot" (2026-04-17). Likely belongs to WH-138 BLE-stack-fixes work.
- 1 commit with a non-existent WH-ID: `e6f7b83e` "fix:[WH-130] add steps when limbs reconnect" — WH-130 does not exist in the CSV; content suggests this should be WH-129.
- Tasks WITH commits (16): WH-167, 165, 154, 140, 138, 129, 128, 127, 118, 112, 111, 106, 98, 58, 11, 22 (joint with Abdelkader — Abdelkader's commits cover the actual code).
- Code-task tasks WITHOUT any commit (10):
  - **Bugs missing commits:** WH-144 (5h, urgent), WH-114 (2h), WH-78 (2h), WH-34 (2h), WH-33 (1h)
  - **Improvements missing commits:** WH-113 (2h), WH-68 (2h)
  - **Defensible (review/planning/non-code):** WH-57 (3h, "retest PRs"), WH-48 (4h, "checked tested merged"), WH-47 (4h, "planning")
- The 5 missing-bug-commit cases are the ones to ask about. 2h–5h declared without any visible code change is unusual on a team using AI assistance.

### Work Review (key tasks)

| WH-ID | Title | Hours | Commits | Verdict |
|---|---|---|---|---|
| WH-165 | global auto reconnect | 3h | `40cf2dcf` (1770+/-60, 18 files, includes new state machine + 396 lines of tests), `ac64257f` (translations) | **Justified — undervalued, actually.** This is a substantial architecture commit (`ble_connection_controller.service.dart`, `connection_attempt_executor.service.dart`, new enums for `connection_phase`, `connection_rung`, `connection_trigger`, `give_up_reason`). 3h is light for what landed. Either real time was higher or significant prep happened off-task. |
| WH-167 | recovering stream when limb reconnects | 6h | `a1cbec73` (logs), `7301fe4d` (fix) | **Justified.** Combined diff modest (130 lines) but the bug class (stream recovery during reconnect) requires testing on physical sensors — small diff, real debugging time is plausible. |
| WH-154 | visual to calibration when sensors connected | 4h | `1208b094` (625+/-38, 9 files), `20cb1cde` (sheet, 127 lines) | **Justified.** Multiple UI surfaces, real complexity. |
| WH-58 | investigate pairing problem | 10h | `0684bde9` (106 lines), `85cf732a` (250+/-220, 12 files inc. translations + injectable.config) | **Justified for research+impl.** This was research-typed but resulted in real code (delay between cleaning and reconnect, pairing step enum). |
| WH-129 | reconnection in calibration/pairing | 4h | 3 commits, 125 lines total | **Justified.** Consecutive iterations on real bug. |
| WH-71 | tested with new changes / reproduce bug | **14h** | None (research) | **Unclear.** 14h is the largest research declaration in the period. No deliverable visible. Worth asking what came out of this. |
| WH-58/96/45/46 | research cluster on offline/online + pairing | 24h combined | None (research) | **Unclear-but-defensible.** Research is allowed without commits but 24h of "investigate / analyze / search" on related topics in the same person warrants a check on what artifacts (docs, decisions) came out. |

### Duplicate / Split Tasks
- **WH-129 (urgent bug, 4h) + WH-129 fix follow-up + WH-138 BLE stack fixes (high bug, 2h) + WH-118 (urgent bug, 2h) + WH-128 (urgent improvement, 1h) + WH-127 (medium improvement, 2h) + WH-111 (urgent bug, 3h) + WH-112 (urgent bug, 2h)** — these are all touching the same BLE reconnection / pairing concern within a 5-day window (Apr 16–Apr 21). Some splitting is legitimate (different files / different facets), but the cluster as a whole is one initiative. Combined: ~16h. Not artificial — but visualizing them as one program of work would be more honest.
- **WH-176 (2h) + WH-167 (6h) + WH-188 (4h)** — research+fix+research on stream cascading bug, same week. 12h combined. Legit because reconnection is genuinely hard to debug.
- **WH-46 + WH-47 + WH-45** on 2026-03-31 — analyze, plan, analyze offline/online (all created same minute, all by Sidali, 5+4+5=14h declared but logged at end-of-period). Looks like backfilled reflection rather than real-time logging. Worth confirming what artefact resulted (the audit report referenced in WH-137 may be it).

### Task Type Issues
- WH-137 typed as `bug` but title is "analyze and created a report for the branch farhad_claude" — should be `research`. Misclassifying analytical work as `bug` distorts bug-rate metrics.
- WH-138 typed as `bug` but description spans 5 separate fixes — looks more like a `feature`-sized chunk of work or 5 separate bugs. Either way, classifying 2h on this is also too low for what's described.
- WH-129 / WH-111 / WH-112 / WH-118 typed `bug` is correct.

### Code Quality (sampled)

**Score: 7/10**

**Good examples:**
- `40cf2dcf` (WH-165): introduces clean enum types (`ConnectionPhase`, `ConnectionRung`, `ConnectionTrigger`, `GiveUpReason`), separates `BleConnectionControllerService` from `ConnectionAttemptExecutorService`, **adds 396 lines of unit tests in `ble_connection_controller_test.dart`**. This is well above team baseline.
- `569250d8` (WH-138): structured fix with clear separation of concerns (Komposti / retry / GATT loop / timer cancel / pairing pipeline lock). Each fix is in the right file.
- `40cf2dcf` removes two now-unused use-case files (`abandon_device.usecase.dart`, `cleanup_all_connections.usecase.dart`) — actively cleans dead code rather than leaving it.

**Concerns:**
- File-level churn (see below) suggests he's iterating on production code under time pressure rather than designing-then-implementing.
- Translation files (`de.json`, `en.json`, `es.json`, `nl.json`, `sv.json`) are touched in 6 commits. There's no separation between feature commits and translation commits — minor process issue but it bloats diffs.

### Code Churn

`lib/features/bluetooth/data/repositories/ble.data.repository.dart` — **15 commits in 5 weeks** (every 1.6 days on average). `sensor_connection_cubit.dart` — 9 commits. `measurements_manager_cubit.dart` — 7 commits.

**Estimated churn: 30–40% (HIGH).** This is the same pattern flagged in the March audit: same file modified again within days. Some of this is legitimate iteration on a hard domain; some is "fix-then-refix" symptomatic of pushing code before testing physically.

### Bug Causation
Insufficient sample: most of his self-fixed bugs in this period are in BLE/reconnection logic where the original code was largely his own (per March audit). For this period specifically:
- WH-129 (`680b17be`): 1-line fix to a blind-spot reconnection — one line, but the bug class is a 🟡 moderate (silent reconnect bypassing UI updates).
- WH-112 (`db674c0b`): "session hangs when a limb disconnect" — caused by a `Completer` that never completes. 🔴 careless if the Completer was his own; 🟡 if inherited. The file mostly has his fingerprints from prior periods, so likely **self-caused careless**.
- WH-167: stream recovery bug introduced by his own WH-165 work the same week. 🟡 moderate.

Pattern continues from March audit: bugs concentrate on reconnection/pairing edge cases that he himself wrote. The complex-domain caveat applies, but he should be testing on hardware before pushing.

### Codebase Ownership
- **Sole owner of the BLE stack** (`features/bluetooth/`, `features/measurements/`, `sensor_connection_cubit`, `measurements_manager_cubit`).
- **Bus factor = 1** on the most complex part of the codebase. Abdelkader's departure removed the only person who was even partly familiar with this area.

### Verdict
**Rating: Adequate — strong technical capability, weak process discipline, bus-factor risk.**

**Strengths:**
- Real architectural work on WH-165 (state machine + tests)
- High commit-level WH-tagging compliance (92%)
- Hour declarations match output, no inflation visible
- Owns the hardest domain in the codebase

**Concerns:**
- 5 bug tasks (WH-144, WH-114, WH-78, WH-34, WH-33) declared 1–5h with zero commits. These are deliverables that aren't visibly delivered.
- High file-level churn on BLE files — same pattern as March audit, no improvement
- Bus-factor-of-1 on BLE; if he is unavailable, no one else can fix urgent BLE bugs
- WH-71 (14h research, no deliverable visible) is the single largest unexplained time sink

**Talking Points for Review Meeting:**
1. **WH-144 was declared as 5h urgent bug ("fix in calibration when the pairing of errored sensors disconnects other limbs") but I can't find a commit. Walk me through how this was fixed?**
2. **WH-71 took 14 hours of testing/reproduction. What did you learn? Is there a write-up or doc?**
3. **WH-165 looks like a major piece of work — 1770 lines, new state machine, tests. Why was this declared as 3h? Did the prep happen on a different ticket?**
4. **`ble.data.repository.dart` was modified in 15 of your 25 commits this month. Are you happy with how this file is structured, or is there a refactor that would let you stop revisiting it?**
5. **What's the plan for de-risking the BLE stack so it isn't a single-person owner area?**

---

## Assia Madani — Web / Backend Lead

### Hours Analysis
- Expected (leave-adj.): 132h. Logged: 114.75h. Missing: 17.25h.
- Reasonable meeting time at 30h/week × 5 weeks = 7.5h.
- **Unexplained gap: 9.75h. ⚠️ Flag.**
- Took 3 "other" leave days.

### Task Summary
- ~85 tasks total in the period. Roughly 75 are code-related (Web / General platform, non-research, non-design).
- Hours per task: **dominated by sub-1h items**. Approx. distribution:
  - 0.25–0.5h: ~25 tasks
  - 1–2h: ~30 tasks
  - 3–4h: ~15 tasks
  - >4h: 2 tasks (WH-110 = 9h, WH-49 = 2h research)
- Total declared on tasks ≈ 110–115h, which roughly matches her logged 114.75h. The math is internally consistent — but the question is whether the tasks themselves are real.

### Commits & Process Compliance

**This is the central finding of the review.**

Across ALL branches in `wergonic-web-apps`, `wergonic-django-backend`, and `wergonic-landing-page`, Assia made **12 non-merge commits** in the 5-week period:

| Repo | Hash | Date | WH-Tagged | Files | Lines |
|---|---|---|---|---|---|
| web-apps | `442640b8` | 04-27 | WH-117 ✓ | 6 | 51/-285 |
| web-apps | `ec24583c` | 04-28 | WH-117 ✓ | 1 | 1/-1 |
| web-apps | `87295adc` | 04-26 | WH-153 ✓ | 2 | 6/-6 |
| web-apps | `17c564e9` | 04-26 | WH-158 ✓ | 10 | 34324/-1071 (lockfile-heavy) |
| django | `293da1a` | 04-30 | WH-177 ✓ | 14 | 1874/-1881 |
| django | `3dc9613` | 04-30 | (untagged duplicate of 293da1a) | 14 | 1874/-1881 |
| django | `622c677` | 04-30 | **untagged** (likely WH-175 + WH-110) | 10 | 12/-32 |
| django | `e763731` | 04-29 | WH-171, WH-169, WH-168 ✓ | 11 | 149/-76 |
| django | `c3d7f13` | 04-09 | **untagged** ("fix build issues") | 1 | -9 |
| django | `d0b653d` | 04-09 | **untagged** ("fix ci-cd pipeline") | 1 | 9/-3 |
| django | `3ad2926` | 04-09 | WH-70 ✓ (also covers WH-7, WH-28 implicitly) | 14 | 862/-964 |
| landing | `3726288` | 04-20 | **untagged** (likely WH-116) | 22 | 179/-129 |
| landing | `182d9b4` | 04-15 | **untagged** (likely WH-99/100/103/104/105/107/108/109) | 90 | 1394/-5938 |

**Tagged tasks visible in commits: WH-117, 153, 158, 70, 168, 169, 171, 177 = 8 unique. Untagged commits plausibly cover up to ~10 more tasks.**

So her best-case task-to-commit compliance is **22% (17/75)**, worst-case is **9% (7/75)**.

**Verifiable evidence the work is not happening:** WH-179 ("Remove db.sqlite3 from repo", 0.5h, status `Ready to Deploy`, declared 2026-04-29). The file `db.sqlite3` is still present in `wergonic-django-backend` on every branch. `git log --diff-filter=D -- db.sqlite3` returns zero results across all branches. The file has not been deleted anywhere. The task cannot be Ready to Deploy.

### Work Review (key tasks)

| WH-ID | Title | Hours | Commits | Verdict |
|---|---|---|---|---|
| WH-179 | Remove db.sqlite3 from repo | 0.5h | **None across all branches; file still present** | **NOT DONE.** Strongest single piece of evidence in this review. |
| WH-194 | Extract AbstractTimestampModel | 0.5h | None | **No commit.** Plausible 30-min refactor — but where is it? |
| WH-192 | Extract a CalculationService | 3.5h | None | **No commit.** 3.5h refactor with zero output is implausible. |
| WH-186 | Migrate URL routing to DRF DefaultRouter | 3h | None | **No commit.** Would touch many `urls.py` files; absence is conspicuous. |
| WH-182 | Offload heavy StatsView calc to Celery | 2h | None | **No commit.** Celery task definitions are visible from WH-70 commit (Apr 9), nothing new in stats area. |
| WH-181 | Add DB indexes (Session, RAMPAssessment, User) | 1h | None | **No commit.** Would need a migration file — none in repo. |
| WH-180 | Replace bare `except Exception:` with specific exceptions | 1h | None | **No commit.** Codebase still has `except Exception:` blocks visible. |
| WH-172 | Move Firebase calls into FirebaseService | 1.5h | None | **No commit.** No FirebaseService class in any branch. |
| WH-170 | Wrap Event get_or_create in transaction.atomic + select_for_update | 0.5h | None | **No commit.** |
| WH-110 | find and clean backend dirty code | **9h** | Possibly `622c677` (12 lines) + `293da1a` (1874+/-1881) | **Partially justified IF** WH-110 is meant to umbrella WH-175 + WH-177 + WH-179 + WH-180 + WH-186 + WH-187 + WH-185 + WH-172 + WH-170 + WH-171 + WH-168 + WH-169. But she also declared each of those individually. **Either WH-110 is the umbrella and the individual sub-tasks are double-counted, or WH-110 is its own work that I can't see.** Worth asking. |
| WH-117 | Fix CI/CD frontend pipeline | 2h | `442640b8` (51/-285), `ec24583c` (1/-1) | **Justified.** Real CI fix. |
| WH-153 | Upgrade axios, xlsx, firebase | 1.5h | `87295adc` (6 lines) | **Justified.** |
| WH-158 | Add `rel="noopener noreferrer"` to external links | 0.5h | `17c564e9` (34324/-1071, mostly lockfile) | **Justified.** Actual change is small + lockfile bump. |
| WH-70 | Session Stuck in processing (bug) | 1.5h | `3ad2926` (862/-964) | **Justified — undervalued.** This commit migrates the entire processing pipeline to Celery (massive change). 1.5h is far too low for what's there. Probably tagged here but represents work spanning multiple tasks. |
| WH-177 | Break up oversized view files | 1h | `293da1a` (1874/-1881, 14 files) | **Justified.** Real refactor. 1h is light for a 14-file split but plausible if done with AI assistance. |
| WH-171/169/168 | Move Firebase to Celery + select_related + N+1 fixes | 2.5h combined | `e763731` (149/-76) | **Justified.** One commit covers all three small backend perf tasks. |
| WH-116 | Fix landing page margins | 3.5h | `3726288` untagged (179/-129) | **Possibly justified.** Touches 22 files of landing page CSS. 3.5h is plausible for global margin/padding work. **But: not WH-tagged.** |
| WH-99/100/103/104/105/107/108/109 | "Enhance Landing X page" cluster (~9 tasks, ~7h declared total) | varies | `182d9b4` untagged (1394/-5938) | **Possibly justified as one batch.** This single commit removes 5938 lines and adds 1394 across 90 files — looks like the entire landing redesign. **But it's a single commit covering 9 separately-declared tasks, none WH-tagged.** Either the work was done as one go and split into 9 tickets after the fact, or each ticket really is separate and the commit is a careless lump. Either way, process is broken. |

### Duplicate / Split Tasks
This is where the pattern is most visible. Examples:

- **2026-04-30 burst — 18 tasks created in a single day**: WH-194, 193, 192, 187, 186, 185, 182, 181, 180, 179, 175, 172, 170, 169, 168, 161 (and a couple more). Most are 0.5–3h "extract X service / move Y to Z / add DB index" type cleanups. Total declared ~22h, but only 2 commits exist on that day and the days around it covering at most 4 of these tasks. **Strongly suggests batch-creating tickets to fill out a sheet rather than reflecting actual delivered work.**
- **2026-04-08 burst — 13 tasks created in a single day** (`created_at = 2026-04-08`) but `latest_log_date = 2026-03-30` — WH-50, 51, 52, 53, 54, 55, 56, 49, 64, 65, 63, 67, 56. Tickets created 9 days *after* the work was supposedly done. **Backfilled logging.** No commits matching most of these.
- **WH-99 + WH-100 + WH-103 + WH-104 + WH-105 + WH-107 + WH-108 + WH-109** — eight separate landing-page tickets (1h, 1h, 1.5h, 1h, 1h, 0.3h, 1h, 0.5h ≈ 7.3h combined) all about "enhance landing page X". Splitting "improve the landing page" into 8 sub-tickets is the textbook example of artificial granularity under the 4h-cap rule.
- **WH-110 (9h) vs. its supposed sub-items** — if WH-110 "find and clean backend dirty code" is the umbrella for WH-175/177/179/180/186/187 etc., then those individual tasks (totalling another ~10h) are double-counting. If WH-110 is its own thing, where's the output?

### Task Type Issues
- **WH-115** "Fix User invite issue" — typed `bug` (correct).
- **WH-116** "Fix Landing page margins" — typed `improvement`, should arguably be `bug` if the margins were broken; or correctly `improvement` if it was a polish pass. Acceptable either way.
- **WH-147** "Sentry DSN: remove hardcoded fallback in prod" — typed `bug`, but it's a security/config improvement. Borderline.
- **WH-49** "Test the web app" — typed `research`, correct, but the title indicates QA testing rather than research. The line is fuzzy.
- **WH-87** "Testing backend performance" — typed `improvement`, should be `research` per the rule "test/investigate → research".
- **WH-193** "Test web app" — typed `improvement`, should be `research` (same as WH-49).
- Net: ~3–5 misclassifications, low impact compared to the commit-traceability problem.

### Code Quality (where visible)

**Score: 7/10 on the small sample that exists.**

The few commits she did make are clean:
- `293da1a` (WH-177) is a legitimate refactor splitting two oversized view files (`stats_view.py` 1074 lines → 7 modules; `orgUserView.py` 840 lines → 6 modules). Module structure is sensible. Net line change is roughly zero (1874/-1881) — pure split, not a rewrite.
- `e763731` (WH-171/169/168) is concise, addresses N+1s by adding `select_related` / `prefetch_related` in the right places.
- `3ad2926` (WH-70) is a substantial Celery migration. Removes a 568-line `AUDIT_REPORT.md` from the repo as part of the same commit (cleanup is good but should ideally be a separate commit).

**Concerns:**
- `622c677` "remove duplicate imports" has no WH-ID despite WH-175 being a perfect match.
- `3dc9613` and `293da1a` are duplicate commits with the same content (the second is on `dev` after merge). Branch hygiene issue — likely a force-push or rebase artifact.
- `17c564e9` mixes a 1-line `rel="noopener"` change with 33,000 lines of `yarn.lock` updates. Should be two commits.

### Code Churn
Not enough sample to compute meaningfully — only 12 commits across 3 repos. **Estimated <10% churn (low)** simply because there's so little code to churn against.

### Bug Causation
Insufficient sample of fix commits in this period to do bug-causation analysis. WH-70 `3ad2926` is the only clear bug fix with a commit, and it's a pipeline rewrite rather than a localized fix.

### Codebase Ownership
- Web-apps frontend: nominally hers but **only 4 commits in 5 weeks**. The rest of the prototype activity in this period is by Amine.
- Django-backend: 7 commits — primary contributor (the only one) but very low absolute volume given that backend has 5+ years of code and many open improvement opportunities.
- Landing-page: 2 commits.
- **Effective ownership of the backend is hers by default (no other developer is touching it).** Bus factor = 1 on backend, but unlike Sidali's BLE work this isn't a complexity-driven situation, it's a staffing one.

### Verdict
**Rating: Concerning.**

**Strengths:**
- The code that does exist is clean and well-targeted (Celery migration, view-file splits, N+1 fixes).
- WH-70 / WH-177 demonstrate she is technically capable of substantial work when she actually does it.

**Concerns:**
- **9–22% task-to-commit traceability.** This is the dominant finding. ~60+ tasks declared with no visible code output across all branches.
- **WH-179 is verifiable evidence of a task being declared Ready-to-Deploy without the work being done.** The file is still in the repo on every branch. This is not an ambiguous case.
- **Backfill pattern.** 2 separate batches of 13–18 tasks created on a single day to cover prior periods. This is the opposite of disciplined real-time tracking.
- **Artificial splitting under 4h cap.** Particularly the 8-ticket landing-page enhancement cluster (WH-99/100/103/104/105/107/108/109).
- **42% of her commits lack WH-IDs** despite the policy. Two of them (`c3d7f13`, `d0b653d` "fix build issues" / "fix ci-cd pipeline") could plausibly be WH-117 work but aren't tagged.

**Talking Points for Review Meeting:**

1. **WH-179 was marked Ready to Deploy on April 29 — "remove db.sqlite3 from repo". The file is still present on every branch. Can you walk me through what happened?** (No good answer to this. Lead with this one.)
2. **You declared 75 code tasks and made 12 commits, of which 8 are WH-tagged and cover 7 unique tasks. That's ~10% commit traceability. Where is the rest of the work?** Possible answers: local branches not pushed (not acceptable for "Ready to Deploy" status); work done in a different system (which?); tasks created without the corresponding work having happened.
3. **On April 30 you created 18 tasks (WH-194 down to WH-161). Most of them have no commits. Were these tasks done that day, or were they created retroactively?**
4. **WH-110 "find and clean backend dirty code" was declared as 9 hours. You also declared individually WH-175, WH-177, WH-179, WH-180, WH-186, WH-187, WH-172, WH-170, WH-171, WH-168, WH-169. Are these the sub-tasks of WH-110, or separate work? If sub-tasks, why are the hours double-declared?**
5. **The 8 landing-page enhancement tickets (WH-99 through WH-109) covering ~7 hours map to a single commit (`182d9b4`) that removes 5938 lines and adds 1394. Were these really 8 separate pieces of work, or did the 4-hour cap force you to fragment one task?**
6. **You committed only 12 times across three repos in 5 weeks despite logging 114h. By any reasonable engineering benchmark, even fully AI-assisted, this is far below the expected ratio of commits to hours. What's your view on this?**

---

## Khadidja Cheurfi — Designer (part-time)

### Hours Analysis
- Expected: 100h (no leave taken in period). Logged: 72.5h. Missing: 27.5h.
- Reasonable meeting time at 20h/week × 5 weeks = 5h.
- **Unexplained gap: 22.5h.** ⚠️⚠️
- Leave balance is currently **-7 days** (used more leave historically than accrued). Worth asking about.

The gap is the largest of any team member — 22.5h of expected part-time work is missing without explanation. At 20h/week, that's effectively 1.1 weeks of unworked time across the period.

### Task Summary
- 32 design tasks visible in CSV. All `platform: Design`. All correctly typed `improvement` (design iteration is appropriately classified as improvement).
- Total declared on tasks: ~65–70h (matches the 72.5h logged).
- All tasks revolve around: dark mode prototype, landing page assets, prototype updates, dashboard layouts, design system.

### Commits & Process Compliance
- N/A — no commits expected for design work. The instructions explicitly exclude design tasks from code review.

### Work Review (task-data quality)

Since I cannot see her Figma output, the review is on **task hygiene** per the instructions:

**Vague task titles (problematic):**
- WH-191 "updated the landing page assets" (2h)
- WH-190 "finished updating landing page" (2h, same day as WH-191)
- WH-183 "updated the rula continue template" (2h) — what is "rula continue"?
- WH-174 "updated the prototype dark mode" (3h)
- WH-150 "fixed some issues in the dark mode" (2h)
- WH-135 "updating dark mode" (3h)
- WH-119 "adding the dark mode to the prototype" (3h)
- WH-123 "made the design system for the dark mode" (3h)

The dark-mode work appears in **5 separate tasks** (WH-119, 123, 135, 150, 174) totalling 13h across the period. Either these were 5 distinct iterations (which should be in the description), or it's one initiative split for time-tracking.

**Better-scoped tasks (good):**
- WH-156 "added the template for the mec, ramp" (3h) — specific deliverable
- WH-89 "started the prototype in claude" with description "made the main pages (dashboard, sessions, assessments…)" (4h) — clear scope
- WH-173 "finished updating the assets for home page" with description "made assets (he used images) in figma" (4h) — specific
- WH-124 "made the design for the compare Sessions (3 and 4 Sessions)" (4h) — specific
- WH-92 "improve the layout + add new interactions to the ui" (6h) — but typed only as 1 task at 6h, which exceeds the 4h cap policy. Either policy was relaxed for design or this is an exception.

### Duplicate / Split Tasks

- **WH-191 + WH-190 same day, both about "the landing page", 2h each = 4h combined.** Hard to see why these aren't one ticket "WH-X update landing page assets, 4h". **Looks like 4h-cap-driven splitting.**
- **WH-122 + WH-93 + WH-124** all about "compare sessions / compare assessments" prototype across multiple days. Probably legitimate iteration, not artificial.
- **Dark-mode cluster (WH-119, 123, 135, 150, 174)** — 5 tasks, 13h, spread over 12 days. Hard to judge without seeing the design output. **Combined hours implies a major dark-mode initiative; presenting it as 5 separate "updates" understates it.**
- **WH-92 (6h, 2026-04-13) exceeds the 4h cap.** Worth flagging as a policy exception.

### Task Type Accuracy
- All correctly typed `improvement`. ✓

### Work Pattern Analysis
- Output is **not steady**. Heavy clustering on certain days:
  - 2026-04-13: 4 tasks logged in one day (WH-88 3h + WH-92 6h + WH-89 4h + WH-126 1h = 14h)
  - 2026-04-18: 3 tasks logged retroactively for prior weeks (WH-119, 120, 121, 123, 124, 125, 126 — all created 2026-04-18 but with `latest_log_date` 2026-04-13/16/17)
  - 2026-04-29 → 2026-05-01: cluster of landing-page work (WH-191, 190, 183, 174 etc.)
- **Multi-day gaps** with no logged work that aren't leave days: 2026-04-04, 2026-04-05 (Sat-Sun expected gap), 2026-04-11 (Sat), 2026-04-25 (Sat). Most gaps look like weekends. But the 22.5h hours-gap suggests some hidden weekday gaps too.

### Verdict
**Rating: Adequate – but data quality is poor and hour gap is unexplained.**

I cannot evaluate the actual quality of her design work because the deliverables live in Figma. Based purely on task data:

**Strengths:**
- All design tasks are typed correctly (`improvement`)
- Some tasks have clear, specific deliverables (WH-89, WH-124, WH-156, WH-173)
- Output volume on her active days suggests she's productive when she's working

**Concerns:**
- **22.5h unexplained hour gap** is the largest in the team — this is the headline issue
- Many tasks have **vague titles** that don't describe a specific deliverable
- **Artificial 4h-cap splitting** visible (WH-190/191 same-day landing-page split; dark-mode work fragmented across 5 tickets)
- **One task exceeds the 4h cap** (WH-92 = 6h) — policy exception or violation?
- **Retroactive logging cluster on 2026-04-18** — 7 tickets created that day for prior days' work. Same backfill pattern as Assia, smaller scale.

**Talking Points for Review Meeting:**

1. **You logged 72.5h out of 100h expected — about 28h short. With no leave taken in the period, where did the missing time go?** This is the most important question.
2. **Tasks like "updated the landing page assets" and "finished updating landing page" the same day, 2h each — could those have been one 4-hour ticket? Are you splitting work to fit under the 4-hour cap?**
3. **The dark-mode prototype work shows up in 5 separate tickets (WH-119/123/135/150/174) totalling 13 hours. Could you walk me through the actual scope so I can judge it as one initiative?**
4. **WH-92 was logged at 6 hours, which is above the 4-hour task cap. Was this an exception we agreed to, or did the rule slip?**
5. **Your leave balance shows -7 days (used 7 more days than accrued). Can we reconcile that this period?**

---

## Team-Wide Observations

### Systemic Issues

1. **Process compliance is wildly inconsistent.** Sidali tags 92% of his commits with WH-IDs. Assia tags 58% (and produces only 12 commits). This isn't a tooling problem — it's enforcement.
2. **Task-to-commit traceability collapses for backend/web work.** ~75 backend/web tasks vs. ~12 commits is fundamentally broken. Either the team needs a rule that "Ready to Deploy" status requires a linked commit, or the status loses meaning.
3. **Backfill / batch-create is now visible across 2 of 3 team members** (Assia and Khadidja). Tasks created days after `latest_log_date` are systematically present. Real-time tracking is not happening.
4. **The 4-hour task cap is producing artificial fragmentation.** Khadidja's same-day 2h+2h landing-page split, Assia's 8-ticket landing-page enhancement cluster, Sidali's 5-ticket BLE-bug cluster are all examples. The cap is meant to discipline scope, not fragment one piece of work into N entries.
5. **The export's TEAM MEMBERS section excludes Abdelkader despite him being assignee on 12 tasks.** This is presumably correct (he's no longer with the company) but it means the CSV is internally inconsistent — it shows hours and tasks for someone who doesn't exist in the team list. The Hub should either remove his tasks or include him with `employment_type: Former`.

### Risk Areas

- **Bus factor = 1 on BLE / mobile sensor stack** (Sidali). Explicit risk if he is unavailable for any urgent BLE bug.
- **Bus factor = 1 on backend** (Assia, by default — no one else touches the Django repo). Made worse by her low output: if she leaves, no one is up to speed.
- **Backend has 1 person making 7 commits in 5 weeks.** That's not maintenance velocity, that's near-stasis. The repo will accumulate cruft.
- **Landing-page work goes in via untagged batch commits** (`182d9b4` covers ~9 tasks in one shot). When this approach is normalized, problems hide in those batches.
- **Khadidja's design output cannot be verified by me** — there is no link from a CSV task to a Figma file/version in the export. If The Hub could capture a Figma URL or version snapshot per task, design review becomes auditable.

### Recommendations

1. **Hard-enforce WH-IDs in commit messages.** Add a server-side `pre-receive` hook on each repo that rejects commits without `WH-\d+` (allow `chore:` and `merge:` exemptions). 100% commit compliance becomes mechanical, not behavioural.
2. **Block "Ready to Deploy" status without a linked commit hash.** The Hub should require a commit URL/hash on transition into Ready-to-Deploy for any non-Design task. This single change makes the WH-179 type of fabrication impossible.
3. **Audit Assia's pipeline directly.** A 1-on-1 walking through every "Ready to Deploy" Web/Backend task she has and asking for the commit. Tasks with no commit should be moved back to Todo or deleted. This will be uncomfortable but is necessary.
4. **Re-examine the 4-hour task cap.** The cap is causing visible artificial splitting. Options: (a) raise to 6h, (b) keep at 4h but require multi-task initiatives to declare a parent ticket, (c) drop the cap and rely on weekly review for excess.
5. **Capture design deliverable links in The Hub.** A Figma version / page link per design task would let you (or me) actually verify design output rather than judging on title quality alone.
6. **De-risk BLE.** Either pair Sidali with another engineer for 50% of his time over the next 2 months specifically on knowledge transfer, or accept the bus-factor risk explicitly and document it.
7. **Backend needs a second person.** 7 commits in 5 weeks on a Django backend serving production is a velocity problem, not just an Assia problem. Either bring on another backend dev or formally declare the backend in maintenance-only mode.

---

## Appendix

### A. Methodology

- **Hours:** taken directly from the CSV TEAM MEMBERS section. `Missing = leave_adjusted_expected_hours − logged_hours_in_period`. Reasonable meeting time = `5 weeks × 2h/week × (weekly_hours/40)`. Unexplained gap = `Missing − Reasonable meeting time`.
- **Task → commit linkage:** for each task with `platform != Design`, ran `git log --all --since=2026-03-30 --until=2026-05-02 --grep="WH-XXX"` across all 4 repos. Commits matching are listed; tasks with no match are flagged.
- **Untagged commits:** identified by pattern-grep against each developer's known emails/aliases, filtering out merge commits. Commits whose subject contains no `WH-\d+` are listed as compliance violations.
- **Code quality sample:** 3–5 largest meaningful diffs per developer, inspected via `git show --stat`. Quality scoring is on a 1–10 scale where 7 = mid-level expectation per REVIEW_INSTRUCTIONS.
- **Churn estimate:** count of commits per file by the same author within 14 days of a prior commit by the same author on the same file.
- **Bug causation:** for tasks typed `bug` with a fix commit, looked at recent file history. Self-vs-inherited determination is approximate when files have many authors.
- **Verifiable claims** (e.g. WH-179 file presence): cross-checked by `git log --diff-filter=D` and direct file listing.

### B. Tasks Reviewed in Detail

| WH-ID | Title | Assignee | Hours | Commits | Verdict |
|---|---|---|---|---|---|
| WH-165 | global auto reconnect | Sidali | 3 | `40cf2dcf`, `ac64257f` | Justified (undervalued) |
| WH-167 | recovering stream when limb reconnects | Sidali | 6 | `a1cbec73`, `7301fe4d` | Justified |
| WH-154 | visual to calibration | Sidali | 4 | `1208b094`, `20cb1cde` | Justified |
| WH-58 | investigate pairing problem | Sidali | 10 | `0684bde9`, `85cf732a` | Justified |
| WH-129 | reconnection in calibration | Sidali | 4 | `680b17be`, `ab456a85`, `d793955b` | Justified |
| WH-71 | tested with new changes | Sidali | 14 | None (research) | Unclear — large unexplained research time |
| WH-144 | calibration disconnects other limbs | Sidali | 5 | None | **Missing commit (urgent bug)** |
| WH-114 | sensor disconnection during recording | Sidali | 2 | None | **Missing commit (bug)** |
| WH-78 | work cycle sync bug | Sidali | 2 | None | **Missing commit (bug)** |
| WH-34 | Zip deleted on failure | Sidali | 2 | None | **Missing commit (bug)** |
| WH-33 | Connectivity check pings | Sidali | 1 | None | **Missing commit (bug)** |
| WH-117 | Fix CI/CD frontend pipeline | Assia | 2 | `442640b8`, `ec24583c` | Justified |
| WH-153 | Upgrade axios/xlsx/firebase | Assia | 1.5 | `87295adc` | Justified |
| WH-158 | rel=noopener on external links | Assia | 0.5 | `17c564e9` | Justified |
| WH-70 | Session Stuck in processing | Assia | 1.5 | `3ad2926` | Justified (undervalued) |
| WH-177 | Break up oversized view files | Assia | 1 | `293da1a` | Justified |
| WH-171/169/168 | Firebase to Celery + select_related + N+1 | Assia | 2.5 | `e763731` | Justified |
| WH-179 | Remove db.sqlite3 from repo | Assia | 0.5 | **None — file still present** | **NOT DONE** |
| WH-194 | Extract AbstractTimestampModel | Assia | 0.5 | None | No commit |
| WH-192 | Extract a CalculationService | Assia | 3.5 | None | No commit |
| WH-186 | Migrate URL routing to DRF DefaultRouter | Assia | 3 | None | No commit |
| WH-182 | Offload heavy StatsView calc to Celery | Assia | 2 | None | No commit |
| WH-181 | Add DB indexes | Assia | 1 | None | No commit (no migration file) |
| WH-180 | Replace bare except blocks | Assia | 1 | None | No commit |
| WH-172 | Move Firebase calls to FirebaseService | Assia | 1.5 | None | No commit (class doesn't exist) |
| WH-110 | find and clean backend dirty code | Assia | 9 | Possibly `622c677`+`293da1a` | Possibly justified — but overlaps with sub-tasks |
| WH-116 | Fix Landing page margins | Assia | 3.5 | `3726288` (untagged) | Justified — but commit untagged |
| WH-99–109 cluster | landing page enhancements | Assia | ~7 (8 tickets) | `182d9b4` (untagged) | Justified as a batch — but 8 tickets for 1 commit |

### C. Flagged Commits (without WH-ID)

| Repo | Hash | Author | Date | Message | Assessment |
|---|---|---|---|---|---|
| flutter | `a9764095` | bboysidou (Sidali) | 2026-04-17 | feat: sentry on blind spot | Likely WH-138, missed tag |
| flutter | `e6f7b83e` | bboysidou (Sidali) | 2026-04-18 | fix:[WH-130] add steps when limbs reconnect | Wrong WH-ID — WH-130 doesn't exist (typo for WH-129) |
| web-apps | `c3d7f13` | assia-mad | 2026-04-09 | fix: fix build issues | Likely WH-117 prep work, missed tag |
| django | `d0b653d` | assia-mad | 2026-04-09 | fix: fix ci-cd pipeline | Likely WH-117 prep work, missed tag |
| django | `622c677` | Assia | 2026-04-30 | chore: remove duplicate imports across backend | Almost certainly WH-175, missed tag |
| django | `3dc9613` | Assia | 2026-04-30 | refactor: split stats_view and orgUserView (duplicate of `293da1a`) | Branch hygiene issue |
| landing | `3726288` | assia-mad | 2026-04-20 | chore: unify margin and padding across sections | Likely WH-116, missed tag |
| landing | `182d9b4` | assia-mad | 2026-04-15 | chore: improve UI/UX across all pages | Covers WH-99/100/103/104/105/107/108/109 — 8 tasks in one untagged commit |

For Abdelkader's 41 commits: **all 41 are without WH-ID**. Listing them here would be noise; the takeaway is that he was on the team for 4 days of the period and tagged 0% of his commits. If he ever returns, the onboarding should include the commit-message rule.

---

## Appendix D. Abdelkader Barhoumi — Context (not in active team)

Abdelkader is no longer in the TEAM MEMBERS section but appears as assignee on 12 tasks early in the period. Last commit: 2026-04-03. Total flutter commits in period: 41, all untagged. His work was substantial — he extracted `session_sync` and `session_report` as separate features (`bfdd453f`, `d12d02ed`), enforced the new error-handling pattern across the session features (`14e6e3cf`), removed `firebase_crashlytics`, and organized 70+ pubspec dependencies into 12 logical groups (`cf0a5042`). The architecture work he started in March continued through April 3 and then stopped. His tasks in CSV (WH-2, 3, 4, 5, 22, 23, 24, 30, 31, 32, 36, 37) are mostly delivered in commits — tagging just wasn't applied. Co-assignments with Sidali (WH-22 refactor session, WH-37 merge PRs) explain why Sidali has those tasks but no individual commits for them.
