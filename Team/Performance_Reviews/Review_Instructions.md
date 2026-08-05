# Performance Review Instructions

> **Usage:** Place this file and the exported CSV from The Hub in the same folder as your 3 code repositories. Run Claude Code and tell it: "Read REVIEW_INSTRUCTIONS.md and use the CSV to generate the performance review."

---

## 1. Input Data

### CSV Structure

The CSV contains 3 sections separated by header rows starting with `===`:

1. **TASKS** — Completed tasks in the review period. Key columns:
   - `task_id`: format `WH-xxx` — this ID appears in commit messages
   - `title`, `description`, `status`, `priority`, `type` (bug/feature/improvement/research), `platform` (Web/Mobile/Design/General)
   - `assignees`, `assignee_emails` (can be comma-separated for multi-assignee tasks)
   - `total_hours_in_period`: hours the team member declared for this task
   - `created_by_name`, `created_at`, `updated_at`, `latest_log_date`

2. **TEAM MEMBERS** — One row per person with:
   - `weekly_hours`: contractual weekly hours (varies per person)
   - `expected_hours_in_period`, `leave_adjusted_expected_hours`, `logged_hours_in_period`
   - `employment_type`: Full-time or Part-time

3. **LEAVE DAYS** — Leave taken per person: vacation, sick, other

Parse all 3 sections. Derive the review period dates from the CSV header row (format: `TASKS (YYYY-MM-DD to YYYY-MM-DD ...)`). Derive the team member list from the TEAM MEMBERS section. Do NOT hardcode any names or roles — everything comes from the CSV.

### Repositories

There are 3 repositories in this workspace. Before starting:
```bash
# For each repo directory
git checkout dev && git pull origin dev
```

Determine which repo is which by inspecting their contents (look for `pubspec.yaml` = Flutter/Mobile, `manage.py` or `requirements.txt` = Django/Backend, `package.json` with React/Vite = Web frontend).

### Linking Tasks to Commits

Every commit should contain a task ID in the format `[WH-xxx]` or `WH-xxx` in its message. To find commits for a task:
```bash
git log --all --grep="WH-123" --oneline
```
Search across all 3 repos for each task.

### Platform-to-Repo Mapping

- `platform: Web` → search in web frontend repo AND backend repo
- `platform: Mobile` → search in mobile repo
- `platform: General` → search in all 3 repos
- `platform: Design` → no commits expected (design work happens in external tools like Figma)

---

## 2. Analysis Dimensions

For each team member found in the CSV, run all applicable analyses below. Skip code-related analyses for people who only have Design-platform tasks (they have no commits to review).

### 2.1 Hours & Attendance

From the TEAM MEMBERS and LEAVE DAYS sections:

- Calculate **missing hours** = `leave_adjusted_expected_hours` - `logged_hours_in_period`
- Calculate **weeks in period** = total weekdays in period / 5
- Calculate **reasonable meeting time** = weeks_in_period × 2 hours (2h/week is the expected average)
- **Unexplained gap** = missing_hours - reasonable_meeting_time
- If unexplained gap > 5 hours: flag as a concern with exact numbers
- Show weekly breakdown if possible (group time entries by week using `latest_log_date`)

For part-time team members, adjust expectations proportionally.

### 2.2 Task-to-Commit Cross-Reference

For every task where `platform` is NOT `Design`:

a) Search for commits containing the `WH-xxx` ID across all repos
b) If task type is `bug`, `feature`, or `improvement` and has zero commits: **flag as missing commit**
c) If task type is `research`: commits are optional, but note if present or absent
d) For tasks WITH commits: review the diff (see 2.4 for what to evaluate)

**Output:** A compliance table showing per team member: total code tasks, tasks with commits found, tasks missing commits, compliance %.

### 2.3 Commits Without Task IDs

For each team member, find commits in the review period that do NOT contain any `WH-` pattern:
```bash
git log --since="PERIOD_START" --until="PERIOD_END" --author="NAME_OR_EMAIL" --oneline | grep -iv "WH-"
```

Use author names/emails from the CSV. Try both name and email as git might use either.

**Every commit must have a task ID.** Commits without IDs are a process violation. Count them and list the worst examples per person.

### 2.4 Work vs. Time Justification

For each task that has commits, evaluate whether the declared hours are reasonable.

**Critical context:** All developers on the team have access to Claude Code (AI coding assistant). This means:
- Straightforward code (responsive layouts, CRUD, boilerplate, renaming, find-and-replace, simple refactors, adding error handling, import cleanup) can be generated very quickly — often in minutes
- Complex code (BLE/hardware interaction, state machine logic, race conditions, architectural redesign, debugging intermittent issues, performance optimization with profiling) legitimately takes time even with AI help
- A large diff does NOT mean a lot of work. A 500-line responsive CSS change is trivial with AI. A 30-line concurrency fix might take hours of debugging

**Classify each reviewed task as:**
- **Justified** — hours match the complexity
- **Possibly over-declared** — work seems simpler than the hours suggest. Explain why
- **Unclear** — can't determine from the commit alone (e.g., debugging work that required testing but the commit is small)

Don't review every single task in detail. Focus on:
- Tasks where hours seem disproportionate to the diff
- Tasks with 3+ hours declared
- Bug fixes (to check causation)
- The 5-8 most significant tasks per developer

For the rest, provide aggregate statistics.

### 2.5 Duplicate & Split Task Detection

Policy: tasks should not exceed 4 hours. This can lead to artificial splitting. Detect:

- Tasks by the same person with similar titles on the same or consecutive days
- Tasks that describe sequential parts of the same work (e.g., "fix reconnection" and "test reconnection" and "deploy reconnection fix")
- Research tasks immediately followed by a fix task on the same topic by the same person
- Multiple small tasks (<1h each) logged on the same day that could reasonably be one task

When found, report the combined real hours and flag whether the split seems artificial or legitimate (sometimes splitting is natural, like research then implementation).

### 2.6 Task Type Accuracy

Check if task types make sense based on the title:
- Title contains "debug", "investigate", "analyze", "research", "test", "search for" → should be `research`, not `bug` or `feature`
- Title contains "fix" → should be `bug`, not `improvement`
- Title is about adding a new capability → should be `feature`
- Title is about improving existing code/UX → should be `improvement`

Flag misclassifications. This matters because it distorts metrics (e.g., bug count looks higher or lower than reality).

### 2.7 Code Quality

For team members with code commits, sample 8-10 of their most significant commits (largest meaningful diffs, not just bulk renames). Evaluate:

- **Readability**: clear naming, logical structure, appropriate complexity
- **Error handling**: proper exception handling, no swallowed errors, edge cases considered
- **Architecture adherence**: follows existing project patterns (check the codebase to understand conventions)
- **Dead code**: commented-out code left behind, unused imports, abandoned functions
- **Type safety**: `any` in TypeScript, `dynamic` in Dart, missing type annotations in Python
- **Copy-paste**: duplicated logic that should be abstracted
- **Security**: obvious vulnerabilities (SQL injection, XSS, hardcoded secrets, open CORS)
- **Testing**: did they add/update tests? (note: lack of tests is common across the codebase, but proactive test writing by a mid-level is a positive signal)

**Score: 1-10** where 7 = meets mid-level expectations. Provide specific file paths and commit hashes as evidence for both good and bad examples.

### 2.8 Code Churn

For each developer with commits, measure how much of their recently written code was rewritten within 2-3 weeks:

```bash
# Approximate: for each developer's commits, check if the same files were modified again shortly after by the same person
```

Healthy churn is 15-25%. Above 30% suggests the developer is struggling with the task, requirements were unclear, or code was pushed without adequate thought. Below 10% on actively developed features could mean no iteration/improvement.

Provide a churn estimate per developer and flag if it's outside the healthy range.

### 2.9 Bug Causation

For tasks typed as `bug` (or tasks whose title clearly indicates a bug fix regardless of type):

a) Find the fix commit via `WH-xxx`
b) Use `git blame` on the changed lines BEFORE the fix to identify who wrote the original code
c) Determine:
   - **Self-caused**: same person introduced and fixed the bug
   - **Inherited**: bug was in code written by someone else (possibly a former developer)
   - **Unknown**: can't determine (e.g., file was heavily modified by many people)

d) For self-caused bugs, classify severity:
   - **Careless** (🔴): null checks missing, wrong variable, copy-paste error, would fail on basic testing, typo in logic
   - **Moderate** (🟡): edge case, state management under specific conditions, integration issue
   - **Understandable** (🟢): complex async/BLE timing, third-party quirk, cross-platform inconsistency, race condition

e) Report: per developer — total bugs fixed, self-caused count, severity breakdown, specific examples of the worst self-caused bugs with commit refs

### 2.10 Ownership & Impact

Map which parts of the codebase each developer primarily works on:
- Which directories/modules do they touch most?
- Are they concentrated in one area or spread across the codebase?
- Are any critical modules owned by only one person (bus factor = 1)?

This is informational, not scored. It helps you understand team dynamics and risk.

### 2.11 Design-Only Team Members

For team members who only have `Design` platform tasks (no code commits expected):

- Review task titles and descriptions: are they clear and specific, or vague?
- Hours analysis: same as 2.1
- Duplicate/split detection: same as 2.5
- Work pattern: is output steady across the period or clustered? Are there multi-day gaps without any logged work (that aren't leave days)?
- Task granularity: are tasks too broad ("updated the design") or appropriately scoped?

Score based on: clarity of task descriptions, consistency of output, reasonable time declarations, adherence to process. Be transparent that you cannot evaluate the quality of design output itself without seeing the actual deliverables.

### 2.12 Process Compliance Summary

Per team member, compile:
- % of code tasks with matching commits (2.2)
- Number of commits without task IDs (2.3)
- Task type accuracy rate (2.6)
- Missing hours / unexplained gaps (2.1)

This gives a quick "process discipline" score independent of code quality.

---

## 3. Output

Generate a single file: `performance_review_[PERIOD_END_MONTH]_[PERIOD_END_YEAR].md`

### Structure

```markdown
# Performance Review
## Period: [START] to [END]
## Generated: [TODAY]
## Team: [COUNT] members reviewed

---

## Executive Summary
[4-6 sentences: overall team health, top concerns, notable positives, key recommendations]

---

## Team Overview

### Hours & Attendance
| Name | Type | Weekly Hrs | Expected (adj.) | Logged | Missing | Reasonable Meetings | Unexplained Gap | Flag |
[One row per team member]

### Process Compliance
| Name | Code Tasks | w/ Commits | Compliance % | Commits w/o IDs | Type Accuracy | Hours Gap |
[One row per team member]

### Scoring Summary
| Name | Code Quality | Bug Rate | Time Justification | Process Discipline | Overall |
[One row per team member, 1-10 scale, N/A for design-only members on code metrics]

---

## [TEAM MEMBER NAME] — [ROLE INFERRED FROM PLATFORM]

### Hours Analysis
[Expected vs logged, missing hours breakdown, meeting time assumption, flags]

### Task Summary
[Total tasks, type breakdown, total hours, notable patterns]

### Commits & Process Compliance
[Tasks with/without commits, commits without IDs, examples]

### Work Review
[Key tasks reviewed in detail: WH-xxx, title, hours, what the commit shows, justified/over-declared/unclear]
[Focus on the most notable cases — not every task]
[For design-only: review task descriptions, patterns, granularity]

### Duplicate/Split Tasks
[Detected cases with combined hours]

### Task Type Issues
[Misclassified tasks]

### Code Quality (if applicable)
[Score /10, specific good and bad examples with file paths and commit hashes]

### Code Churn (if applicable)
[Churn %, interpretation]

### Bug Causation (if applicable)
[Self-caused bugs, severity, specific examples]

### Codebase Ownership (if applicable)
[What they own, bus factor risks]

### Verdict
**Rating:** [Strong / Adequate / Needs Improvement / Concerning]

**Strengths:**
- [Specific, with evidence]

**Concerns:**
- [Specific, with evidence]

**Talking Points for Review Meeting:**
1. [A question referencing a specific task/commit that opens a constructive conversation]
2. [...]
3. [...]
4. [...]

---

[REPEAT FOR EACH TEAM MEMBER]

---

## Team-Wide Observations

### Systemic Issues
[Patterns that affect the whole team, not just individuals: recurring task types, common quality issues, process gaps]

### Risk Areas
[Bus factor concerns, undertested modules, parts of the codebase with high churn]

### Recommendations
[3-5 concrete actions the CEO should consider: process changes, training, tooling, etc.]

---

## Appendix

### A. Methodology
[Brief explanation of how each metric was computed]

### B. Tasks Reviewed in Detail
| WH-ID | Title | Assignee | Hours | Commit(s) | Verdict |
[Table of all tasks that were reviewed in depth]

### C. Flagged Commits
[Commits without task IDs, with hash, author, date, message]
```

---

## 4. Rules

1. **Everything comes from the CSV + git.** Do not hardcode names, roles, or team structure. If the CSV has 2 people, review 2. If it has 10, review 10. Infer roles from the `platform` column patterns.

2. **Be direct.** This document is for the CEO's internal use only. Don't soften findings. If something is bad, say it with evidence.

3. **Always cite evidence.** Every claim must reference: WH-xxx task ID, commit hash (short), file path, or specific hour numbers. No vague statements like "code quality could improve."

4. **Mid-level is the benchmark.** All team members are evaluated against mid-level expectations unless the CSV or context suggests otherwise. A mid-level developer should:
   - Write clean, readable code without obvious anti-patterns
   - Handle errors and edge cases without being told
   - Not introduce bugs that basic testing would catch
   - Complete standard tasks within reasonable time
   - Write meaningful commit messages with task IDs
   - Classify tasks correctly
   - Log hours honestly and completely

5. **AI-assisted work is the norm.** These developers have Claude Code. Evaluate time declarations with this in mind. Large volumes of straightforward code should be fast. Complex debugging and architecture decisions still take time.

6. **Don't penalize volume.** Use rates (bugs per 10 tasks, churn %, compliance %) not absolute counts when comparing people with different task loads.

7. **The 4-hour rule.** Tasks are capped at 4 hours by policy. This context is essential for duplicate detection — it's not suspicious to have many 3-4h tasks; it IS suspicious to have three 4h tasks with near-identical titles on the same day.

8. **Design tasks have no commits.** This is expected and not a negative. Review design team members purely on task data quality and work patterns.

9. **Talking points should be questions, not accusations.** Example: "WH-123 was declared as 4 hours but the commit shows a 3-line CSS change. Can you walk me through what else was involved?" — this invites explanation rather than defensiveness.

10. **If uncertain, say so.** Mark unclear findings with [UNCERTAIN] and explain why. Don't guess.

11. **Check `dev` branch.** All primary work lands on `dev` across all 3 repos.

12. **Watch for gaming patterns.** Beyond split tasks, look for: tasks created and completed the same minute (backfilled?), time entries clustered at end of week (Friday catch-up logging?), research tasks with no description or deliverable, identical hours on every task (always exactly 2h or 4h — suggests rounding).

13. **Positive findings matter too.** If someone writes exceptional code, proactively improves architecture, catches bugs in review, or handles complex work efficiently — highlight it. Good reviews aren't just about finding problems.
