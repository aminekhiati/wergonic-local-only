# Wergonic — Full Product Task Backlog

Generated: 2026-04-20
Scope: Django Backend, Flutter Mobile, Web Apps (Client Panel), Landing Page

Priority levels: **HIGH** (causes bugs, security issues, or visible broken features), **NORMAL** (quality improvement, should be fixed), **LOW** (nice-to-have, polish)

---

## BOTH (Backend + Frontend coordination required)

| # | Priority | Title | Description |
|---|----------|-------|-------------|
| 1 | HIGH | Fix "assessment" typo across all projects | The word "assessment" is misspelled as "assesment" (single 's') in backend URL namespaces (`core/urls.py` namespace="Assesments"), API routes, frontend query keys, and URL paths (`apiRoutes.ts`). This is a coordinated migration: add new correctly-spelled endpoints on backend while keeping old ones as aliases, update frontend to use new endpoints, then deprecate old ones after a release cycle. |
| 2 | HIGH | Move Sentry DSN to environment variables in all projects | Sentry DSN is hardcoded in `wergonic-flutter/lib/main.dart` (line 29), `wergonic-web-apps/apps/client-panel/src/main.tsx` (line 13). Move to env variables (`--dart-define` for Flutter, `VITE_SENTRY_DSN` for web). Anyone with repo access can currently spam your Sentry quota. |
| 3 | NORMAL | Fix "measurements" typo in API field names | `measurments_csv` is misspelled in the backend DB column (`SessionBasedModel.py`) and referenced in frontend. Since it's a DB column, create a migration to rename the field, add a deprecation alias on the serializer for mobile clients still using the old key, and update frontend/mobile after backend deploys. |
| 4 | NORMAL | Fix "mouvement" terminology (French spelling) in stats responses | `forward_mouvement` and `side_mouvement` are used in backend stats views and Excel export logic. Coordinate rename across backend response keys and frontend consumers. |
| 5 | NORMAL | Standardize organization-related naming across platforms | Backend uses `set_active_consulting_organization`, Flutter has route typo `switchOranization` (missing 'g'), and the concept of "active org" vs "consulting org" vs "mobile org" is inconsistent. Define clear terminology and apply across all codebases. |

---

## WEB — Django Backend

| # | Priority | Title | Description |
|---|----------|-------|-------------|
| 6 | HIGH | Change default REST permission class to IsAuthenticated | In `core/settings.py` line 211, `DEFAULT_PERMISSION_CLASSES` is set to `AllowAny`. Any endpoint where a developer forgets to declare `permission_classes` is publicly accessible. Change to `rest_framework.permissions.IsAuthenticated` and audit all views that intentionally need to be public (login, register, password reset) to explicitly set `AllowAny`. |
| 7 | HIGH | Restrict ALLOWED_HOSTS in production | `core/settings.py` line 26 has `ALLOWED_HOSTS = ["*"]` with no environment guard. Add a condition: if `ENVIRONMENT == "PROD"`, set `ALLOWED_HOSTS` to actual production hostnames only. |
| 8 | HIGH | Fix Invitation.expiration_date default (evaluated at import time) | In `users/models/invitation.py` line 17, `default=timezone.now() + timedelta(days=7)` is evaluated once at module import. Every invitation gets the same expiration timestamp from server startup. Fix: create a callable `def default_expiration(): return timezone.now() + timedelta(days=7)` and use `default=default_expiration`. |
| 9 | HIGH | Fix set_active_consulting_organization not deactivating previous org | In `users/models/baseUserModel.py` lines 165-187, the method only activates the new org but never deactivates the previous one. Users end up with multiple `is_active=True` UserOrganization rows. Add `UserOrganization.objects.filter(user=self, is_active=True).update(is_active=False)` before activating the new one. |
| 10 | HIGH | Remove ValueError raises from Session post_save signal | In `user_sessions/models/SessionBasedModel.py` lines 835 and 841, `ValueError` is raised inside a signal handler. This surfaces as a 500 error on the API call that saved the session. Replace raises with `logger.error(...)` + `return` (the session is already saved). |
| 11 | HIGH | Add null checks in session_check cron command | In `user_sessions/management/commands/session_check.py` line 31, `session.worker.user.organization.id` is accessed without null checks. `worker` is nullable (SET_NULL). Any ONGOING session with a deleted worker crashes the entire cron run, skipping remaining sessions. Add null checks at each level. |
| 12 | HIGH | Replace hardcoded "tno" organization name check with a model flag | In `SessionBasedModel.py` line 536, `if "tno" in instance.organization.name.lower()` determines whether TNO calculations run. Add a boolean field `enable_tno_calculations` on the Organization model and use that instead. |
| 13 | HIGH | Require authentication for Swagger/API docs in production | In `core/settings.py` line 41 and `core/urls.py` line 44, API documentation is set to `AllowAny`. Full endpoint structure is publicly readable. Gate behind `IsAuthenticated` or `IsAdminUser` when `ENVIRONMENT != "DEV"`. |
| 14 | HIGH | Stop sending plaintext passwords in emails | In `organizations/views/orgUserView.py` lines 241-256, `registerOrganizationView.py` lines 127-139, random passwords are generated and emailed in plaintext. Replace with a password-reset or magic-link flow. The passwordless sign-in infrastructure already exists — use it. |
| 15 | HIGH | Fix naive datetime in FirebaseAuthentication | In `firebase_auth/authentication.py` line 65, `user.last_seen = datetime.now()` stores a naive datetime while `USE_TZ = True` is active. Replace with `from django.utils import timezone; user.last_seen = timezone.now()`. |
| 16 | HIGH | Fix FirebaseAuthentication swallowing all exceptions as unauthenticated | In `firebase_auth/authentication.py` lines 69-71, any exception (including DB connection errors) is caught and returns `None` (unauthenticated). A DB outage silently treats all requests as anonymous. Only catch `User.DoesNotExist`; re-raise everything else. |
| 17 | HIGH | Fix MergeSessions thread-safety issues with transaction.atomic | In `user_sessions/views/session_views.py` lines 465, 551-553, `@transaction.atomic` wraps `post()` but a background thread runs outside the transaction. Also `bypass_signal` (a ContextVar) set in the main thread won't be seen by the executor thread. Move the signal bypass into the thread function and handle transaction boundaries properly. |
| 18 | HIGH | Fix stats views missing authorization check (cross-org data access) | In `user_sessions/views/stats_view.py` lines 52-65, permission check only verifies the user has ANY active organization — not that they belong to the session's organization. A user from org A can access org B's session stats. Add proper org membership check. |
| 19 | HIGH | Fix .first().organization.id null pointer in stats views | In `user_sessions/views/stats_view.py` lines 140-146, 454-460, `UserOrganization.objects.filter(...).first().organization.id` is called without null-checking `.first()`. If it returns None, raises AttributeError. This pattern appears in 5+ views. Add null guard. |
| 20 | NORMAL | Fix Organization.number_of_employees using len() instead of .count() | In `users/models/organizationModel.py` lines 92-97, `len(self.user_set.all())` loads all user objects into memory for a count. With 500+ workers per org this is wasteful. Replace with `.count()`. |
| 21 | NORMAL | Fix N+1 queries in UserDisplaySerializer | In `users/serializers/userSerializer.py` lines 170-193, `get_organization()` and `get_role()` each run per-object queries. Add `prefetch_related("userorganization_set__organization")` to list views (`ListUsersView`, `OrganizationUserView`). |
| 22 | NORMAL | Fix number_of_sessions_per_month date calculation bug | In `users/models/organizationModel.py` lines 99-110, `last_month_start = today.replace(day=1) - timedelta(days=1)` computes the last day of the previous month, not the first day of the current month. Same bug in `number_of_assessments_per_month`. Fix the date range. |
| 23 | NORMAL | Replace InMemoryChannelLayer with Redis for production | In `core/settings.py` line 164, `InMemoryChannelLayer` doesn't work across multiple Gunicorn workers. WebSocket features silently fail at scale. Use Redis channel layer for non-dev environments. |
| 24 | NORMAL | Fix Notification post_save signal calling instance.save() | In `notifications/models.py` lines 39-63, `instance.save()` is called inside a `post_save` signal — this re-triggers the signal (only avoids recursion by checking `created`). Use `Notification.objects.filter(pk=instance.pk).update(organization=user_organization)` instead. |
| 25 | NORMAL | Fix circular import between Organization model and user_sessions/ramp | In `users/models/organizationModel.py` lines 4-5, Organization imports Session and RAMPAssessment. Move `number_of_sessions_per_month` and `number_of_assessments_per_month` logic to the serializer layer where it belongs. |
| 26 | NORMAL | Fix duplicate URL pattern "" in organizations/urls.py | In `organizations/urls.py` lines 8-9, two paths with `""` are registered. Django always matches the first one, making the second dead code. Use distinct patterns. |
| 27 | NORMAL | Fix ReportTemplateViewSet missing permission on list action | In `users/views/ReportTemplete.py` lines 14-15, the permission check for `get_queryset` is commented out. Any authenticated user can list another user's report templates. Uncomment and fix the permission check. |
| 28 | NORMAL | Rename ReportTemplete.py to ReportTemplate.py | Filename typo: `users/views/ReportTemplete.py` should be `ReportTemplate.py`. Update all imports. |
| 29 | NORMAL | Fix Sentry not initializing on staging | In `core/settings.py` line 310, `if not DEBUG` guards Sentry init. Staging runs with `DEBUG=True`, so all staging errors are invisible. Change to `if ENVIRONMENT != "DEV"`. |
| 30 | NORMAL | Use bulk_update in BulkUpdateArchiveSettingsView | In `user_sessions/views/archive_settings_view.py` lines 152-156, one `.get()` + `.save()` per item creates 2N queries. Fetch all settings in one query with `filter(id__in=ids)` and use `bulk_update()`. |
| 31 | NORMAL | Fix double-serialized JSON in Session.devices_json | In `SessionBasedModel.py` lines 146-150, `json.dumps(data)` is called before assigning to a `JSONField`, which auto-serializes. This double-serializes the data. Remove the manual `json.dumps()`. |
| 32 | NORMAL | Remove duplicate scheduling libraries from requirements.txt | `django-background-tasks`, `APScheduler`, and `django-apscheduler` are all installed but only one is used. Remove unused ones. |
| 33 | NORMAL | Fix max_page_size=1000 causing large payloads | In `core/pagination.py` line 9, `max_page_size = 1000` with complex nested serializers can return massive responses. Lower to 100 or add per-view overrides. |
| 34 | LOW | Remove 150+ lines of commented-out code in stats views | In `user_sessions/views/stats_view.py` lines 708-865, `session_views.py`, and `userSerializer.py`. Dead code creates noise and confusion. |
| 35 | LOW | Fix subject_ID field naming to subject_id | In `users/models/baseUserModel.py` line 92, `subject_ID` violates Python naming conventions. Should be `subject_id`. Requires migration. |
| 36 | LOW | Remove dead Register view from social_auth.py | The `Register` class in `users/views/social_auth.py` is never mapped to any URL. Remove it. |
| 37 | LOW | Remove CreateWorkerAccountView commented-out logic or complete the feature | In `users/views/createWorkerAccount.py` lines 48-65, the entire creation logic is commented out. The endpoint only sends an invitation. Either complete it or rename it to reflect actual behavior. |
| 38 | HIGH | Write unit tests for critical business logic | Zero test files exist in the project. Priority test targets: session processing logic, signal handlers, permission checks, date calculations, merge operations, and cron commands. Start with the most bug-prone areas identified in this audit. |

---

## MOBILE — Flutter App

| # | Priority | Title | Description |
|---|----------|-------|-------------|
| 39 | HIGH | Fix UserCubit.user getter crash when state is not LoggedIn | In `user_cubit.dart` line 26, `(state as UserStateLoggedIn).user` throws CastError if state is Loading or Error. This getter is called in many places without a state guard. Change return type to `UserEntity?` or add a guard that returns null when not logged in, and update all callers. |
| 40 | HIGH | Fix force-unwrap crash on currentWorkSession in stopAllMeasurements | In `measurements_manager_cubit.dart` line 272, `_workSessionCubit.currentWorkSession!` crashes when null. This fires from `FeedbackScreen.dispose()` which runs even without an active session. Add null guard: `if (currentWorkSession == null) return`. |
| 41 | HIGH | Move SafeArea from MaterialApp wrapper to individual screens | In `app.dart` line 441, `SafeArea` wraps the entire `MaterialApp`. This causes every screen to lose control of its own system-bar handling, breaks bottom sheets, dialogs, and splash screens. Remove from app.dart, add to individual Scaffold bodies where needed. |
| 42 | HIGH | Fix LateInitializationError when user.organization is null | In `work_session_listing.page.dart` lines 99-107, `_workSessionListingCubit` is `late final` but only assigned inside an `if (user.organization != null)` block. If org is null, any reference throws `LateInitializationError`. Always assign the field or make it nullable. |
| 43 | HIGH | Fix SessionTimerCubit emitting initial state every tick | In `session_timer_cubit.dart` line 35, every 1-second tick emits `initial()` before `timerUpdated()`. This causes double-rebuilds and visual flicker on all timer widgets. Remove the `emit(const SessionTimerState.initial())` line from the timer callback. |
| 44 | HIGH | Fix deep links only configured for staging host | In `AndroidManifest.xml` lines 22-30, `autoVerify` intent-filters only specify `staging.cloud.wergonic.com`. Production host `cloud.wergonic.com` lacks path-specific filters and autoVerify. Password reset and magic login deep links from production emails will open in browser. Add production host intent-filters. |
| 45 | HIGH | Fix SettingsEntity.copyWith parameter name mismatches | In `settings.entity.dart` lines 138-175, several copyWith parameters don't match their field names (e.g. `voiceFeedbackInterval` vs field `voiceFeedbackIntervals`, `instantFeedbackRefreshRate` vs `feedbackRefreshRate`). Calling `copyWith` with field names silently does nothing. Align all parameter names to field names. |
| 46 | HIGH | Fix FeedbackScreen.dispose not awaiting stopAllMeasurements | In `feedback_screen.page.dart` line 60, `stopAllMeasurements()` is called without await in `dispose()`. Since dispose can't be async, CSV flush and stream cleanup may be orphaned causing data loss. Move cleanup to `onFinishWorkSession` in the recording screen (which is async) before navigating away. |
| 47 | HIGH | Fix enum toString() returning translated strings (breaks serialization) | In `enums.dart` lines 26-48, `SessionEventActivityMode.toString()` and `BleDeviceConnectionStatus.toString()` call `.tr()`. If used for serialization/API calls, values change per locale (e.g. "Rijden" instead of "driving" on Dutch devices). Add a separate `toApiString()` method for serialization, keep `toString()` for display only. |
| 48 | NORMAL | Fix WorkCycle enum value violating Dart naming convention | In `enums.dart` line 664, `WorkSessionType.WorkCycle` uses PascalCase. Dart enum values must be camelCase: `workCycle`. Fix and update all references. |
| 49 | NORMAL | Fix SessionSyncCubit bypassing BlocProvider lifecycle | In `session_summary.page.dart` line 47 and `work_session_listing.page.dart` line 93, `SessionSyncCubit` is created with raw `locator` in `initState`. This bypasses the BlocProvider pattern, causes lifecycle issues, and makes the cubit inaccessible to child widgets. Provide via `BlocProvider` at route level. |
| 50 | NORMAL | Remove double dispose of _debouncer in WorkSessionListPage | In `work_session_listing.page.dart` lines 112 and 117, `_debouncer.dispose()` is called twice. Remove one. |
| 51 | NORMAL | Fix InternetCubit managing UI animation state | In `internet_cubit.dart`, the cubit directly manages animation heights and visual state. Move animation logic to the widget layer using `AnimationController`, keep the cubit as a simple `isOnline` boolean emitter. |
| 52 | NORMAL | Fix WorkCycleCubit force-unwrap on nullable workCycleTaskList | In `work_cycle_cubit.dart` line 63, `workCycleTaskList![indexTask]` crashes if the list hasn't been fetched. Replace with `workCycleTaskList?[indexTask]`. |
| 53 | NORMAL | Reduce unnecessary rebuilds in WorkSessionRecordingScreen | In `work_session_recording.page.dart` lines 158-238, three nested `BlocBuilder`s rebuild the entire screen on any state change during active sessions. Use `BlocSelector` or `buildWhen` to limit rebuilds. Split into smaller widgets. |
| 54 | NORMAL | Fix SettingsCubit bypassing state stream with mutable public field | In `settings_cubit.dart` line 35, `settings` is a public mutable field read directly by widgets. Changes don't trigger rebuilds reliably. Move settings into the cubit state so `BlocBuilder` works correctly. |
| 55 | NORMAL | Fix SessionHistoryCubit always mutating timestamps[0] | In `session_history_cubit.dart` lines 45-52, `timeStamps[0]` is hardcoded regardless of which timestamp should be updated. This silently corrupts data for events with multiple timestamps. Pass the correct index. |
| 56 | NORMAL | Fix WorkSessionEntity mutability bypassing state management | In `work_session.entity.dart` line 42, `syncStatus`, `startedAt`, `endedAt`, `sessionEvents` are mutable public fields. Multiple places directly mutate `_sessionCubit.currentWorkSession`, bypassing the state machine. Make fields final and use copyWith pattern. |
| 57 | NORMAL | Replace debugPrint with structured logger throughout cubit layer | `debugPrint` calls in `work_session_cubit.dart`, `measurements_manager_cubit.dart`, `session_sync_cubit.dart` disappear in release builds. Use the already-imported `logger` package for operational events that need production visibility. |
| 58 | NORMAL | Consolidate dual database systems (drift + isar) | Both `drift` and `isar` are declared as dependencies in `pubspec.yaml`. Running two embedded databases doubles storage and maintenance. Choose one and migrate. |
| 59 | NORMAL | Pin git dependencies to commit SHAs | `sensors_plus` and `shake` point to personal forks on `master` branch without commit pinning. A `flutter pub get` can silently pull breaking changes. Pin to specific commit SHAs. |
| 60 | NORMAL | Translate hardcoded English error messages | In `session_bloc_listeners.widget.dart` lines 83-102 and `work_session_cubit.dart` line 134, user-visible error messages bypass the translation system. Wrap in `.tr()` and add translation keys. |
| 61 | NORMAL | Remove BLUETOOTH_PRIVILEGED permission from manifest | In `AndroidManifest.xml` line 81, this is a signature-level permission that has no effect on regular apps. Remove to avoid Play Store review confusion. |
| 62 | NORMAL | Fix "Clase" enum typo | In `enums.dart` line 294, `enum Clase { vibrator, sensor }` is misspelled (Spanish for "Class"). Rename to `DeviceClass` or `SensorClass` with proper documentation. |
| 63 | NORMAL | Implement sessionDurationLimit enforcement | In `settings.entity.dart` line 83, `sessionDurationLimit` (default 8h) exists as a setting but `SessionTimerCubit` never checks or enforces it. Add a warning or auto-stop when the limit is reached. |
| 64 | LOW | Split app.dart MultiBlocProvider into logical groups | `app.dart` has 25+ BlocProviders in a single 480-line build method. Extract into grouped factory classes (auth, bluetooth, session, settings) for maintainability. |
| 65 | LOW | Remove commented-out print blocks from production code | In `work_session_listing_cubit.dart` lines 48-59 and others, large blocks of commented-out debug prints exist. Clean up. |
| 66 | HIGH | Write unit tests for critical business logic | Zero real tests exist (only the default Flutter stub). `bloc_test` and `mockito` are commented out in pubspec. Priority: calibration logic, session state management, sync flow, CSV writing, BLE reconnection. |

---

## WEB — Client Panel (React/TypeScript)

| # | Priority | Title | Description |
|---|----------|-------|-------------|
| 67 | HIGH | Fix useHook called inside render function in ActiveSessionsTable | In `ActiveSessionsTable.hooks.tsx` line 222, `useTheme()` is called inside a Cell render function. This violates Rules of Hooks. Extract `useTheme()` to the top level of `useColumns` or move the Cell into its own component. |
| 68 | HIGH | Fix ErrorFallback infinite loop in GlobalAppProvider | In `GlobalAppProvider.tsx` line 22, `resetErrorBoundary()` is called synchronously during render, creating an infinite loop (error -> reset -> error). Remove the `resetErrorBoundary()` call; the `<Navigate>` alone handles the redirect. |
| 69 | HIGH | Fix useSetURLParamsOnMount infinite loop | In `setURLParamsOnMount.ts` line 21, `searchParams` in the dependency array triggers re-runs every time `setSearchParams` creates a new reference. Change to empty dependency array `[]` to run only on mount. |
| 70 | HIGH | Fix unhandled rejection in useAuth crashing auth flow | In `auth.ts` lines 19-44, `retrieveCurrentUser()` inside `onAuthStateChanged` has no try/catch. If backend returns an error, the user is stuck in loading state forever. Wrap in try/catch, call `setPendingAuthState(false)` in finally. |
| 71 | HIGH | Fix noMoreData state never resetting when filters change | In `ActiveSessionsTable.hooks.tsx` lines 82-117, `noMoreData` is set `true` but never reset when `showInterrupted` toggles. Users get permanently disabled "load more" button. Add `setNoMoreData(false)` at the start of the useEffect. |
| 72 | HIGH | Fix setTimeout race condition in PDF generation | In `ReportExportButton.tsx` lines 143-158, `setTimeout(..., 50)` is used to "wait" for state updates before triggering PDF generation. Under React 18 concurrent rendering this is unreliable. Replace with a `useEffect` that depends on `[selectedTaskId, shouldDownloadPDF]`. |
| 73 | HIGH | Fix OAuth user.delete() not being awaited | In `useLoginForm.hooks.tsx` lines 58 and 89, `user.delete()` for Google/Microsoft OAuth new users is called without `await`. The Firebase account briefly exists and `onAuthStateChanged` may fire before deletion completes. Add `await` before the delete call. |
| 74 | NORMAL | Add guard for undefined organizationId in Firestore listeners | In `NotificationsButton.hooks.ts` lines 17-25, `ActiveSessionsTable.hooks.tsx` line 84, and interrupted/non-interrupted session count hooks — all create Firestore listeners without checking if `organizationId` is defined. Add `if (!organizationId) return;` early return. |
| 75 | NORMAL | Fix RAMP form validation marking null values as filled | In `formValidation.ts` line 17, `Boolean(values[current]) || values[current] !== ""` returns `true` for `null`/`undefined` because `null !== ""` is true. Change to `values[current] !== "" && values[current] != null`. |
| 76 | NORMAL | Fix wrong component name in AssessmentsPage error | In `AssessmentsPage.tsx` line 64, the thrown error says "RAMPPage" but it's in `AssessmentsPage`. Update the message. |
| 77 | NORMAL | Add null check for started_at in active sessions table | In `ActiveSessionsTable.hooks.tsx` line 199, `parseISO(value)` is called without checking if value is null. Add: `value ? format(parseISO(value), "LLL dd, yyyy p") : "N/A"`. |
| 78 | NORMAL | Gate ReactQueryDevtools to dev-only | In `GlobalAppProvider.tsx` line 51, devtools render in all builds. Wrap with `{import.meta.env.DEV && <ReactQueryDevtools ... />}` to exclude from production bundle. |
| 79 | NORMAL | Reduce global staleTime for session-related queries | In `GlobalAppProvider.tsx` line 31, `staleTime: 15min` is too long for real-time data (active sessions, notifications). Override with shorter staleTime on session-specific queries. |
| 80 | NORMAL | Fix SessionDetailesInfoSection typo in component name | Component and folder named `SessionDetailesInfoSection` (extra 'e'). Rename to `SessionDetailsInfoSection`. |
| 81 | NORMAL | Fix env variable typo VITE_API_BASE_URl (lowercase l) | In `axios.ts` line 6 and `.env.example`, the variable ends with lowercase `l`. While consistent internally, it will cause a hard-to-debug issue if someone creates a new env file using standard `URL` suffix. Rename to `VITE_API_BASE_URL`. |
| 82 | NORMAL | Fix SessionsPage dual state management (useState + searchParams) | In `SessionsPage.tsx`, `selectedTab` is maintained in both `useState` and `searchParams`. Browser back button works but direct `setSelectedTab` calls don't update the URL. Derive state purely from searchParams. |
| 83 | NORMAL | Enable ESLint failOnError in Vite build config | In `vite.config.ts` lines 21-24, `failOnError: false` allows shipping builds with known lint errors. Set `failOnError: true` to catch regressions. |
| 84 | NORMAL | Fix AIExplanation loading state never set to true | In `AIExplanation.tsx` lines 39-138, `loading` is declared as `useState(false)` and only ever set to `false` in error handlers — never to `true`. The loading guard on line 138 is dead code. Either add `setLoading(true)` before async operations or remove the state entirely. |
| 85 | NORMAL | Replace == with === for string comparisons throughout | In `compareSessions.ts` and `assessments.ts`, strings are compared with `==` instead of `===`. While functionally equivalent for strings, it bypasses TypeScript type safety. Use strict equality. |
| 86 | NORMAL | Write unit tests for calculation functions and form validation | Zero test coverage exists. Priority targets: RAMP/REBA/RULA score calculations, `formValidation.ts`, `compareSessions.ts`, auth hooks, and the `functions.ts` utilities. |
| 87 | LOW | Remove deprecated fillIfNull utility function | In `functions.ts` lines 42-48, the function has a comment saying to use `displayOrFallback` from ui instead. Remove and migrate callers. |
| 88 | LOW | Remove "todo delete all comments" in apiRoutes.ts | Line 1 has `// todo delete all comments` that was never acted on. Either clean the comments or remove the todo. |
| 89 | LOW | Upgrade react-table v7 to @tanstack/react-table v8 | react-table v7 is unmaintained and has React 18 compatibility issues. Plan migration to @tanstack/react-table v8. |
| 90 | LOW | Fix ErrorPage hardcoded width breaking on mobile | In `ErrorPage.tsx` line 17, `width="539px"` overflows on narrow screens. Change to `maxWidth="539px"`. |

---

## WEB — Landing Page (Next.js)

| # | Priority | Title | Description |
|---|----------|-------|-------------|
| 91 | HIGH | Wire up contact form to actual submission endpoint | In `ContactFormSection.tsx` lines 36-39, `handleSubmit` only calls `console.log`. Visitors fill the form and nothing happens. Connect to a form service (Resend, Formspree, or a custom API endpoint) and add success/error UI feedback. |
| 92 | HIGH | Replace placeholder leadership team data | In `LeadershipSection.tsx` lines 36-40, all 4 team members are "Farhad Abtahi, CEO & Co-Founder". This is placeholder data visible on the live site. Replace with actual team names and roles. |
| 93 | HIGH | Replace placeholder phone number | In `OfficeInfoSection.tsx` line 34, `"+46 700 XXX XXX"` is a visible placeholder. Replace with real number or remove the phone card. |
| 94 | HIGH | Fix all CTA buttons having no destination | Across HeroSection, ActionSection, CTASection, ProductsCTASection, ProductDetailSection, DPAHeroSection, QuickActionsSection — buttons like "Start Free Trial", "Download Android App", "Access Cloud Dashboard", "Schedule a Consultation", "Request Demo" have no href or onClick. Each needs a real destination URL. |
| 95 | HIGH | Add unique metadata to every page | Only the homepage has metadata. About, Products, Contact, Data Protection, and DPA pages all inherit the homepage title/description, causing duplicate SEO signals. Add unique `export const metadata` to each page file. |
| 96 | HIGH | Add robots.txt and sitemap.xml | Neither exists. With static export, Next.js doesn't generate these automatically. Add `public/robots.txt` and `public/sitemap.xml` listing all 6 routes. |
| 97 | HIGH | Add Open Graph and Twitter Card meta tags | No `openGraph` or `twitter` properties in root metadata. LinkedIn and X shares show no preview image or branded content. Add to root layout and override per page. |
| 98 | NORMAL | Fix contact page email casing (Sales@Wergonic.Com) | In `ContactHeroSection.tsx` lines 42-46, emails display as titlecased. Change to lowercase: `sales@wergonic.com`, `support@wergonic.com`, `partnerships@wergonic.com`. |
| 99 | NORMAL | Fix HowItWorksSection steps 2-4 using same image | In `HowItWorksSection.tsx` lines 28-43, steps 02, 03, 04 all reference `/how_it_works_2.png`. Add distinct images for each step. |
| 100 | NORMAL | Fix DPA Executive Summary showing product features instead of legal content | In `DPAHeroSection.tsx` lines 7-12, the summary lists "Advanced Sensor Fusion Algorithms" etc. — product features, not DPA content. Replace with actual DPA summary points (data residency, retention, breach notification). |
| 101 | NORMAL | Add image optimization (lazy loading, priority hints, dimensions) | `unoptimized: true` in next.config and all `<img>` tags lack `loading="lazy"` or `fetchpriority`. Add `loading="lazy"` to below-fold images, `fetchpriority="high"` + explicit dimensions to the hero image. Consider a CDN image service. |
| 102 | NORMAL | Add metadataBase for canonical URLs | No `metadataBase` is set in root layout. Add `metadataBase: new URL('https://wergonic.com')` to generate correct canonical and og:url tags. |
| 103 | NORMAL | Add JSON-LD structured data | No Organization, Product, or FAQPage schema exists. Add at minimum `Organization` schema in root layout and `FAQPage` on DPA page. |
| 104 | NORMAL | Fix mobile menu missing focus trap | In `Navbar.tsx` lines 152-193, the mobile drawer has no focus trap. Keyboard users can tab behind the overlay. Add focus trapping when menu is open. |
| 105 | NORMAL | Remove unused UI components cluttering the codebase | `StatCard`, `FeatureCard`, `ProductCard`, `PartnerCard`, `StepIndicator`, `ChecklistItem`, `GradientButton`, `GradientTextButton`, `ImageWithGradient`, `GradientBlur`, `GlassCard`, `IconBox`, `GradientText`, `NavLink` are all exported but never used. The sections implement their own inline versions. Either use the components or delete them. |
| 106 | NORMAL | Replace hardcoded #5266F3 with Tailwind primary color class | Across 10+ files, `text-[#5266F3]`, `bg-[#5266F3]`, `from-[#5266F3]` are hardcoded instead of using `text-primary`, `bg-primary`. A brand color change would require multi-file find-replace. |
| 107 | LOW | Fix Logo using CSS invert filter instead of proper dark variant | In `Logo.tsx` line 28, `invert` flips a white logo PNG to appear dark. Use an SVG with configurable fill or ship a separate dark logo asset. |
| 108 | LOW | Remove redundant build:production script | In `package.json`, `build:production` is identical to `build`. Remove or differentiate. |
| 109 | LOW | Fix btn-secondary missing explicit text color | In `globals.css` lines 413-430, `.btn-secondary` has no `color` property — text color works by inheritance. Add `color: var(--color-text-primary)` explicitly to prevent invisibility on dark sections. |

---

## Summary

| Category | HIGH | NORMAL | LOW | Total |
|----------|------|--------|-----|-------|
| Both | 2 | 3 | 0 | 5 |
| Backend | 15 | 12 | 4 | 31 |
| Mobile | 10 | 16 | 2 | 28 |
| Web App | 7 | 13 | 4 | 24 |
| Landing Page | 7 | 9 | 3 | 19 |
| **Total** | **41** | **53** | **13** | **109** |

---

## Recommended Execution Order

1. **Security fixes first** (tasks 6, 7, 13, 14, 15, 16, 18 — backend)
2. **Crash-causing bugs** (tasks 8, 9, 10, 11, 39, 40, 41, 42, 43, 45, 46, 47 — backend + mobile)
3. **User-facing broken features** (tasks 91, 92, 93, 94, 95, 96, 97 — landing page)
4. **Data integrity issues** (tasks 12, 17, 19, 31, 55, 56 — backend + mobile)
5. **Frontend bugs** (tasks 67-73 — web app)
6. **Performance** (tasks 20, 21, 22, 30, 53, 78, 79)
7. **Code quality & terminology** (remaining NORMAL tasks)
8. **Testing** (tasks 38, 66, 86 — ongoing)
9. **Polish** (LOW priority tasks)
