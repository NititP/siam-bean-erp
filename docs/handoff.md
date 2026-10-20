# Handoff report: 2026-10-20 (end of day)

Facts were gathered from git, GitHub (`gh`), the repo files and the live URLs on
2026-10-20. Anything that could not be checked directly is marked **unverified**.
No secrets, passwords or `.env` contents appear here.

## 0. The three repo copies

Checked after `git fetch`, before anyone pulled:

| Copy | Part | Branch | Uncommitted | Unpushed | Local branches not merged into `main` | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `C:\Users\user\Documents\siam-bean-erp` | 3 | `main` | none | none | none | Was 6 commits behind `origin/main`. Then pulled to `175f118`; this report is committed on top of that. |
| `...\siam-bean-erp-1` | 1 | `main` (`74bbc28`) | none | none | none | **14 commits behind `origin/main`: pull before starting.** Six local feature branches, all already merged (PRs #5–#10), safe to delete: `feature/product-list`, `product-edit`, `product-deactivate`, `customer-list`, `customer-edit`, `customer-deactivate`. |
| `...\siam-bean-erp-2` | 2 | `main` (`175f118`) | none | none | none | Up to date. Six local feature branches, all already merged (PRs #12–#17), safe to delete: `feature/create-draft-order`, `order-list`, `confirm-order`, `invoice-list`, `accounting-receivables`, `record-payment`. |

No copy has stashes. On GitHub, no remote branch is unmerged into `main`.

## 1. Main

Latest commit before this report: `175f118` Merge pull request #17 from NititP/feature/record-payment.

All 17 PRs are merged, and none are open:

| PR | Title | Ticket | Part |
| --- | --- | --- | --- |
| #1 | Part 3: Skeleton | 01 | 3 |
| #2 | Part 3: Login, current user and roles | 02 | 3 |
| #3 | Part 3: Auth hardening | 23 | 3 |
| #4 | Part 3: Prepare backend for Render | 03 (backend half) | 3 |
| #5 | Product list with stock on hand and low-stock badge | 04 | 1 |
| #6 | Customer list with search and paging | 07 | 1 |
| #7 | Create and edit products | 05 | 1 |
| #8 | Deactivate and reactivate products | 06 | 1 |
| #9 | Create and edit customers | 08 | 1 |
| #10 | Deactivate and reactivate customers | 09 | 1 |
| #11 | Part 3: Prepare frontend for Cloudflare Pages | 03 (frontend half) | 3 |
| #12 | Create a draft sales order | 10 | 2 |
| #13 | Sales order list | 11 | 2 |
| #14 | Confirm sales order to invoice | 14 | 2 |
| #15 | Invoice list and detail | 15 | 2 |
| #16 | Accounting screen with receivables | 16 | 2 (taken over from 3) |
| #17 | Record a payment | 17 | 2 (taken over from 3) |

## 2. Tickets (`.scratch/mini-erp/issues/`)

The `Status:` line in every ticket file still says `ready-for-agent`, even for
merged tickets; nobody has updated them. The status column below comes from
the merged PRs and the code on `main`. No branch anywhere holds red tests or
other unfinished work.

| # | Title | Owner | Status |
| --- | --- | --- | --- |
| 01 | Skeleton | 3 | merged (#1) |
| 02 | Login, current user and roles | 3 | merged (#2) |
| 03 | Deploy live | 3 | **in progress**: code merged (#4, #11); Render and Pages are live, but CORS, the live logins and the URLs in `plan.md` are still open (see section 5) |
| 04 | Product list with stock on hand and low-stock badge | 1 | merged (#5) |
| 05 | Create and edit products | 1 | merged (#7) |
| 06 | Deactivate and reactivate products | 1 | merged (#8) |
| 07 | Customer list with search and paging | 1 | merged (#6) |
| 08 | Create and edit customers | 1 | merged (#9) |
| 09 | Deactivate and reactivate customers | 1 | merged (#10) |
| 10 | Create a draft sales order | 2 | merged (#12) |
| 11 | Sales order list | 2 | merged (#13) |
| 12 | Cancel a draft sales order | 2 | not started (no `/orders/{id}/cancel` route on `main`) |
| 13 | Stock in | 1 | not started (`routers/stock.py` is an empty router, and `StockInPage` is a placeholder) |
| 14 | Confirm sales order to invoice | 2 | merged (#14) |
| 15 | Invoice list and detail | 2 | merged (#15) |
| 16 | Accounting screen with receivables | 3 → **2** | merged (#16) |
| 17 | Record a payment | 3 → **2** | merged (#17) |
| 18 | Dashboard | 1 | not started (`routers/dashboard.py` is an empty router, and `DashboardPage` is a placeholder) |
| 19 | Café Lune end-to-end | 3 | not started (blocked by 03 and 18) |
| 20 | Bonus: purchase orders | 1 | not started (`routers/purchasing.py` is an empty router) |
| 21 | Bonus: receive a purchase order | 1 | not started (blocked by 20) |
| 22 | Bonus: invoice PDF | 2 | not started (no `/invoices/{id}/pdf` route) |
| 23 | Auth hardening (review follow-ups from 02) | 3 | merged (#3) |

## 3. Tests

`uv run pytest` in the Part 3 copy on `main` (`175f118`): **153 passed, 0 failed**, 5 warnings (all deprecation warnings from the `starlette` and `supabase` libraries), in 2 min 21 s.

This run reset the shared Supabase project's data (orders, invoices, payments and stock movements made in the app are gone).

## 4. Database (one Supabase project, used by the app and by the tests)

| SQL | Run in Supabase? | Evidence |
| --- | --- | --- |
| `docs/schema.sql`: tables, `stock_on_hand` view, `next_doc_number`, `confirm_order`, `record_payment`, `receive_po`, `dashboard_numbers`, `reset_demo_data` | yes | `plan.md` says it was "already run in the project"; the tests call `reset_demo_data`, `confirm_order` and `record_payment` and pass |
| `docs/seed.sql` (sample data) | yes | same `plan.md` statement; tests rely on the seeded products and customers |
| `docs/demo_users.sql` (demo logins) | yes | same `plan.md` statement; `client_as(role)` loads demo users from the `users` table |
| `reset_demo_data` fix (`... where not active`) | yes | PR #1: "already live in Supabase" |
| `create_order` (appended by Part 2) | yes | commit `987d9a1` and PR #12: "already run in the SQL Editor" |

Since `create_order` (`987d9a1`), nothing has been added to `docs/schema.sql`,
`seed.sql` or `demo_users.sql`, so no SQL is waiting to be run. `receive_po`
(for the bonus) and `dashboard_numbers` (for 18) are already in the original
schema.

Not verified here: the project's name. The repo only records its URL, not its name.

## 5. Deploy

**Backend (Render):** https://siam-bean-erp.onrender.com
- `GET /health` returns `200 {"status":"ok"}` (checked).
- The live route list matches `main`, including `/orders/{id}/confirm`, `/accounting/receivables` and `/invoices/{id}/payments`, so Render is running the latest code.
- Free instance: it sleeps after about 15 minutes idle, and the first request can take up to a minute.

**Frontend (Cloudflare Pages):** https://siam-bean-erp.pages.dev is **live, but its API calls don't work yet** (CORS).
- It serves our `Siam Bean ERP` build, and deep links work (`/products` returns 200).
- The live bundle contains the Render API URL and the Supabase URL and publishable key, and **no** secret key (checked).

**Blocking issue:** Render's `FRONTEND_ORIGIN` does not match the Pages URL.
A CORS preflight from `https://siam-bean-erp.pages.dev` gets `400`; only
`http://localhost:5175` gets `200`. So on the live site, every API call
(starting with `/me` after login) is blocked by the browser. Nobody has done a
live login yet.

Environment variables (names only):

| Where | Variables | How we know |
| --- | --- | --- |
| Render (backend) | `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `FRONTEND_ORIGIN` | Set during step 1. `FRONTEND_ORIGIN` currently equals `http://localhost:5175` (from the preflight test above). The two Supabase variables are **unverified**: `/health` does not touch the database, and no logged-in call has been made live. |
| Cloudflare Pages (frontend, build time) | `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_API_URL` | Their values appear in the live bundle. |
| Local: `backend/.env`, `backend/.env.test`, `frontend/.env` | as listed in `plan.md` | files exist in each copy and are gitignored |

Settings used:
- Render: root directory `backend`. Build `pip install uv && uv sync --frozen --no-dev`. Start `uv run --no-dev uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Health check `/health`. Auto-deploy on commit to `main`. Python 3.12 comes from `backend/.python-version`.
- Cloudflare: a **Pages** project, not Workers (the dashboard pushes Workers first; the Pages link is at the bottom of "Create application"). Root directory `frontend`, build `npm run build`, output `dist`, production branch `main`. Node 22 comes from `frontend/.node-version`.

## 6. Scenario coverage (`docs/scenario.md`)

User stories:

| Story | Status | Tickets |
| --- | --- | --- |
| US-1 Sales order → invoice (150 kg left, `INV-0001` 9,630; "Not enough stock for ARB-1KG") | done in code and API tests; not yet shown on the live URL | 10, 14, 15 (live proof: 19) |
| US-2 Low stock (badge + dashboard count) | partly: the badge works; the dashboard low-stock count does not exist yet | 04 done; 18 not started |
| US-3 Roles (Sales gets 403 and the access-denied page on Accounting; Warehouse gets 403 on confirm; Admin loads) | done (tests for both 403 cases; access-denied page and role menu exist) | 02, 23, 14, 16 (live proof: 19) |
| US-4 Payment (invoice becomes Paid; dashboard receivables drop by 9,630) | partly: payment and the Paid status work; the dashboard part does not exist yet | 17 done; 18 not started |
| US-5 Search (200 customers, at most 20 per page) | done (a test seeds 200 customers) | 07 |

Minimum requirements ("In scope"):

| Requirement | Status | Tickets |
| --- | --- | --- |
| Login with roles | done | 02, 23 |
| Products and customers: create, list, edit, deactivate | done | 04–09 |
| Stock: stock-in form | **not done** | 13 |
| Stock: stock goes down when an order is confirmed | done | 14 |
| Stock: low-stock alert | partly (product list yes, dashboard no) | 04, 18 |
| Sales order → invoice with 7% VAT | done | 10, 14, 15 |
| Record a payment against an invoice | done | 16, 17 |
| Dashboard with at least 3 live numbers | **not done** | 18 |
| Deployed with a public URL | partly (both live; CORS blocks the app) | 03 |

Success criteria: the Café Lune flow on the live URL (19) and the live check that Warehouse cannot confirm (19) are both still to do.

## 7. Open questions, decisions not yet in `plan.md`, risks

Decisions made today that are not yet written in `docs/plan.md`:
1. **Part 2 took over tickets 16 and 17**, so `app/routers/accounting.py`, `POST /invoices/{id}/payments` and the Accounting page now belong to Part 2. The ownership table still says Part 3.
2. **Workflow:** every change went through a feature branch, a PR and a merge (17 PRs). `plan.md` "Git" still says "commit straight to `main`".
3. The deploy settings in section 5 (Render commands, Pages rather than Workers, the `.python-version` and `.node-version` pins).
4. The live URLs. Ticket 03 requires them in `plan.md`.

Open questions:
- Should `FRONTEND_ORIGIN` accept more than one origin, for example local dev plus Pages, or Pages preview URLs (`<hash>.siam-bean-erp.pages.dev`)? Today it accepts exactly one origin.
- Do demo passwords go in the README (the template has a "Demo accounts" section) or are they shared another way?

Known bugs and risks:
- **The live site can't call the API until `FRONTEND_ORIGIN` is fixed** (section 5).
- The app and the tests share one Supabase project. `uv run pytest` wipes all app data, so never run tests during the demo.
- Render's free tier sleeps. Open `/health` a minute before the demo.
- The ticket files' `Status:` lines are stale (all `ready-for-agent`).
- Part 1's copy is 14 commits behind `main`.

## 8. Next steps

**Part 3** (in order):
1. Finish **03**:
   - On Render → Environment, set `FRONTEND_ORIGIN` to `https://siam-bean-erp.pages.dev` (no trailing slash), then save and redeploy.
   - Log in on the live URL as each demo user and check their menu: admin `punji@gmail.com`, sales `ana@gmail.com` and `bogie@gmail.com`, warehouse `gap@gmail.com`, accountant `jump@gmail.com`.
   - Write both live URLs into `docs/plan.md`.
2. Update `docs/plan.md` with the decisions in section 7 (ownership of 16 and 17, PR workflow, deploy settings). Update the `Status:` lines in the ticket files.
3. **19** Café Lune end-to-end, once Part 1 has merged 18: one API test first, then the same flow by hand on the live URL after `reset_demo_data`. File any mismatch as a new ticket for the owning Part.
4. **README:** create `README.md` from `docs/README-template.md`, which already has an ER diagram (mermaid). Fill in the live URLs, demo accounts (emails and roles), user stories, bonus, "Who did what" and setup.
5. **Final deploy check**, after all merges: Render and Pages are both on the latest `main` commit, `/health` returns 200, and every demo user can log in.
6. **Demo day:** don't run tests. Run `select reset_demo_data('yes-reset');` once in the Supabase SQL Editor right before the demo, then warm up Render by opening `/health`.

**Part 1** (in order):
1. `git switch main && git pull` (the copy is 14 commits behind), then delete the merged local branches.
2. **18 Dashboard.** This is a minimum requirement and it blocks 19 and finishes US-2 and US-4. `dashboard_numbers` already exists in the database.
3. **13 Stock in.** This is a minimum requirement.
4. Bonus: **20** purchase orders, then **21** receive a purchase order (`receive_po` already exists).

**Part 2** (in order):
1. **12** Cancel a draft sales order.
2. Bonus: **22** invoice PDF.
3. Be available for fixes that 19 turns up in orders, invoices or accounting (now Part 2's).

Demo logins (no passwords here): `punji@gmail.com` admin, `ana@gmail.com` sales,
`bogie@gmail.com` sales, `gap@gmail.com` warehouse, `jump@gmail.com` accountant.
