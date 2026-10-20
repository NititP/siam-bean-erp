# 23: Part 3: Auth hardening (review follow-ups from 02)

Part: 3
Status: ready-for-agent

**What to build:** Close the three gaps the ticket 02 review found, before Parts 1 and 2 add real endpoints. Every endpoint except the health check needs a login without each owner having to remember it. When Supabase cannot be reached, the API answers with a clear message instead of a bare server error. Every demo login, including the second sales user, is checked.

**Blocked by:** 02 (Part 3: Login, current user and roles)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`. Review notes: PR #2.

- [x] Every API route except `/health` returns 401 without a token, checked by one test over all registered routes, so an endpoint added later without `require_roles` still needs a login
- [x] Login is required for every router once, in the app setup; router owners add `require_roles(...)` only where a role limit applies
- [x] When Supabase cannot be reached, any endpoint returns 503 with a `detail` message saying to try again, not a 500
- [x] `GET /me` returns Ploy (`ploy@example.com`, sales) when logged in as her; `client_as` can log in as a specific demo user, not only one per role
