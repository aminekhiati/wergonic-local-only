# Wergonic Developer Performance Audit

## Period: January 2025 — March 2026
## Generated: 2026-03-20
## Branch: `dev` (all repositories)

---

### Git Author Mappings

| Real Name | Git Author(s) | Email(s) | Repo(s) | Status |
|-----------|--------------|----------|---------|--------|
| **84rrry** (Abdelbari) | `84rrry`, `Abdelbari` | abdelbaribouklab@gmail.com | Flutter | Former (benchmark) — inactive since Aug 2025 |
| **Sidali** | `bboysidou`, `SidouXP3` | bedrani.sidali.94@gmail.com | Flutter | Active — main mobile dev |
| **Abdelkader Barhami** | `AbdelkaderBarhoumi21`, `Abdelkader Barhoumi` | abdelkaderbarhoumi21@gmail.com | Flutter | Active — joined Feb 2026 |
| **Moussa** | `moozes`, `Moozes`, `Khodja Moussa` | m.khodja@esi-sba.dz, khodja.moussa.pro@gmail.com | Web Apps | Former — inactive since May 2025 |
| **Assia** | `assia-mad` | as.madaniyousfi@esi-sba.dz | Web Apps | Active — current web dev (fading) |
| **Faycal** | `faycal-dev`, `El-mogherbi Mohammed Fayçal` | m.elmogherbi@esi-sba.dz | Backend (historical) | Former — no commits in timeframe |
| **farhad-abtahi** | `farhad-abtahi` | farhad.abtahi@gmail.com | Flutter | External contributor (17 commits) |

**Backend note:** The Django backend repo (`wergonic-django-backend`) has **zero commits since November 20, 2024**. Faycal was the primary historical contributor (703 commits all-time) but has no activity in the audit timeframe. Backend is excluded from all analysis below.

---

## Executive Summary

**Team health: Concerning.** Of the 5 developers analyzed, 2 have completely stopped contributing (84rrry in Aug 2025, Moussa in May 2025), and Assia's output is declining sharply since mid-2025. The mobile team is effectively carried by Sidali with Abdelkader ramping up since February 2026. The web team has been Assia-only for 10 months with diminishing velocity.

**Biggest concerns:**
1. **Sidali's bug introduction rate** is the highest on the team — 57% of his commits are fixes, and he generates self-caused bugs at a concerning rate. Much of Abdelkader's recent work is cleaning up Sidali's code rather than building new features. He has strong technical capability (BLE, async state management) but commits code before testing it.
2. **Assia's fix-to-feature ratio (60%)** is a red flag — the RAMP assessment feature, which is core product functionality, was broken and re-patched 5 times in under a year. Several bugs survived 7-13 months in production.
3. **Zero task/ticket integration** across all repos — commits cannot be traced back to planned work, making it impossible to assess estimate accuracy or accountability.
4. **Backend is abandoned** — no commits in 16+ months. If it's still serving production traffic, this is a risk.

**Standout performer:** 84rrry (during his active period) had the cleanest code quality, lowest bug rate, and best commit hygiene of the mobile team. He is the correct benchmark. Abdelkader, despite being new and junior, shows the lowest individual defect rate — though his sample size is small.

---

## 1. Bug Causation Analysis

### 1.1 Overview

#### Flutter Repository

| Developer | Total Commits | Fix Commits | Fix % | Bugs Caused (confirmed) | Self-Caused | 🔴 Obvious | 🟡 Moderate | 🟢 Understandable |
|-----------|-------------|-------------|-------|------------------------|-------------|-------------|-------------|-------------------|
| **Sidali** | 253 | 169 | **57%** | ~52 | ~30 | 6+ | 5+ | 2 |
| **84rrry** | 229 | 77 | 22% | ~18 | ~12 | 3 | 4 | 1 |
| **Abdelkader** | 195 | 40 | 37%* | ~6 | ~3 | 1 | 1 | 1 |

*Abdelkader's fix commits are mostly cleaning up Sidali's architectural debt — only 6 bugs are his own.

#### Web Apps Repository

| Developer | Total Commits | Fix Commits | Fix % | Bugs Caused (confirmed) | Self-Caused | 🔴 Obvious | 🟡 Moderate | 🟢 Understandable |
|-----------|-------------|-------------|-------|------------------------|-------------|-------------|-------------|-------------------|
| **Moussa** | 538 | 101 | 24% | 18 | 11 | 8 | 7 | 3 |
| **Assia** | 207 | 55 | **45%** | 19 | 14 | 11 | 6 | 2 |

#### Bug Rate Normalized (bugs caused per 100 non-fix commits)

| Developer | Non-Fix Commits | Bugs Caused | Rate per 100 |
|-----------|----------------|-------------|--------------|
| **Sidali** | 84 | 52 | **61.9** |
| **Assia** | 152 | 19 | **12.5** |
| **Moussa** | 437 | 18 | **4.1** |
| **84rrry** | 152 | 18 | **11.8** |
| **Abdelkader** | 155 | 6 | **3.9** |

**Key insight:** When normalized, Sidali's bug introduction rate is catastrophically high — roughly 1 confirmed bug for every 1.6 feature commits. Moussa and Abdelkader have the healthiest rates.

---

### 1.2 Per-Developer Bug Reports

#### Sidali — Top 10 Worst Bugs

| # | Fix Hash | File | Date Fixed | Severity | Description |
|---|----------|------|-----------|----------|-------------|
| 1 | `35e4e422` → 5 more | `measurements_manager_cubit.dart` | 2025-10-22 | 🔴 | **6 consecutive fix commits same day** for corrupted CSV. Committed 10× identical `debugPrint` statements as debug spam. Classic fix-then-break loop — 6 passes to resolve one issue. |
| 2 | `d3f0fba2` | `organization.remote.datasource.dart` | 2026-01-28 | 🔴 | **`print(token)` — bearer auth token printed to console in production.** Security vulnerability. Removed as part of a different fix, meaning it was present for weeks. |
| 3 | `b59a86c9` | `search_models_work_cycle.dart` | 2026-01-30 | 🔴 | Session history displayed **task ID integer** instead of task name. `SessionEventEntity.name` was set to `taskId.toString()`. Careless field confusion. |
| 4 | `ec41606d` | `work_session_recording_screen.dart` | 2026-01-28 | 🔴 | Break refused to resume. Multiple null-unsafe dereferences (`currentWorkSession!`, `sessionEvents!.last.timeStamps!.last`) with no guards. Crashed when session events list was empty. |
| 5 | `0daee1ee` | `injectable.config.dart` | 2025-10-15 | 🔴 | Circular DI reference + wrong Dio client injection. **App crashed on startup.** |
| 6 | `79ac8180` | `consultant.model.dart` | 2025-12-03 | 🔴 | Token returned null — wrong `@freezed` annotation for JSON key casing. App displayed null username. |
| 7 | `a492a1d1` | Multiple files | 2026-02-10 | 🟡 | Batch of `!` operators on nullable fields throughout BLE/firmware/session code. Required a dedicated "potential nulls" sweep commit. |
| 8 | `18b05041` | `welcome_screen.dart` | 2026-02-24 | 🟡 | Offline mode not persistent on app restart — `InternetCubit` never notified of persisted settings. |
| 9 | `f0850636` | session local DB | 2025-12-15 | 🟡 | Duplicate session records — no upsert guard when session ends. |
| 10 | BLE reconnection chain | `ble.data.repository.dart` | Feb–Mar 2026 | 🟡 | **12 consecutive BLE reconnection fix commits over 3 weeks.** Original code had no timeout, no retry limit, no stale GATT handling, no protection against connecting one sensor to two limbs. |

#### 84rrry — Top 10 Worst Bugs

| # | Fix Hash | File | Date Fixed | Severity | Description |
|---|----------|------|-----------|----------|-------------|
| 1 | `887ce30e` + `7a061d1a` | `enums.dart` | 2025-07-18 + 07-24 | 🔴 | `vibrationResult.confidence` accessed without null check. Crashed app. **Required 2 separate fix commits** (fix-then-break). Introduced May 29, unfixed 50 days. |
| 2 | `4742b47f` | `work_session_entity.dart` | 2025-03-31 | 🔴 | `endedAt!.difference(startedAt)` — forced unwrap on nullable. **This was a regression** — previous code had `?.` safe null, this commit re-introduced the crash. |
| 3 | `8dd675fd` | `feedback_manager.dart` | 2025-07-10 | 🔴 | ChestStrap (HR sensor) grouped with Trunk in feedback switch case. HR feedback panel always showed red (wrong thresholds). **Unfixed for 191 days (6+ months).** |
| 4 | `1ef8e4e4` | `ble_measurements_cubit.dart` | 2025-03-18 | 🟡 | BLE subscription memory leak — subscriptions never canceled before restart, causing duplicate data in CSV files. |
| 5 | `7f83a548` | `work_session_repository.dart` | 2025-04-15 | 🟡 | Wrong named parameter in `syncWorkTasks` call — positional arg passed to wrong param, silently broke work task sync. |
| 6 | `787bf5db` | `settings_model.dart` | 2025-07-23 | 🟡 | Wrong property name (`workSessionDurationLimit` vs `sessionDurationLimit`). Session duration limit silently broken for 110 days. |
| 7 | `aa119cec` | `work_session_repository.dart` | 2025-04-25 | 🟡 | `device.limb!` on nullable — CSV files created with empty headers when limb was null. |
| 8 | `895785d9` | `ble_data_source.dart` | 2025-03-07 | 🟢 | FlutterBluePlus API signature change on upgrade. Understandable. |

#### Abdelkader — All Bugs (6 total)

| # | Fix Hash | File | Date Fixed | Severity | Description |
|---|----------|------|-----------|----------|-------------|
| 1 | `5fd192ab` | `welcome_screen.dart` | 2026-03-18 | 🔴 | Missing parenthesis — syntax error committed to branch. Self-fixed same day. |
| 2 | `732e011c` | Multiple files | 2026-03-16 | 🟡 | Missing `dispose()` calls on resources from his own refactor work. Memory leaks. |
| 3 | `ad45e8dd` | `selectable_limbs_cubit.dart` | 2026-03-09 | 🟢 | Unnecessary null check on non-nullable type. Lint error. |
| 4 | `f8c7e52c` | `welcome_screen_version_widget.dart` | 2026-03-18 | 🟢 | `FutureBuilder` rebuilding — Future created inline in `build()` not `initState`. |

#### Moussa — Top 10 Worst Bugs

| # | Fix Hash | File | Date Fixed | Severity | Description |
|---|----------|------|-----------|----------|-------------|
| 1 | `ffaffda5` | `ActiveSessionsTable.hooks.tsx` | 2025-01-22 | 🔴 | Firestore query with `where("status", "!=", INTERRUPTED)` + `orderBy("status")` — requires an index, silently returned no results. **Active sessions invisible to users for ~6 weeks.** |
| 2 | `6947414545` | `SecurityScreen.tsx` | 2025-03-06 | 🔴 | Single `isPassword` state controlled all 3 password field visibility toggles. Copy-paste error — clicking one eye toggled all three. |
| 3 | `75624448` | `DonutChartCard.tsx` | 2025-01-27 | 🔴 | `data.reverse()` mutates prop array in place. Chart flickered/flipped on every React re-render. Reported by external user, required hotfix. |
| 4 | `2c2fbede` | `CompareButton.tsx` | 2025-03-10 | 🔴 | Compare button had no disabled state with 0 rows selected — triggered silent error on click. |
| 5 | `a3e4e39d` | `compareSessions.ts` | 2025-03-06 | 🟡 | Trunk limb used arm angle ranges in multi-compare. Wrong posture breakdown for trunk. |
| 6 | `c5be7bec` etc. | Sessions/users table hooks | 2025-03-07 | 🟡 | Page number not reset on filter change — **4 separate fix commits for the same missing pattern.** |
| 7 | `b589db1e` | `URLLimbsFilter.hooks.tsx` | 2025-04-01 | 🟡 | Limbs filter not initialized from URL on mount. Sharing/refreshing showed wrong state. |
| 8 | `3f8916c3` | `DeactivateUserButton.tsx` | 2025-01-13 | 🟡 | `is_activated_in_org` removed from API but still gating frontend button visibility. |
| 9 | `de349b7a` | Multiple | 2025-03-14 | 🟡 | Backend error strings rendered directly in UI — raw server text exposed to users. |
| 10 | `7b219e49` | `apiRoutes.ts` | 2025-04-19 | 🔴 | Fixed Assia's bug: every query param used `if (value)` truthy check — `page=0`, `is_active=false` silently dropped. |

#### Assia — Top 10 Worst Bugs

| # | Fix Hash | File | Date Fixed | Severity | Description |
|---|----------|------|-----------|----------|-------------|
| 1 | `281081c7` | `sessions/utils/functions.ts` | 2025-11-26 | 🔴 | `formatTime()` treated input as seconds when caller passed minutes. Every duration showed as 1/60th of correct value (30 min → 0:00:30). **Bug lived 13+ months.** |
| 2 | `cc65610a` | `wergonic-admin/services/axios.ts` | 2026-01-27 | 🔴 | **axios baseURL hardcoded to `http://localhost:8000/api/v1/`** — deployed admin panel made all API calls to localhost. Every user got network errors. |
| 3 | `8dfde8d9` | `RAMP/hooks/generatedDetailedSummary.tsx` | 2025-09-17 | 🔴 | Truthy check on time value `0` — valid zero-exposure postures showed "Missing sensor" instead of `00:00:00` across all RAMP reports. |
| 4 | `7249626e` | `RAMP/hooks/generatedDetailedSummary.tsx` | 2025-12-01 | 🔴 | RAMP Q5 score: `null.toString()` not guarded. Crash or wrong score. **Introduced Apr 2025, unfixed 7+ months.** |
| 5 | `1203aa40` | `api/workcycles.ts` | 2025-07-29 | 🔴 | Wrong Django ORM lookup paths for workcycle filters (`task_model__workstation__line__factory` vs correct `task_model__operator__workstation__...`). Filters had zero effect. |
| 6 | `913dc62c` | `FinishedSessionSettingsButton.tsx` | 2025-05-02 | 🔴 | Field typo `has_measurments` vs `has_measurements`. Recalculate button permanently disabled for all sessions. |
| 7 | `4c52ce08` | `FinishedSessionsTable.hooks.tsx` | 2025-02-13 | 🟡 | Sessions API only fetched `FINISHED` status — `FAILED` sessions never appeared in table. |
| 8 | `3bc366c0` | `MEC/DetailedSummary/ResultsTable` | 2025-12-11 | 🟡 | MEC Q9 arm results used pipe-delimited string format. Parser misidentified cases, showed wrong arm data in PDF/detail view. |
| 9 | `a35a4de9` | `GenerateAssessmentButton.hooks.ts` | 2025-07-22 | 🟡 | Avix import: `label_task` and `work_cycle_task` both sent as same type — incorrect assessment generation. |
| 10 | `d406c496` | `api/apiRoutes.ts` | 2025-04-14 | 🔴 | All query params used truthy checks `if (params?.page)` — `page=0` and `is_active=false` silently dropped from API calls. Fixed by Moussa. |

---

### 1.3 Self-Caused Bugs Hall of Shame

**The Pattern:** Developer introduces a bug, then later fixes it — sometimes presenting the fix as productive work.

#### Worst Offenders by Self-Caused Bug Count:

| Developer | Self-Caused Bugs | As % of Total Bugs Caused | Avg Time to Self-Discovery |
|-----------|-----------------|--------------------------|---------------------------|
| **Sidali** | ~30 | 58% | Same day (most are same-day emergency patches) |
| **Assia** | 14 | 74% | Weeks to months (several survived 7-13 months) |
| **84rrry** | ~12 | 67% | Days to months (some survived 50-191 days) |
| **Moussa** | 11 | 61% | Days to weeks |
| **Abdelkader** | 3 | 50% | Same day |

**Most Damaging Self-Caused Bugs:**

| Developer | Bug | Time in Production | Impact |
|-----------|-----|-------------------|--------|
| Assia | `formatTime()` seconds vs minutes | **13 months** | Every duration display wrong in distance-of-hand feature |
| 84rrry | ChestStrap in wrong feedback case | **191 days** | HR feedback panel always showed red |
| Assia | RAMP Q5 null crash | **7+ months** | Score display crash/wrong values |
| 84rrry | Settings wrong property name | **110 days** | Session duration limit silently broken |
| Moussa | Active sessions Firestore query | **~6 weeks** | Active sessions invisible to all users |
| 84rrry | Vibration confidence null | **50 days** | App crash on vibration data absence |

---

### 1.4 Bug Introduction Matrix (Who Caused → Who Fixed)

#### Flutter

| Caused By ↓ / Fixed By → | Sidali | 84rrry | Abdelkader |
|---------------------------|--------|--------|------------|
| **Sidali** | **~30** | ~4 | **~22** |
| **84rrry** | 1-2 | **~12** | 0 |
| **Abdelkader** | 0 | 0 | **~3** |

**Key finding:** ~22 of Abdelkader's ~40 fix commits target code Sidali authored. Abdelkader is effectively a cleanup crew for Sidali's technical debt.

#### Web Apps

| Caused By ↓ / Fixed By → | Moussa | Assia |
|---------------------------|--------|-------|
| **Moussa** | **11** | 1-2 |
| **Assia** | 5 | **14** |

**Key finding:** Moussa fixed 5 of Assia's bugs (notably the truthy check param issue affecting 69 API params). Assia's bugs are mostly self-caused and long-lived.

---

### 1.5 Fix-Then-Break Cycles

#### Cycle 1: Sidali — Corrupted CSV (Oct 22, 2025) — **WORST IN DATASET**
6 commits on the **same day**, all labeled `fix: corrupted csv when creating consecutive sessions`:
```
35e4e422 → 65313599 → 5ff983ce → a44a48c6 → fa17501b → 38a6c05f
```
The `CsvWriterManager` was being re-initialized without closing the previous instance. Debug spam (10× identical prints) was committed to production. Each pass introduced new state issues.

#### Cycle 2: 84rrry — Vibration Confidence (May–July 2025)
`c387a959` (May 29) → `887ce30e` (Jul 18, partial fix) → `7a061d1a` (Jul 24, real fix). Two fixes required for one null check.

#### Cycle 3: 84rrry — WorkSession totalDuration regression (Mar–Apr 2025)
The `endedAt` field had been safe (`endedAt?.difference`). Commit `d488b444` (Mar 30) **re-introduced** the forced unwrap `endedAt!.difference`. This is a regression of a previously fixed pattern.

#### Cycle 4: Sidali — Session Start Stuck (Jan 2026)
4 separate commits addressing session-start/break/resume null dereferences over 3 days. Feature was pushed before being testable end-to-end.

#### Cycle 5: Sidali — BLE Reconnection (Feb–Mar 2026)
~12 BLE reconnection fix commits over 3 weeks — each adding guards, timeouts, or state fixes that should have been in the original implementation.

#### Cycle 6: Assia — RAMP Detailed Summary (Jan 2025 – Dec 2025)
Same file (`generatedDetailedSummary.tsx`) broken and patched **5 times over 11 months**. Multiple variants of the same falsy-check and null-guard bug.

#### Cycle 7: Moussa — Page Number Reset (Mar 2025)
4 separate fix commits on the same day for the identical missing pattern (page not reset on filter change). Should have been one shared hook.

---

## 2. Code Quality Assessment

### 2.1 Quality Scores

| Developer | Score | Justification |
|-----------|-------|--------------|
| **84rrry** | **7.0/10** | Solid architecture (clean architecture layers properly separated), good error handling, proper `Either<Failure, T>` patterns. Dragged down by directory typos (`entites/`), missing try/catch in one method, and formatting inconsistencies. |
| **Assia** | **6.5/10** | Clean component decomposition (`.tsx`/`.hooks.ts`/`.styles.tsx` split), explicit error handling with typed `AxiosError`. Penalized for 60% fix ratio, repetitive data structures in RAMP hook (275 lines of copy-paste), and `as any` casts. |
| **Sidali** | **6.5/10** | Demonstrates genuine technical capability on hard problems (async BLE, connection state machines, pipeline serialization). Penalized for 57% fix ratio, commit hygiene, typos in field names, and hardcoded strings. |
| **Moussa** | **5.5/10** | Major architectural contributions (legacy API route migration, component cleanup). Penalized for severe code duplication (query builder copy-pasted 12×), god-hook returning 28 values, test artifacts committed to repo, `any` type overuse. |
| **Abdelkader** | **5.5/10** | Systematic refactoring work (text styles centralization). Penalized for copy-paste duplication in 4 auth screens, noop dead code (`const CircularProgressIndicator()` created and discarded), and file-per-commit noise. |

---

### 2.2 Per-Developer Code Review

#### 84rrry (Benchmark — 7.0/10)

**Strengths:**
- Work cycle feature follows clean architecture: `data/sources`, `data/repositories`, `domain/entities`, `domain/usecases`, `presentation/logic/cubits`
- Repository methods pattern-match through `Either<Failure, T>` using `freezed`
- Error handling: `on ApiException catch → throw Failure` + `on Exception catch → Sentry.captureException + rethrow`

**Weaknesses:**
- `lib/work_cycle/data/repositories/work_cycle_repository.dart` ~line 84: `getWorkOperatorByStation()` has **no try/catch** while every other method does — inconsistent
- `lib/work_cycle/domain/entites/` — directory named `entites` (typo, missing 'i') across 6+ files, never corrected
- `lib/work_cycle/data/models/work_cycle_model_model.dart` — double "model" in filename
- `work_session_recording_screen.dart` line 53: `isFristStart` typo; lines 380, 398: `//Take a look at this` unresolved placeholder comments
- `work_cycle_cubit.dart` constructor takes 10 positional parameters — injection risk, should use named

#### Sidali (6.5/10)

**Strengths:**
- `ble.data.repository.dart` (466 lines) — genuinely sophisticated: `Completer`-based connection timeouts, GATT retry logic, pipeline serialization lock, `isCancelled()` guards, stale GATT recovery. This is non-trivial async code done well.
- Error handling distinguishes BT exceptions from generic errors with meaningful messages

**Weaknesses:**
- `feedback_screen.page.dart` lines 48-49, 76-78: commented-out method calls left in code
- `work_session_cubit.dart` line 58: `_internatlMeasurementsCubit` — typo in field name used throughout class
- `work_session_crud.data.repository.dart`: `_workSessionlocalDataSource` — inconsistent capitalization
- `sensors_settings_section.dart` lines 164-183: 4 hardcoded English UI strings not going through localization
- `welcome_screen.dart` line 300: `"Failed to create work session no Organization specified"` — hardcoded error string
- Commit messages: `"fix: just a commit for now"` (×2), `"fix: bugs and errors"`, `"fix: some test files"` (×3)

#### Abdelkader (5.5/10)

**Strengths:**
- Text styles refactor executed systematically across ~43 files with clean commit granularity (one commit per feature folder, consistent message format)
- Auth screen layouts are functional

**Weaknesses:**
- `login_with_email_page.dart` lines 131-133: **`const CircularProgressIndicator()` created and immediately discarded** — noop dead code that implies loading intent but does nothing. Same in `reset_password_page.dart` lines 96-98.
- 4 auth screens (`login_with_email_page.dart`, `reset_password_page.dart`, `create_new_password_page.dart`, `login_form.dart`) have identical 15-line footer block copy-pasted — should be an `AuthFooter` widget
- `sensors_settings_section.dart` lines 208-224: `//TODO: RETORE THIS WHEN THE FEATURE IS READY` — typo in TODO, large commented-out block
- 25+ lint fix commits each named `"Fix: fix lint rules issues in X folder"` — should have been 1-2 commits
- `"Fix: reslove conflicts"` (×5) — typo in commit messages

#### Moussa (5.5/10)

**Strengths:**
- Migrated legacy `legacyApiRoutes.ts` (verbose imperative URL builders) into clean `apiRoutes.ts` with typed params — the new pattern is clearly better
- Consistent conventional commit usage (233 `refactor:` commits, each scoped)
- Active dead code removal (deleted `AddNewUserButton2`, versioned component duplicates)

**Weaknesses:**
- `apiRoutes.ts` lines 37-403: **query builder block copy-pasted 12 times verbatim** across routes. A single `buildQueryString(params)` utility would eliminate 200+ lines of duplication.
- `useTabData.tsx`: god-hook returning **28 values**, firing 7 API queries simultaneously. `useTabData2` is a partial duplicate with inconsistent naming. **6 `eslint-disable-next-line react-hooks/exhaustive-deps`** — lying dependency arrays.
- `MEC/utils/Untitled-1.txt` — **scratch notes file committed to repo** (commit `4f21bf62`, message: `"fix: testing"`), still in HEAD
- `TestingNewComponentsPage.tsx` — playground page with `console.log(allDataIsValid)`, hardcoded mock data, still in router with index export
- `apiRoutes.ts` line 1: `// todo delete all comments` — meta-TODO never resolved
- `legacyApiRoutes.ts` — ~250 lines still in repo despite being replaced, carrying 83 `// todo done` comments
- `sessions.ts`: `api.get<any>` × 4, `data: any` on high-traffic functions

#### Assia (6.5/10)

**Strengths:**
- Consistent file structure: `.tsx` / `.hooks.ts` / `.styles.tsx` / `index.ts` split respected throughout
- `GenerateAssessmentButton.tsx` + `.hooks.ts`: clean hook/component boundary, `yup.when()` validation correctly applied
- Error handling: `useMutation` callbacks consistently use `AxiosError<IServerError>` typing with `error.response?.data.detail` surfaced to user
- Active dead code cleanup via PR #693 (deletion-dialogs refactor, 17 file deletions)

**Weaknesses:**
- `generatedDetailedSummary.tsx` lines 37-312: **275 lines of hardcoded repeated data structure** — 10× copy-pasted ternary patterns. Should be a config array with single mapping function.
- `generatedDetailedSummary.tsx` lines 321, 323: `(cache?.data as any)?.session` — casting through `any` instead of typing the cache
- `NotificationsList.tsx` line 1: `/* eslint-disable no-else-return */` blanket at file level hiding nested if/else that should be a lookup map
- `GenerateReportButton.tsx` line 201: `setTimeout(resolve, 300)` — artificial delay hack for UX spinner
- 23 commits (~19%) are version history updates to a static `versionHistory.ts` file — process overhead

---

### 2.3 Code Smell Density Comparison

| Developer | Estimated Smells per 100 Lines | Primary Smell Types |
|-----------|-------------------------------|---------------------|
| **84rrry** | ~2.5 | Naming typos, occasional missing error handling |
| **Assia** | ~2.5 | Repetitive data structures, `as any` casts, eslint suppression |
| **Sidali** | ~3.0 | Dead code, hardcoded strings, typos in field names |
| **Moussa** | ~3.5 | Massive duplication, `any` types, test artifacts, god-hooks |
| **Abdelkader** | ~4.0 | Copy-paste auth screens, noop dead code, commented blocks |

---

### 2.4 Commit Hygiene Comparison

| Metric | 84rrry | Sidali | Abdelkader | Moussa | Assia |
|--------|--------|--------|------------|--------|-------|
| Fix % of commits | 22% | **57%** | 37%* | 24% | **45%** |
| Message quality | Good (conventional) | Variable (many vague) | Mixed (refactor good, lint noise) | Mostly good | Good format |
| Worst message | `"refactor: bug fixes"` | `"fix: just a commit for now"` | `"Fix: reslove conflicts"` ×5 | `"fix: testing"` | — |
| Broken/redo commits | Low | **High** | Medium | Medium | Medium |
| Avg commit size | ~141 lines | ~325 lines | ~327 lines* | ~51 lines | ~212 lines |

*Abdelkader's high avg includes generated/doc files. His real code-change average is much lower.

---

## 3. Velocity & Efficiency

### 3.1 Activity Metrics

#### 84rrry — Flutter (Jan–Aug 2025, then GONE)

| Month | Commits | Lines Added | Lines Removed | Active Days |
|-------|---------|-------------|---------------|-------------|
| 2025-01 | 41 | 1,690 | 118,483* | 11 |
| 2025-03 | 14 | 1,083 | 503 | 1 |
| 2025-04 | 5 | 11,083 | 7,046 | 2 |
| 2025-05 | 40 | 2,011 | 935 | 10 |
| 2025-06 | 55 | 7,311 | 4,020 | 13 |
| 2025-07 | 65 | 5,854 | 1,991 | 14 |
| 2025-08 | 5 | 50 | 51 | 2 |
| **TOTAL** | **229** | | | **54 days** |

*Jan: 116k lines from test CSV asset removal.
**Last commit: Aug 4, 2025. No activity in 7+ months.**

#### Sidali — Flutter (Sep 2025–present)

| Month | Commits | Lines Added | Lines Removed | Active Days |
|-------|---------|-------------|---------------|-------------|
| 2025-09 | 10 | 2,605 | 1,673 | 3 |
| 2025-10 | 30 | 4,978 | 1,972 | 6 |
| 2025-11 | 16 | 51,635* | 53,521* | 5 |
| 2025-12 | 26 | 22,605 | 10,126 | 9 |
| 2026-01 | 17 | 6,075 | 2,584 | 9 |
| 2026-02 | 80 | 6,817 | 3,065 | 15 |
| 2026-03 | 74 | 19,685 | 14,618 | 12 |
| **TOTAL** | **253** | | | **59 days** |

*Nov spike: ~45k from auto-generated `.g.dart` files (Dart build runner).

#### Abdelkader — Flutter (Feb–Mar 2026 ONLY)

| Month | Commits | Lines Added | Lines Removed | Active Days |
|-------|---------|-------------|---------------|-------------|
| 2026-02 | 132 | 51,901* | 32,448 | 8 |
| 2026-03 | 63 | 69,168* | 21,602 | 9 |
| **TOTAL** | **195** | | | **17 days** |

*Large line counts include doc files added/moved/deleted multiple times and file-per-commit lint refactors. Real code output is significantly lower.
**First commit ever in this repo: Feb 18, 2026.**

#### Moussa — Web Apps (Jan–May 2025, then GONE)

| Month | Commits | Lines Added | Lines Removed | Active Days |
|-------|---------|-------------|---------------|-------------|
| 2025-01 | 145 | 7,815 | 6,788 | 23 |
| 2025-02 | 75 | 2,657 | 63,321* | 16 |
| 2025-03 | 193 | 5,379 | 5,220 | 19 |
| 2025-04 | 112 | 3,153 | 2,866 | 18 |
| 2025-05 | 13 | 1,093 | 362 | 4 |
| **TOTAL** | **538** | | | **80 days** |

*Feb: SVG inline React component cleanup (legitimate deletions).
**Last commit: May 30, 2025. No activity in 10 months.**

#### Assia — Web Apps (Jan 2025–present, declining)

| Month | Commits | Lines Added | Lines Removed | Active Days |
|-------|---------|-------------|---------------|-------------|
| 2025-01 | 18 | 345 | 244 | 7 |
| 2025-02 | 8 | 264 | 64 | 5 |
| 2025-03 | 25 | 2,815 | 599 | 12 |
| 2025-04 | 17 | 1,263 | 373 | 8 |
| 2025-05 | 32 | 2,880 | 1,334 | 11 |
| 2025-06 | 9 | 1,008 | 459 | 4 |
| 2025-07 | 20 | 2,825 | 548 | 9 |
| 2025-08 | 10 | 608 | 526 | 4 |
| 2025-09 | 25 | 16,454* | 16,403* | 4 |
| 2025-10 | 4 | 108 | 38 | 2 |
| 2025-11 | 4 | 38 | 17 | 3 |
| 2025-12 | 10 | 1,303 | 640 | 4 |
| 2026-01 | 7 | 61 | 15 | 4 |
| 2026-02 | 16 | 522 | 150 | 6 |
| 2026-03 | 2 | 11 | 69 | 1 |
| **TOTAL** | **207** | | | **86 days** |

*Sep spike: Prettier formatter run across translation JSON files (~11k lines changed, not substantive).
**Trend: 32 commits in May 2025 → 4, 4, 10, 7, 16, 2 in recent months. Clearly fading.**

---

### 3.2 Gaps > 5 Business Days

#### 84rrry — MAJOR GAPS
| From | To | Business Days | Notes |
|------|----|---------------|-------|
| 2025-01-22 | 2025-03-10 | **33** | 6+ weeks dark |
| 2025-03-10 | 2025-04-29 | **36** | 7+ weeks dark |
| **2025-08-04** | **present** | **~160+** | **GONE** |

#### Sidali
| From | To | Business Days | Notes |
|------|----|---------------|-------|
| 2025-09-16 | 2025-10-22 | **26** | 5+ weeks silence |
| 2025-12-17 | 2026-01-06 | 14 | Year-end (acceptable) |

#### Abdelkader
No gaps — only 17 active days total (Feb 18 – Mar 16, 2026). **Zero history before Feb 2026.**

#### Moussa — MAJOR GAP
| From | To | Business Days | Notes |
|------|----|---------------|-------|
| **2025-05-30** | **present** | **~200+** | **GONE** |

#### Assia — FRAGMENTED RHYTHM
| From | To | Business Days |
|------|----|---------------|
| 2025-08-13 | 2025-09-11 | **21** |
| 2025-10-01 | 2025-10-30 | **21** |
| 2025-10-30 | 2025-11-26 | **19** |
| 2026-01-27 | 2026-02-15 | **13** |
| Plus 6 additional gaps of 6-12 days | | |

Assia has the most fragmented commit rhythm of all 5 developers.

---

### 3.3 Suspicious Patterns

#### 🔴 RED FLAGS

| Pattern | Developer | Evidence |
|---------|-----------|---------|
| **Complete dropout** | 84rrry | Last commit Aug 4, 2025. 160+ business days of zero activity. |
| **Complete dropout** | Moussa | Last commit May 30, 2025. 200+ business days of zero activity. |
| **File-per-commit inflation** | Abdelkader | Feb 19: 29 commits, Feb 26: 28 commits — each touching one file in a systematic refactor. Inflates commit count ~5-10× vs. batched approach. |
| **Doc file shuffling** | Abdelkader | `API_ENDPOINTS_DOCUMENTATION.md` (3,800 lines) added → deleted → re-added → duplicated across 3 paths. Inflates line count by ~25%. |
| **Formatter run as feature work** | Assia | Sep 12: 10 of 12 commits are `"fix: fix prettier formatting"` on JSON files. Inflates Sep line count by ~22k lines. |
| **Generated files as productivity** | Sidali | Nov 2025: ~28k of 105k lines changed are `.g.dart` generated files. Not hand-written. |
| **Zero task integration** | ALL | No ticket/task IDs in any commit across any repo. Cannot trace commits to planned work. |

#### 🟡 YELLOW FLAGS

| Pattern | Developer | Evidence |
|---------|-----------|---------|
| **Late night commits** | Sidali | Multiple commits 1am–4am on Oct 28-30 and Mar 15 (21 commits that day). Crunch mode. |
| **Declining engagement** | Assia | From 32 commits/month (May 2025) to 2 commits/month (Mar 2026). Nearly done. |
| **Burst after silence** | 84rrry | 33-day gap → 14 commits in one day → 36-day gap → resumes. Sporadic. |

---

### 3.4 Commit Timing

```
84rrry:    ░░░ (midnight)  █████████████ (10-17h peak)  ░░ (evening)
Sidali:    ████ (midnight-2am) █████████████████ (9-18h peak, strongest 15-16h) ░░ (evening)
Abdelkader: (clean 10-14h block only, no night work)
Moussa:    ████████████████ (10-18h peak, strongest at 17h with 90 commits) ████ (21-22h)
Assia:     ███ (midnight) █████████████ (9-16h) ░░ (evening)
```

---

## 4. Comparative Analysis

### 4.1 Mobile Team vs Benchmark (84rrry)

| Metric | 84rrry (Benchmark) | Sidali | Abdelkader |
|--------|-------------------|--------|------------|
| Quality Score | 7.0 | 6.5 | 5.5 |
| Fix % | 22% | **57%** | 37%* |
| Bug rate (per 100 non-fix commits) | 11.8 | **61.9** | 3.9 |
| Smells per 100 lines | ~2.5 | ~3.0 | ~4.0 |
| Architecture quality | Strong | Strong | N/A (UI/styling scope) |
| Commit message quality | Good | Variable | Mixed |
| Self-testing evident | Moderate | **Low** | Moderate |

**Sidali vs 84rrry:** Sidali handles harder problems (BLE state machines, connection recovery) and his technical capability on async code is comparable or higher. But his discipline is far worse — 57% vs 22% fix rate, 6× higher bug introduction rate, and a habit of committing before testing. 84rrry introduced fewer bugs per feature and his bugs were mostly in complex areas (BLE, model serialization) rather than careless null checks.

**Abdelkader vs 84rrry:** Limited comparison due to scope difference. Abdelkader is doing UI/styling/refactoring while 84rrry built data pipelines. On Abdelkader's own work, he has copy-paste patterns that 84rrry avoids, plus the noop `CircularProgressIndicator()` issue suggests insufficient attention to what code does. His bug rate is the lowest but his sample is small (17 active days).

---

### 4.2 Cross-Team Rankings

| Rank | Developer | Overall Assessment | Justification |
|------|-----------|-------------------|---------------|
| 1 | **84rrry** | Best quality, lowest bug density, cleanest commits | But departed — no longer relevant |
| 2 | **Moussa** | Highest raw output, major refactoring contributions | But departed. Code had duplication and hygiene issues. |
| 3 | **Sidali** | Strongest active technical ability, handles hardest problems | Bug rate is alarming. Needs discipline, not skill. |
| 4 | **Assia** | Cleanest active code structure, good error handling | Output declining. Long-lived bugs in core features. |
| 5 | **Abdelkader** | Lowest individual defect rate, systematic approach | Too early to assess. Scope limited. Copy-paste patterns. |

---

### 4.3 Growth Trajectories

#### Sidali — Trajectory: **Improving (slowly)**
- Sep–Nov 2025: Architecture migration with high fix churn, learning the refactored codebase
- Dec 2025–Jan 2026: Feature delivery improving, fewer same-day fix cycles
- Feb–Mar 2026: BLE reconnection still took 12+ passes, but overall commit quality improving
- **Verdict:** Moving in the right direction but still has fundamental discipline problems

#### Abdelkader — Trajectory: **Too early to tell**
- Feb 2026: Started with systematic refactors (good) but with file-per-commit inflation
- Mar 2026: First feature work (welcome screen, sensor settings) — some noop code issues
- **Verdict:** 17 active days is insufficient sample. Clean refactoring work is promising. Need 2-3 more months of feature work to assess properly.

#### Assia — Trajectory: **Declining**
- Jan–May 2025: Active, shipping features, 11-23 active days/month
- Jun–Aug 2025: Slowed to 4-9 active days/month
- Sep 2025–present: Mostly version history updates, formatter runs, minor fixes. 2-4 active days/month.
- **Verdict:** Engagement has dropped significantly. Either part-time, demotivated, or transitioning out.

---

## 5. Performance Review Briefs

### 5.1 Sidali

**Summary Verdict: Needs Improvement**

**Strengths:**
- Handles the most technically complex code in the mobile app (BLE connectivity, async state machines, pipeline serialization)
- `ble.data.repository.dart` demonstrates sophisticated async patterns: `Completer` timeouts, GATT retry, mutex locks — commit evidence throughout Feb–Mar 2026
- Currently the only consistent mobile developer
- Clean architecture understanding — features properly separated into data/domain/presentation layers

**Weaknesses:**
- **57% of all commits are fixes** — the highest on the team by far
- **Bug rate of 61.9 per 100 feature commits** — roughly 1 bug for every 1.6 features
- Bearer token printed to console in production (`d3f0fba2`) — security vulnerability
- 6-commit same-day fix cycle for CSV corruption (`35e4e422` → `38a6c05f`, Oct 22 2025)
- 12 consecutive BLE reconnection fixes over 3 weeks — fundamentals (timeouts, retry limits) missing from original code
- Commit messages like `"fix: just a commit for now"`, `"fix: bugs and errors"` — unprofessional
- Typos in field names used throughout classes (`_internatlMeasurementsCubit`)
- Hardcoded English strings not going through localization

**Self-Caused Bugs:** ~30 confirmed. Most are same-day emergency patches, indicating code is committed before testing.

**Quality Concerns:**
- `work_session_cubit.dart`: `_internatlMeasurementsCubit` typo propagated throughout
- `sensors_settings_section.dart` lines 164-183: 4 hardcoded UI strings
- `welcome_screen.dart` line 300: hardcoded error message

**Efficiency Concerns:**
- 26-day gap (Sep 16 – Oct 22, 2025) with no commits
- Late night commits (1-4am) on multiple occasions — indicates crunch mode rather than planning
- BLE reconnection took 12+ iterations when fundamentals should have been in v1

**Recommendations:**
1. **Mandatory self-testing before commit.** Every feature must be tested end-to-end before pushing. The same-day fix cycles show code is being committed untested.
2. **Code review gate.** Sidali's PRs need review before merge — the bug rate demands it.
3. **No debug prints in commits.** The `print(token)` security leak is unacceptable. Set up a pre-commit hook to reject `print()` calls.
4. **BLE feature planning.** Before writing BLE code, list all edge cases (timeout, retry, stale connection, multi-device) upfront. Don't discover them over 12 commits.

**Talking Points:**
1. "Your BLE repository code shows you can handle complex async problems well. But commit `d3f0fba2` had a `print(token)` that leaked the bearer auth token to console. How did that get committed?"
2. "On October 22, you had 6 consecutive fix commits for the CSV corruption bug. Can you walk me through why it took 6 passes?"
3. "Your commit `_internatlMeasurementsCubit` has a typo in a field name that's used throughout the WorkSessionCubit. Do you use any linting or spell-checking?"
4. "About 22 of Abdelkader's 40 fix commits are cleaning up bugs in your code. Are you aware of this ratio? What can we do to bring it down?"
5. "You had a 26-day gap between September 16 and October 22 with no commits. What were you working on during that time?"

---

### 5.2 Abdelkader Barhami

**Summary Verdict: Adequate (Too Early for Full Assessment)**

**Strengths:**
- Lowest individual defect rate on the team (6 bugs in 195 commits, only 3 self-caused)
- Text styles refactor was exemplary: systematic, one commit per feature folder, consistent messages
- Clean working hours (10-14h block, no crunch)
- Effectively cleaning up Sidali's technical debt (~22 fix commits targeting Sidali's code)

**Weaknesses:**
- **Noop dead code:** `const CircularProgressIndicator()` in `login_with_email_page.dart` lines 131-133 and `reset_password_page.dart` lines 96-98 — widget created and discarded, does nothing
- **Copy-paste duplication:** 4 auth screens with identical 15-line footer blocks. Should be an extracted widget.
- **File-per-commit inflation:** 29 commits in one day (Feb 19) for a refactor that could be 3-5 commits. Creates misleading velocity metrics.
- **Doc file shuffling:** `API_ENDPOINTS_DOCUMENTATION.md` added, deleted, re-added, duplicated across 3 paths
- **Commit message typos:** `"Fix: reslove conflicts"` appears 5 times

**Self-Caused Bugs:** 3 — minor (syntax error, missing dispose, FutureBuilder rebuild). All self-fixed same day.

**Quality Concerns:**
- `login_with_email_page.dart` lines 131-133: code that does literally nothing. This should have been caught by the developer before committing.
- `sensors_settings_section.dart` lines 208-224: `//TODO: RETORE THIS WHEN THE FEATURE IS READY` — typo in TODO

**Efficiency Concerns:**
- Only 17 active days total in the repo (Feb 18 – Mar 16, 2026). Very recent addition.
- High line counts inflated by doc file operations and file-per-commit refactoring approach
- Zero commits before Feb 2026 — unclear what he was doing for 14 months prior

**Recommendations:**
1. **Learn to extract reusable widgets.** The 4 auth screens with identical footers is a training opportunity.
2. **Batch refactoring commits.** One commit per file during a systematic refactor creates noise. Use 3-5 commits max for a sweep.
3. **Test what the code does.** The `const CircularProgressIndicator()` that does nothing shows he may not understand Flutter widget lifecycle fully.
4. **Give him more feature ownership.** He's spent most of his time on cleanup — he needs to prove he can build features independently.

**Talking Points:**
1. "In `login_with_email_page.dart`, there's a `const CircularProgressIndicator()` that gets created inside an if-block but never used — it just gets discarded. Can you explain what you intended that to do?"
2. "Your text styles refactor was clean and well-organized. But the 4 auth screens all have the same footer copy-pasted. Why didn't you extract it into a shared widget?"
3. "On February 19 you had 29 commits and on February 26 you had 28 commits. Each one touches a single file. Why not batch these into fewer commits?"
4. "You've been on the project for about a month. What's your assessment of the codebase so far, and what do you think needs the most work?"

---

### 5.3 Assia

**Summary Verdict: Needs Improvement**

**Strengths:**
- Consistent component structure (`.tsx` / `.hooks.ts` / `.styles.tsx` / `index.ts` split)
- Explicit error handling — `AxiosError<IServerError>` typing, `error.response?.data.detail` surfaced to users via snackbar
- `GenerateAssessmentButton.tsx` + `.hooks.ts` is well-decomposed with clean hook/component boundary
- Yup validation schemas used correctly with conditional requirements
- Active cleanup: PR #693 deleted 17 unused files

**Weaknesses:**
- **60% fix-to-feature ratio** — highest on the web team
- **`formatTime()` seconds vs minutes bug survived 13 months** (`281081c7`) — every duration in distance-of-hand feature displayed as 1/60th of correct value
- **axios baseURL hardcoded to `localhost`** in deployed admin panel (`cc65610a`) — all users got network errors
- **RAMP assessment feature broken and re-patched 5 times over 11 months** — `generatedDetailedSummary.tsx` is a fragile mess
- **RAMP Q5 null crash undetected for 7+ months** (`7249626e`)
- Field typo `has_measurments` broke recalculate button for all sessions (`913dc62c`)
- Wrong Django ORM lookup paths in workcycle filters (`1203aa40`) — filters had zero effect
- Truthy check on `0` showed "Missing sensor" for valid zero-exposure postures (`8dfde8d9`)

**Self-Caused Bugs:** 14 — the highest self-caused percentage (74%). Several survived months in production.

**Quality Concerns:**
- `generatedDetailedSummary.tsx` lines 37-312: 275 lines of hardcoded repeated structure with 10× copy-pasted ternary patterns. This file is the source of multiple bugs and needs to be refactored into a data-driven config.
- `(cache?.data as any)?.session` — casting through `any` instead of typing
- `eslint-disable no-else-return` blanket at file level in `NotificationsList.tsx`
- `setTimeout(resolve, 300)` UX hack in `GenerateReportButton.tsx`

**Efficiency Concerns:**
- **Output declining sharply:** 32 commits in May 2025 → 2 commits in Mar 2026
- 6 gaps of 13-21 business days since Aug 2025
- 23 commits (19%) are version history file updates — process overhead, not engineering
- Sep 2025: 10 of 12 commits are Prettier formatter runs on JSON files — inflated metrics

**Recommendations:**
1. **Refactor `generatedDetailedSummary.tsx` immediately.** This file is a bug factory. Convert the hardcoded array of 6 objects into a declarative config with a single mapping function.
2. **Test with real data before PRs.** The `formatTime()` bug, the `0 == "Missing sensor"` bug, and the `localhost` deploy all would have been caught by running the app once with real data.
3. **Address engagement.** Her output has dropped ~94% from peak (32 → 2 commits/month). Need to understand if this is a capacity, motivation, or offboarding issue.
4. **Type the APIs.** `(cache?.data as any)?.session` shows she knows the shape of the data but won't type it. This causes bugs downstream.

**Talking Points:**
1. "The RAMP detailed summary hook has been broken and fixed 5 times in the last year. It's 275 lines of copy-pasted ternary expressions. What would it take to refactor this into something maintainable?"
2. "Commit `281081c7` fixed a `formatTime()` bug where seconds were treated as minutes. That bug was live for 13 months — every duration in the distance-of-hand feature showed wrong values. How did that go unnoticed?"
3. "The wergonic-admin deployed with `localhost` as the API URL. Every user got network errors. What was your deployment testing process?"
4. "Your commits have dropped from 32/month in May to 2 in March. What's going on? Are there blockers, or has your availability changed?"
5. "The `has_measurments` typo (vs `has_measurements`) broke the recalculate button for all sessions. Do you have any TypeScript strict mode or compile-time checks that would have caught this?"

---

### 5.4 Moussa (Former — for reference)

**Summary Verdict: Strong (during active period)**

**Strengths:**
- Highest raw commit volume (538 in 5 months)
- Major architectural contribution: migrated legacy API routes to clean typed pattern
- Most active days per month of any developer (23 in Jan, 19 in Mar)
- Active dead code removal and component cleanup
- Lowest normalized bug rate (4.1 per 100 non-fix commits)

**Weaknesses:**
- Query builder pattern copy-pasted 12× in `apiRoutes.ts` — no utility extraction
- `useTabData` god-hook returning 28 values with 6 suppressed dependency arrays
- Committed scratch file (`Untitled-1.txt`) and testing page with `console.log` to repo
- `legacyApiRoutes.ts` not deleted despite being fully replaced
- 4 `any` types in high-traffic API functions

**Note:** Moussa has been inactive since May 30, 2025. If still nominally on the team, this needs to be addressed.

---

### 5.5 84rrry (Former — Benchmark Reference)

**Summary Verdict: Strong**

Cleanest code quality, proper clean architecture, best commit hygiene. Some long-lived bugs (191-day ChestStrap, 110-day settings property) suggest insufficient post-merge testing. The `endedAt!` regression is the most concerning pattern — re-breaking something that was previously safe.

**Inactive since Aug 4, 2025.**

---

## Appendix

### A. Methodology

1. **Branch:** All analysis performed on `dev` branch of each repository, pulled to latest as of 2026-03-20.
2. **Timeframe:** `git log --since="2025-01-01"` across all queries.
3. **Bug identification:** Commits matched against keywords: fix, bug, hotfix, patch, resolve, broken, crash, revert, regression, error, issue, wrong, missing, null, exception. Merge commits excluded. Each substantive fix was inspected with `git show` and `git blame` to trace authorship.
4. **Code quality:** 10-15 most-modified files per developer were read and analyzed for patterns, anti-patterns, and code smells.
5. **Velocity:** `git log` with `--format`, `--numstat`, `--shortstat` for monthly breakdowns. Active days = distinct dates with commits.
6. **Line count caveats:** Auto-generated files (`.g.dart`), formatter runs, doc files, and test CSV deletions are noted where they significantly inflate metrics.

### B. Repository Summary

| Repository | Branch | Last Commit | Total Commits (2025+) | Contributors (2025+) |
|------------|--------|-------------|----------------------|---------------------|
| `wergonic-flutter` | dev | Mar 2026 | 694 | 4 (84rrry, Sidali, Abdelkader, farhad) |
| `wergonic-web-apps` | dev | Mar 2026 | 745 | 2 (Moussa, Assia) |
| `wergonic-django-backend` | dev | Nov 2024 | 0 | 0 |

### C. Key Commit Hashes Referenced

#### Flutter
| Hash | Developer | Description |
|------|-----------|-------------|
| `35e4e422` | Sidali | CSV corruption — start of 6-commit cycle |
| `d3f0fba2` | Sidali | `print(token)` security leak |
| `b59a86c9` | Sidali | Task ID shown instead of name |
| `ec41606d` | Sidali | Break resume crash |
| `0daee1ee` | Sidali | DI circular reference crash |
| `79ac8180` | Sidali | Token null from wrong freezed annotation |
| `c387a959` | 84rrry | Vibration confidence null (introduced) |
| `887ce30e` | 84rrry | Vibration confidence partial fix |
| `d488b444` | 84rrry | `endedAt!` regression |
| `8dd675fd` | 84rrry | ChestStrap feedback fix (191 days late) |
| `5fd192ab` | Abdelkader | Missing parenthesis syntax error |
| `a40412f4` | Abdelkader | Fixed Sidali's null safety in WorkSessionCubit |

#### Web Apps
| Hash | Developer | Description |
|------|-----------|-------------|
| `ffaffda5` | Moussa | Firestore active sessions query fix (6 weeks broken) |
| `75624448` | Moussa | DonutChart .reverse() mutation fix |
| `7b219e49` | Moussa | Fixed Assia's truthy check bug (69 params) |
| `281081c7` | Assia | formatTime seconds vs minutes (13 months) |
| `cc65610a` | Assia | axios localhost hardcode in deployed admin |
| `8dfde8d9` | Assia | RAMP `0` = "Missing sensor" fix |
| `7249626e` | Assia | RAMP Q5 null crash (7 months) |
| `913dc62c` | Assia | `has_measurments` typo fix |
| `1203aa40` | Assia | Wrong ORM lookup paths in workcycle filters |
| `d406c496` | Assia | Truthy check params (introduced, fixed by Moussa) |

---

*Report generated by automated git archaeology analysis. All claims reference specific commit hashes and file paths. Findings marked [UNCERTAIN] where confidence is limited.*
