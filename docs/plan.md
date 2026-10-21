# Siam Bean Mini ERP: team plan and decisions

This file is for the team and for every coding agent. The business brief is
`docs/scenario.md`; it always wins. This file records how we build it.

## Team and ownership

Everything runs on one Windows PC with three copies of the repo, one per part,
so three agent sessions can work at the same time without touching each other.

| Part | Folder | Ports (API / web) | Module | Backend files | Frontend pages |
| --- | --- | --- | --- | --- | --- |
| 1 | `siam-bean-erp-1` | 8000 / 5173 | Products, customers, dashboard, purchasing (bonus) | `app/routers/products.py`, `customers.py`, `dashboard.py`, `purchasing.py` | Products, Customers, Dashboard, Purchase orders |
| 2 | `siam-bean-erp-2` | 8001 / 5174 | Sales orders, confirm to invoice, invoices, payments, stock in, PDF (bonus) | `app/routers/orders.py`, `invoices.py`, `accounting.py` (includes `POST /invoices/{id}/payments`), `stock.py`, the `create_order` function in `docs/schema.sql` | Orders, New order, Order detail, Invoices, Invoice detail, Accounting, Stock in |
| 3 | `siam-bean-erp` | 8002 / 5175 | Foundation, login and roles, deploy | `app/main.py`, `app/auth.py`, `app/db.py`, `app/routers/me.py`, `tests/conftest.py`; frontend shared files: routes (`App.tsx`), menu, `api.ts`, `formatTHB`, empty-list and error components | Login, layout and menu, access denied |

Only edit your own files. If you need a change in someone else's file, ask them.

Part 2 took over tickets 16 and 17 (Accounting screen, record payment) from
Part 3, and ticket 13 (stock in) from Part 1, so `accounting.py`, payments,
`stock.py` and the Accounting and Stock in pages are Part 2's.

## Start order

1. Part 3 builds the skeleton and pushes it before Parts 1 and 2 start:
   - Backend: `main.py` already includes every router (`me`, `products`,
     `customers`, `stock`, `dashboard`, `purchasing`, `orders`, `invoices`,
     `accounting`), each starting as an empty `APIRouter()` in its owner's
     file; `auth.py` with `require_roles`; `db.py`; `tests/conftest.py` with
     the file lock and `client_as(role)`; passing tests for `/health` and `/me`.
   - Frontend: a route for every page, pointing at a placeholder component in
     its owner's file; menu filtered by role; `api.ts` (adds the token, shows
     `detail`); `formatTHB`; shared empty-list and error components.
2. Parts 1 and 2 pull the skeleton, then edit only their own router, page and
   test files. They never touch routing or `main.py`.
3. After the skeleton, shared files belong to Part 3. Ask for changes.
4. Each part's tests live in their own files (`tests/test_products.py`,
   `tests/test_orders.py`, ...). No shared test files.

## Git

- One remote, `NititP/siam-bean-erp`. Every change goes through a feature
  branch (`feature/<ticket-slug>`), a PR (`gh pr create`) and a merge into
  `main`. Never commit straight to `main`. `main` deploys, so whatever is
  merged goes live.
- Before opening a PR: `uv run pytest` passes (and `npm run build` for
  frontend changes), and the branch is up to date with `main`
  (`git pull --rebase origin main`). Delete the branch after the merge.
- A rebase conflict means two parts edited the same file. Stop and ask its
  owner; don't resolve it by guessing.
- Tickets in `.scratch/` travel the same way. Commit them promptly.

## Stack

- Database and login: Supabase (Postgres + Auth). **One project**, used by
  both the deployed app and `uv run pytest`. The tests reset its data, so
  running them wipes every order, invoice, payment and stock movement made in
  the app.
- Backend: Python FastAPI, managed with `uv`, in `backend/`. Talks to Supabase
  with the **secret key** using the `supabase` Python package.
- Frontend: React + TypeScript + Vite in `frontend/`. Uses Supabase only to
  log in (publishable key), then calls our FastAPI with the user's token.
- Deploy: backend on Render, frontend on Cloudflare Pages (see Deploy).

## Database

- The full schema is `docs/schema.sql`, sample data `docs/seed.sql`, demo
  logins `docs/demo_users.sql`. Already run in the project.
- Business logic that must be all-or-nothing lives in Postgres functions,
  called from FastAPI with `rpc`:
  - `create_order(company_id, customer_id, user_id, lines jsonb)` - checks
    the customer and products exist and are active, takes the next SO number,
    inserts the draft order and its lines with `unit_price` and `unit_cost`
    copied from the product, all in one transaction. Raises `SB404` not found,
    `SB422` bad input. Added by Part 2 (append to `docs/schema.sql`, then run it
    once in the SQL Editor; never change existing objects).
  - `confirm_order(order_id, user_id)` - stock check, stock out, INV number,
    subtotal, 7% VAT, total, status confirmed. Raises `SB409` "Not enough
    stock for <SKU>", `SB422` wrong state, `SB404` not found.
  - `record_payment(invoice_id, amount, user_id)` - invoice becomes `paid`
    when payments reach the total.
  - `receive_po(po_id, user_id)` - bonus, adds stock once.
  - `next_doc_number(company_id, 'SO' | 'INV' | 'PO')` - `SO-0001` style.
  - `dashboard_numbers(company_id)` - sales today, low-stock count, open
    invoices count, open receivables, stock value.
  - `reset_demo_data('yes-reset')` - back to the scenario starting state.
    One-off exception to "never change existing objects" (ticket 01): its
    `update suppliers set active = true` had no `WHERE`, which Supabase's API
    refuses ("UPDATE requires a WHERE clause"), so tests could not reset. Now
    `... where not active`, same result. The whole function was re-run once in
    the SQL Editor. Any function called through the API must not run an
    `update` or `delete` without a `WHERE`.
- Stock on hand is the `stock_on_hand` view (sum of movements). Never store
  or type a stock number.
- Order lines copy `unit_price` and `unit_cost` from the product when created.
- Deactivated products and customers: hidden from lists unless
  `?include_inactive=true` (admin screens have a "Show inactive" toggle);
  cannot go on new orders (`create_order` raises 422 "Customer <name> is
  inactive"); drafts made before deactivation can still be confirmed; not
  counted in low-stock count or stock value.

## Roles (checked in FastAPI on every endpoint; wrong role = 403)

| Action | admin | sales | warehouse | accountant |
| --- | --- | --- | --- | --- |
| View products and stock on hand | yes | yes | yes | yes |
| Create, edit, deactivate products (prices) | yes | - | - | - |
| View customers | yes | yes | - | yes |
| Create, edit, deactivate customers | yes | yes | - | - |
| Stock in | yes | - | yes | - |
| Create, view and confirm sales orders | yes | yes | - | - |
| View invoices (list, detail, PDF) | yes | yes | - | yes |
| Accounting screen: receivables, record payment | yes | - | - | yes |
| Purchase orders and receiving (bonus) | yes | - | yes | - |
| Dashboard | yes | yes | yes | yes |

The "Accounting screen" in US-3 is `/accounting`. Sales can view invoices but
gets 403 on `/accounting`.

## API (all JSON, all need `Authorization: Bearer <supabase access token>`)

| Method and path | Who | Notes |
| --- | --- | --- |
| `GET /health` | anyone | no login needed |
| `GET /me` | all | email, full_name, role |
| `GET /products` | all | includes `on_hand`, `low_stock`; `?include_inactive=true` |
| `POST /products`, `PATCH /products/{id}`, `POST /products/{id}/deactivate` | admin | reactivate with `PATCH {"active": true}` |
| `GET /customers?q=&page=` | admin, sales, accountant | name contains q (case-insensitive), 20 per page, returns `total`; `?include_inactive=true` |
| `POST /customers`, `PATCH /customers/{id}`, `POST /customers/{id}/deactivate` | admin, sales | tax ID required; reactivate with `PATCH {"active": true}` |
| `POST /stock/in` | admin, warehouse | `{product_id, quantity, note}`, quantity > 0, note optional; saved as `ref_doc` = `STOCK-IN` or `STOCK-IN: <note>` |
| `GET /orders`, `GET /orders/{id}`, `POST /orders` | admin, sales | create = draft with lines `{customer_id, lines:[{product_id, quantity}]}` |
| `POST /orders/{id}/confirm` | admin, sales | calls `confirm_order`; 409 on not enough stock |
| `POST /orders/{id}/cancel` | admin, sales | drafts only (`update ... where status = 'draft'`); 422 "Only draft orders can be cancelled". No editing drafts: cancel and create a new one |
| `GET /invoices`, `GET /invoices/{id}` | admin, sales, accountant | |
| `GET /invoices/{id}/pdf` | admin, sales, accountant | bonus |
| `GET /accounting/receivables` | admin, accountant | open invoices with outstanding amount |
| `POST /invoices/{id}/payments` | admin, accountant | `{amount}`; calls `record_payment` |
| `GET /dashboard` | all | calls `dashboard_numbers` |
| `GET /suppliers`, `GET/POST /purchase-orders`, `POST /purchase-orders/{id}/receive` | admin, warehouse | bonus |

Invoice shape (same fields in `GET /invoices`, `GET /invoices/{id}` and
`GET /accounting/receivables`, so every screen shows the same numbers):
`number, order_number, customer_name, issue_date, due_date, subtotal, vat,
total, status, paid, outstanding`, where `paid` = sum of payments and
`outstanding = total - paid`. The detail response also has `lines` and
`payments` (`amount, paid_at`). Payments are recorded only on the Accounting
screen; the invoice detail page has no "Record payment" button.

Money in JSON is a number with 2 decimals (`9630.00`). The frontend only
formats it with `formatTHB` and never recalculates VAT or totals.

Errors: `{"detail": "<message that says what to fix>"}`. 401 not logged in,
403 wrong role, 404 not found, 409 not enough stock, 422 bad input, 503
Supabase out of reach (handled once in `app/main.py`).

## How login works

1. Frontend logs in with Supabase Auth (email + password).
2. Frontend sends the access token to FastAPI in the `Authorization` header.
3. `app/auth.py` checks the token with `supabase.auth.get_user(token)`, then
   loads the row from `users` to get `role` and `company_id`.
4. A dependency `require_roles("admin", "sales")` returns 403 for anyone else.
5. `app/main.py` already requires a login for every router, so an endpoint
   with no `require_roles` still answers 401 without a token. Add
   `require_roles(...)` wherever the role table limits who may call it. A test
   checks every endpoint except `/health` answers 401 without a token.

## Tests

- `uv run pytest` from `backend/`. Tests use FastAPI's `TestClient`.
- Tests read `backend/.env.test`, which points to the same Supabase project
  as `backend/.env`. Tests reset that project's data.
- Only one test run at a time across the three repo copies: `tests/conftest.py`
  holds a file lock outside the repos (`%TEMP%\siam-bean-pytest.lock`, using
  the `filelock` package) for the whole run. A second run waits for the first.
- Tests wipe the app's data. Call `reset_demo_data('yes-reset')` once right
  before the demo, and never run tests during the demo.
- Before each test, call `reset_demo_data('yes-reset')`.
- Tests override only the token check: a fixture `client_as(role)` logs the
  request in as the matching demo user from the `users` table.
- Write the failing test first, run it, see red, then implement. Never edit a
  test to make it pass.

## Frontend rules

- Money: `9,630.00 THB` everywhere (one shared `formatTHB` helper).
- New order page (pain point 4): the product picker shows stock on hand and
  the low-stock badge; a line over stock on hand shows a warning ("Only 35 kg
  on hand") but the draft can still be saved; order detail shows on hand for
  each line of a draft. Confirm is the only real check and shows the API's
  "Not enough stock for <SKU>". No new API: use `GET /products`.
- Dashboard tile is labelled "Sales today (incl. VAT)": it is the invoice
  total, so it matches the invoice and open receivables.
- Every list shows a message when it is empty.
- Every error shows the API's `detail` text.
- Menu shows only what the role may use; hidden buttons are not security,
  the API still checks.
- Works on a phone (single column under 640 px).

## Environment variables (never commit real values)

`backend/.env` (the app) and `backend/.env.test` (the tests). Both point to
the same Supabase project, so `SUPABASE_URL` and `SUPABASE_SECRET_KEY` are the
same in both:
```
SUPABASE_URL=
SUPABASE_SECRET_KEY=
FRONTEND_ORIGIN=http://localhost:5173
```
`frontend/.env`:
```
VITE_SUPABASE_URL=
VITE_SUPABASE_PUBLISHABLE_KEY=
VITE_API_URL=http://localhost:8000
```

## Deploy

Both deploy automatically from `main`.

| | Live URL | Settings |
| --- | --- | --- |
| Backend (Render web service) | https://siam-bean-erp.onrender.com | Root directory `backend`. Build `pip install uv && uv sync --frozen --no-dev`. Start `uv run --no-dev uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Health check `/health`. Auto-deploy on commit to `main`. Python 3.12 from `backend/.python-version`. |
| Frontend (Cloudflare **Pages**, not Workers) | https://siam-bean-erp.pages.dev | Root directory `frontend`. Build `npm run build`. Output `dist`. Production branch `main`. Node 22 from `frontend/.node-version`. The Pages link is at the bottom of "Create application"; the dashboard pushes Workers first. |

- Render env vars: `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `FRONTEND_ORIGIN`
  = `https://siam-bean-erp.pages.dev` (exactly one origin, no trailing slash).
- Pages build env vars: `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`,
  `VITE_API_URL` = `https://siam-bean-erp.onrender.com`. Never the secret key.
- Render's free instance sleeps after about 15 minutes idle; the first
  request can take up to a minute. Open `/health` a minute before a demo.

## Out of scope

Quotations, delivery notes, multiple companies, HR, withholding tax,
multiple warehouses, LINE. Bonus only: purchasing and PDF invoice.
Possible bonus: stock adjustments (manual stock out or corrections). The
Warehouse role's "stock out" in the scenario means the stock that leaves
automatically when an order is confirmed.
No user management screen: users and their roles are set in Supabase
(Authentication > Users, then an insert like `docs/demo_users.sql`).
No cancelling confirmed orders or invoices (that needs stock reversal and
credit notes). `invoices.status = 'cancelled'` is never set.
