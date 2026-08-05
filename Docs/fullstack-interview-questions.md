# Full-Stack Developer Interview Questions — Mid Level

---

## TIER 1: Must Know (Red flag if they can't answer)

---

### Django ORM

**Q1: What's the difference between `select_related` and `prefetch_related`? When do you use each?**

A: `select_related` does a SQL JOIN in one query — use it for ForeignKey and OneToOne relationships. `prefetch_related` does a separate query per relationship and joins in Python — use it for ManyToMany and reverse ForeignKey. If they just say "both optimize queries" without explaining the mechanism, they haven't used them properly.

---

**Q2: You have a Session model with `worker = ForeignKey(Profile, null=True)`. You write `Session.objects.first().worker.user.email`. What can go wrong?**

A: Three things can blow up: `first()` returns None if no sessions exist, `worker` can be None because it's nullable, and `user` on Profile could also be None. Each `.` is a potential AttributeError. The safe approach is to check for None at each step or use `select_related` with a filter that excludes nulls. This is a real bug pattern in our codebase — if they don't mention null safety, that's a concern.

---

**Q3: What does `on_delete=SET_NULL` vs `CASCADE` vs `PROTECT` mean? Give a real example of when you'd use each.**

A: `CASCADE` deletes the child when parent is deleted (e.g., delete a User, delete their Notifications). `SET_NULL` keeps the child but nulls the FK (e.g., delete a Worker Profile but keep their Sessions for historical data). `PROTECT` prevents deletion if children exist (e.g., can't delete an Organization that still has users). If they only know CASCADE, they'll make dangerous schema decisions.

---

**Q4: You have a queryset that's slow. How do you figure out what's going on?**

A: `django-debug-toolbar` or `connection.queries` to see actual SQL. Look for N+1 queries (missing select/prefetch_related), missing indexes, or unnecessary fields being loaded (use `.only()` or `.defer()`). `QuerySet.explain()` shows the DB execution plan. If they jump to "add an index" without diagnosing first, they're guessing.

---

### Django REST Framework

**Q5: Explain the difference between a Serializer, ModelSerializer, and a ViewSet. How do they connect?**

A: Serializer handles raw data validation and transformation. ModelSerializer auto-generates fields from a Django model and handles create/update. ViewSet combines multiple views (list, create, retrieve, update, destroy) into one class and hooks into a router for URL generation. The ViewSet uses the Serializer to validate input and format output. If they can't explain the flow from request → URL → ViewSet → Serializer → Model, they haven't built APIs with DRF.

---

**Q6: How do you write a custom permission class in DRF? Give an example.**

A: Subclass `BasePermission`, override `has_permission` (for list/create) and/or `has_object_permission` (for retrieve/update/delete). Example: checking if the requesting user belongs to the same organization as the object they're accessing. Return True to allow, False to deny.

```python
class SameOrgPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.organization == request.user.organization
```

If they say "I just use IsAuthenticated" they haven't built multi-tenant apps.

---

**Q7: What's the difference between `authentication` and `permission` in DRF?**

A: Authentication answers "who are you?" (identifies the user from the request — token, session, etc.). Permission answers "are you allowed to do this?" (checks roles, ownership, etc.). Authentication runs first, then permissions. A request can be authenticated but still denied by permissions. If they mix these up, they'll create security holes.

---

**Q8: How do you handle nested serializer writes? For example, creating a User and their Profile in one API call.**

A: Override `create()` on the serializer. ModelSerializer's default `create()` doesn't handle nested writes. You pop the nested data, create the parent, then create the children manually. Same for `update()`. You need to handle transactions with `@transaction.atomic` to avoid partial creates.

```python
def create(self, validated_data):
    profile_data = validated_data.pop('profile')
    user = User.objects.create(**validated_data)
    Profile.objects.create(user=user, **profile_data)
    return user
```

---

### React + TypeScript

**Q9: What's the difference between `type` and `interface` in TypeScript? When would you use each?**

A: Both define shapes. Interfaces can be extended and merged (declaration merging), types can do unions, intersections, and mapped types. In practice: use interfaces for object shapes that might be extended, types for unions, function signatures, and computed types. Our codebase convention: `IName` for interfaces, `TName` for types. If they say "they're the same" they haven't hit the differences.

---

**Q10: What's a generic in TypeScript? Write a simple one.**

A: A generic lets you write reusable typed code without using `any`. Example:

```typescript
function getFirst<T>(items: T[]): T | undefined {
    return items[0];
}
```

The type flows through: `getFirst<string>(["a", "b"])` returns `string | undefined`. If they can't write a basic generic, they'll fall back to `any` which kills type safety.

---

**Q11: Explain the rules of React hooks. Why can't you put a hook inside a condition?**

A: Hooks must be called in the same order every render — React tracks them by position, not name. Inside a condition, a hook might not run on some renders, which shifts the order and breaks everything. This is why custom hooks must also follow the rules (always call them at the top level). If they don't know this, they'll write hooks that randomly break.

---

**Q12: What's a custom hook? When do you extract one?**

A: A function that starts with `use` and calls other hooks inside. You extract one when component logic is reusable or when a component is doing too much (data fetching + transformation + state management all inline). Example: `useAuth()` that handles Firebase state + API sync. If they never write custom hooks, their components will be 300+ lines of mixed concerns.

---

**Q13: What's the difference between `useMemo`, `useCallback`, and `React.memo`? When do you actually need them?**

A: `useMemo` caches a computed value. `useCallback` caches a function reference. `React.memo` prevents a component from re-rendering if props haven't changed. You need them when: passing callbacks to memoized children, expensive computations on every render, or preventing unnecessary re-renders in lists. If they say "I put useMemo everywhere for performance" that's a red flag — unnecessary memoization adds complexity for no gain.

---

### React Query

**Q14: Why use React Query instead of just fetching in useEffect?**

A: React Query gives you caching (don't re-fetch data you already have), background refetching (stale-while-revalidate), automatic retry, pagination/infinite scroll support, cache invalidation, and loading/error states out of the box. With useEffect you manually handle all of this, usually badly. If they've only used useEffect + useState for API calls, they'll need ramp-up time on our codebase.

---

**Q15: How does cache invalidation work in React Query? You update a user — how do you make sure the users list reflects the change?**

A: After a mutation, you call `queryClient.invalidateQueries(['users'])` to mark the cached list as stale, triggering a refetch. Or use `onSuccess` in `useMutation` to invalidate automatically. You can also do optimistic updates with `onMutate` for instant UI feedback. If they say "I just refetch everything" they'll create unnecessary network requests.

---

### State Management

**Q16: You have user auth data, a theme toggle, a list of sessions from the API, and a form being filled out. Where does each piece of state live?**

A: Auth data → Jotai atom (global, persists across pages). Theme → Jotai atom (global UI state). Sessions list → React Query cache (server state, cached and synced). Form → local component state or Formik (ephemeral, discarded after submit). If they put everything in one global store (Redux-style), they don't understand the server state vs client state split.

---

### Firebase Auth

**Q17: Explain how token-based auth works between a React frontend, Firebase, and a Django backend.**

A: User logs in via Firebase on the frontend → Firebase returns an ID token (JWT). Frontend attaches this token to every API request as `Authorization: Bearer <token>`. Django backend has a custom authentication class that intercepts the request, verifies the token with Firebase Admin SDK, extracts the UID, and maps it to a Django User. Token expires → frontend gets a fresh one from Firebase automatically. If they can't trace this flow, they'll struggle debugging auth issues.

---

**Q18: What are Firebase custom claims? Why would you use them?**

A: Custom claims are key-value pairs set on a Firebase user's token server-side (from Django). Example: `{ role: "ORG_ADMIN", org_id: "123" }`. The frontend can read them without an API call, and the backend can trust them because they're in a signed token. We use them to store user role and organization. If they don't know claims, they'll make unnecessary API calls for role checks.

---

### Docker

**Q19: You run `docker compose up` and the Django container can't connect to PostgreSQL. How do you debug?**

A: Check if the DB container is actually running (`docker compose ps`). Check if Django is using the right host (should be the service name, not localhost). Check if the DB port is exposed correctly. Check container logs (`docker compose logs db`). Check if the DB is ready before Django starts (depends_on only waits for container start, not readiness — might need a healthcheck or wait script). If they say "restart everything" as step one, they debug by guessing.

---

### Testing

**Q20: How would you test a DRF endpoint that requires authentication and checks organization-level permissions?**

A: Use DRF's `APIClient`. Create a test user with the right role and organization. Authenticate the client (`client.force_authenticate(user=user)` or pass the token). Hit the endpoint and assert status code + response data. Test both allowed and denied cases — same org should work, different org should return 403. Test with no auth should return 401.

```python
def test_user_can_access_own_org_sessions(self):
    self.client.force_authenticate(user=self.org_admin)
    response = self.client.get(f'/api/v1/sessions/?org={self.org.id}')
    self.assertEqual(response.status_code, 200)

def test_user_cannot_access_other_org_sessions(self):
    self.client.force_authenticate(user=self.other_org_admin)
    response = self.client.get(f'/api/v1/sessions/?org={self.org.id}')
    self.assertEqual(response.status_code, 403)
```

If they only test happy paths, bugs will ship.

---

---

## TIER 2: Should Know (50/50 — separates okay from good)

---

### Django

**Q21: What are Django signals? Give an example. What's the downside of overusing them?**

A: Signals are hooks that fire on model events (pre_save, post_save, pre_delete, etc.). Example: after creating a User, fire a signal to create their Firebase account. Downside: they create invisible side effects — you save a model and something happens elsewhere that's hard to trace, test, or debug. Overuse leads to "action at a distance" bugs. We use them for Firebase user sync and notification pushes.

---

**Q22: What's `@transaction.atomic` and when do you need it?**

A: It wraps a block of code in a database transaction — if anything fails, all changes roll back. You need it when creating multiple related objects (e.g., User + Profile + UserOrganization) where partial creation would leave broken data. If they don't think about transactions, they'll create orphaned records.

---

**Q23: How do Django migrations work? What do you do when two developers create conflicting migrations?**

A: Django auto-generates migration files from model changes. Each migration depends on the previous one. Conflicts happen when two branches add migrations with the same number. Fix: `python manage.py makemigrations --merge` creates a merge migration. If they say "delete migrations and recreate" they'll destroy production data history.

---

**Q24: What's the N+1 query problem? Show how it happens in Django and how to fix it.**

A: Accessing a related object in a loop triggers a new query per iteration.

```python
# N+1: 1 query for sessions + N queries for worker
for session in Session.objects.all():
    print(session.worker.name)  # DB hit each time

# Fixed: 1 query with JOIN
for session in Session.objects.select_related('worker').all():
    print(session.worker.name)  # Already loaded
```

If they've never profiled queries, their code will be slow on real data.

---

### React + TypeScript

**Q25: How do you type a component's props that accepts children and an optional callback?**

A:
```typescript
interface IButtonProps {
    children: React.ReactNode;
    onClick?: () => void;
    variant?: 'primary' | 'secondary';
}

const Button: React.FC<IButtonProps> = ({ children, onClick, variant = 'primary' }) => { ... }
```

If they use `any` for props or don't know `React.ReactNode`, their components won't be type-safe.

---

**Q26: What's the difference between controlled and uncontrolled components? When would you use each?**

A: Controlled: React state drives the input value (`value={state}` + `onChange`). Uncontrolled: DOM holds the value, you read it with a ref. Use controlled for forms where you need validation/formatting on each keystroke. Use uncontrolled for simple forms or file inputs. If they don't know this distinction, form bugs will be hard to trace.

---

**Q27: How does React's reconciliation work? Why do keys matter in lists?**

A: React builds a virtual DOM tree, diffs it against the previous one, and only updates what changed. Keys tell React which items in a list are the same across renders. Without proper keys (or using array index), React can't match items correctly — leading to stale state, broken animations, or re-mounting when it shouldn't. If they say "keys are just to suppress the warning," they don't understand the rendering model.

---

**Q28: How would you handle error boundaries in a React app?**

A: Class component with `componentDidCatch` and `getDerivedStateFromError`. Wraps a tree — if any child throws during render, the boundary catches it and shows a fallback UI instead of crashing the whole app. Can't be done with hooks (class component only). Use `react-error-boundary` library for a hooks-friendly API. We use this in both our apps.

---

### API Design

**Q29: You're building an endpoint that returns sessions filtered by date range, organization, and worker — with pagination. How do you design it?**

A: GET `/api/v1/sessions/?org=123&worker=456&date_from=2024-01-01&date_to=2024-03-01&page=1&page_size=20&ordering=-created_at`. Use DjangoFilterBackend for filtering, StandardResultsSetPagination for pagination, OrderingFilter for sorting. Return paginated response with `count`, `next`, `previous`, and `results`. If they put filters in the request body or ignore pagination, they'll build APIs that don't scale.

---

**Q30: What HTTP status codes should a REST API return for: successful creation, validation error, unauthorized, forbidden, not found?**

A: 201 Created, 400 Bad Request, 401 Unauthorized (no valid credentials), 403 Forbidden (authenticated but not allowed), 404 Not Found. If they can't distinguish 401 vs 403, their API error handling will confuse frontend developers.

---

### Git / Workflow

**Q31: You're working on a feature branch. Main has been updated. How do you get those updates into your branch?**

A: `git fetch origin` then either `git rebase origin/main` (cleaner history, rewrites commits) or `git merge origin/main` (preserves history, creates merge commit). Know when to use which: rebase for local-only branches, merge for shared branches. If they say "I just pull main and merge" without understanding rebase, their PRs will have messy histories.

---

**Q32: You accidentally committed a file with secrets. It's not pushed yet. How do you fix it?**

A: `git reset HEAD~1` to undo the commit (keeps changes), remove the file, add to `.gitignore`, re-commit. If already pushed: rewrite history with `git rebase -i` or `git filter-branch`, force push, and rotate the exposed secrets immediately. If they don't mention rotating the secrets, that's a security awareness gap.

---

---

## TIER 3: Nice Bonus (Good signal, not expected)

---

### Architecture

**Q33: What's the difference between a monorepo and multiple repos? Trade-offs?**

A: Monorepo: all code in one repo. Pros — shared code, atomic changes across packages, unified CI. Cons — larger repo, need tooling (Turborepo/Nx), longer CI if not cached. Multi-repo: separate repos per service. Pros — independent deploys, smaller scope. Cons — sharing code is hard, cross-repo changes need multiple PRs. We use a monorepo for our frontend — knowing this trade-off means they won't fight the setup.

---

**Q34: What's feature-driven (screaming) architecture? How is it different from grouping by technical layer?**

A: Feature-driven: folders are `features/auth/`, `features/sessions/`, `features/devices/` — each containing its own components, hooks, types, API calls. Layer-based: folders are `components/`, `hooks/`, `services/`, `types/` — features scattered across layers. Feature-driven is easier to navigate and delete features from. We enforce this in our ARCHITECTURE.md.

---

### Performance

**Q35: How would you optimize a Django endpoint that's returning data slowly?**

A: Diagnose first (check the SQL with debug toolbar). Common fixes: add `select_related`/`prefetch_related`, add database indexes, reduce serializer fields (don't return what the client doesn't need), use `.only()` to limit loaded fields, paginate results, add caching for expensive queries. If they jump to "add Redis caching" before checking the query, they're optimizing blind.

---

**Q36: What is stale-while-revalidate and how does React Query implement it?**

A: Show cached (stale) data immediately while fetching fresh data in the background. User sees instant results, then gets updated data when the fetch completes. React Query does this with `staleTime` (how long data is considered fresh) and `cacheTime` (how long unused data stays in memory). Our config uses 15-minute stale time. This is a core concept in our data fetching approach.

---

### Database

**Q37: What's a JSON field in PostgreSQL? When would you use it vs a separate table?**

A: PostgreSQL's `jsonb` stores structured JSON that's indexable and queryable. Use it for: flexible/variable schemas (assessment data that changes per type), denormalized aggregates (pre-calculated stats), or config blobs. Use a separate table when: you need to query/filter by the nested data frequently, need referential integrity, or the structure is consistent. We use JSON fields for session calculations and assessment data.

---

**Q38: What's a database index? When would you NOT add one?**

A: An index speeds up reads on a column by maintaining a sorted lookup structure. Don't add when: the table is small, the column has very low cardinality (e.g., boolean), or the table has heavy writes (indexes slow down inserts/updates). Also, composite indexes only help queries that use the leftmost columns. If they index everything, writes will suffer.

---

### Next.js

**Q39: What's the difference between SSR, SSG, and ISR in Next.js?**

A: SSR (Server-Side Rendering): page built on every request — dynamic but slower. SSG (Static Site Generation): page built at build time — fast but static. ISR (Incremental Static Regeneration): SSG + rebuilds in the background after a set time. Our landing page uses static export (pure SSG, no server needed). Knowing when to use which matters if we ever move to dynamic pages.

---

### Security

**Q40: What are the OWASP top vulnerabilities you watch for in a web app?**

A: SQL injection (use ORM, never raw SQL with user input), XSS (sanitize output, use React's built-in escaping), CSRF (Django handles with middleware + tokens), broken auth (token expiry, proper permission checks), IDOR (always check object ownership, don't trust user-supplied IDs). If they can name at least 3 with real examples, they think about security. If they've never heard of OWASP, they'll write vulnerable code.

---

---

## Practical Test (Optional — Give as Take-Home or Live)

**Task**: "Build a simple API + frontend that lists sessions for an organization. The API should have proper permissions (user can only see their org's data), pagination, and one filter. The frontend should display it in a table with loading and error states using React Query."

**What to evaluate**:
- Did they set up permissions correctly or just return everything?
- Did they handle the empty/error/loading states or just the happy path?
- Is the TypeScript typed properly or full of `any`?
- Did they paginate or dump everything?
- Is the code organized or one giant file?

This tells you more in 2 hours than 10 theoretical questions.
