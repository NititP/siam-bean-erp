# 01: Part 3: Skeleton

Part: 3
Status: ready-for-agent

**What to build:** A running backend and frontend that every other Part builds on. The backend answers a health check and already registers an empty router for every module (me, products, customers, stock, dashboard, purchasing, orders, invoices, accounting), each in its owner's file, so Parts 1 and 2 never touch app setup. The test setup resets the demo data before each test and holds a file lock outside the repos so only one test run happens at a time across the three copies. The frontend shell has a route for every page pointing at a placeholder in its owner's file, an API client that sends the token and surfaces the API's `detail`, the THB money formatter, and shared empty-list and error components.

**Blocked by:** None (can start immediately)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `GET /health` returns 200 without login, proven by a test
- [ ] Every module's router is registered and starts empty
- [ ] Each test starts from `reset_demo_data('yes-reset')`
- [ ] Two test runs started at once (from two repo copies) run one after the other, not interleaved
- [ ] Frontend builds (`npm run build`) and every planned page route shows its placeholder
- [ ] Money formatter shows `9630` as `9,630.00 THB`
- [ ] Pushed to `main` so Parts 1 and 2 can pull it
