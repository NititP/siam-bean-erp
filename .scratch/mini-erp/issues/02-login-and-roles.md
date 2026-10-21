# 02: Part 3: Login, current user and roles

Part: 3
Status: resolved

**What to build:** Staff log in with email and password, see their name and role, and see a menu with only the screens their role may use. Opening a screen their role may not use shows an access-denied page. The API checks the token on every request and offers a role requirement that returns 403 to anyone else. Tests can log in as any demo user by role.

**Blocked by:** 01 (Part 3: Skeleton)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] No token on any endpoint except health returns 401
- [ ] `GET /me` returns email, full name and role for each of the five demo users
- [ ] A role requirement returns 403 for a role not on the list (tested on a small protected endpoint)
- [ ] The test fixture `client_as(role)` logs the request in as the matching demo user
- [ ] Login page logs in through Supabase, then shows the layout with name and role; a wrong password shows an error
- [ ] Menu shows only the role's screens (role matrix in `docs/plan.md`)
- [ ] Opening a forbidden page shows the access-denied page
- [ ] Logout returns to the login page
