# Siam Bean Mini ERP: team plan and decisions

This file is for the team and for every coding agent. The business brief is
`docs/scenario.md`; it always wins. This file records how we build it.

## Team and ownership

Everything runs on one Windows PC with three copies of the repo, one per part,
so three agent sessions can work at the same time without touching each other.

| Part | Folder | Ports (API / web) | Module | Backend files | Frontend pages |
| --- | --- | --- | --- | --- | --- |
| 1 | `siam-bean-erp-1` | 8000 / 5173 | Products, customers, stock, dashboard, purchasing (bonus) | `app/routers/products.py`, `customers.py`, `stock.py`, `dashboard.py`, `purchasing.py` | Products, Customers, Stock in, Dashboard, Purchase orders |
| 2 | `siam-bean-erp-2` | 8001 / 5174 | Sales orders, confirm to invoice, invoices, PDF (bonus) | `app/routers/orders.py`, `invoices.py` | Orders, New order, Order detail, Invoices, Invoice detail |
| 3 | `siam-bean-erp` | 8002 / 5175 | Foundation, login and roles, payments, deploy | `app/main.py`, `app/auth.py`, `app/db.py`, `app/routers/me.py`, `app/routers/accounting.py`, `tests/conftest.py` | Login, layout and menu, access denied, Accounting |

Only edit your own files. If you need a change in someone else's file, ask them.

## Stack

- Database and login: Supabase (Postgres + Auth). Two projects: **live** (the
  deployed app) and **test** (only `uv run pytest` uses it).
- Backend: Python FastAPI, managed with `uv`, in `backend/`. Talks to Supabase
  with the **secret key** using the `supabase` Python package.
- Frontend: React + TypeScript + Vite in `frontend/`. Uses Supabase only to
  log in (publishable key), then calls our FastAPI with the user's token.
- Deploy: backend on Render, frontend on Cloudflare Pages.

## Database

- The full schema is `docs/schema.sql`, sample data `docs/seed.sql`, demo
  logins `docs/demo_users.sql`. Already run in both projects.
- Business logic that must be all-or-nothing lives in Postgres functions,
  called from FastAPI with `rpc`:
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
- Stock on hand is the `stock_on_hand` view (sum of movements). Never store
  or type a stock number.
- Order lines copy `unit_price` and `unit_cost` from the product when created.

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
| `POST /products`, `PATCH /products/{id}`, `POST /products/{id}/deactivate` | admin | |
| `GET /customers?q=&page=` | admin, sales, accountant | name contains q (case-insensitive), 20 per page, returns `total` |
| `POST /customers`, `PATCH /customers/{id}`, `POST /customers/{id}/deactivate` | admin, sales | tax ID required |
| `POST /stock/in` | admin, warehouse | `{product_id, quantity, note}`, quantity > 0 |
| `GET /orders`, `GET /orders/{id}`, `POST /orders` | admin, sales | create = draft with lines `{customer_id, lines:[{product_id, quantity}]}` |
| `POST /orders/{id}/confirm` | admin, sales | calls `confirm_order`; 409 on not enough stock |
| `GET /invoices`, `GET /invoices/{id}` | admin, sales, accountant | |
| `GET /invoices/{id}/pdf` | admin, sales, accountant | bonus |
| `GET /accounting/receivables` | admin, accountant | open invoices with outstanding amount |
| `POST /invoices/{id}/payments` | admin, accountant | `{amount}`; calls `record_payment` |
| `GET /dashboard` | all | calls `dashboard_numbers` |
| `GET /suppliers`, `GET/POST /purchase-orders`, `POST /purchase-orders/{id}/receive` | admin, warehouse | bonus |

Errors: `{"detail": "<message that says what to fix>"}`. 401 not logged in,
403 wrong role, 404 not found, 409 not enough stock, 422 bad input.

## How login works

1. Frontend logs in with Supabase Auth (email + password).
2. Frontend sends the access token to FastAPI in the `Authorization` header.
3. `app/auth.py` checks the token with `supabase.auth.get_user(token)`, then
   loads the row from `users` to get `role` and `company_id`.
4. A dependency `require_roles("admin", "sales")` returns 403 for anyone else.

## Tests

- `uv run pytest` from `backend/`. Tests use FastAPI's `TestClient`.
- Tests read `backend/.env.test` (the **test** Supabase project). A guard in
  `tests/conftest.py` refuses to run if the URL is the live project.
- Before each test, call `reset_demo_data('yes-reset')`.
- Tests override only the token check: a fixture `client_as(role)` logs the
  request in as the matching demo user from the `users` table.
- Write the failing test first, run it, see red, then implement. Never edit a
  test to make it pass.

## Frontend rules

- Money: `9,630.00 THB` everywhere (one shared `formatTHB` helper).
- Every list shows a message when it is empty.
- Every error shows the API's `detail` text.
- Menu shows only what the role may use; hidden buttons are not security,
  the API still checks.
- Works on a phone (single column under 640 px).

## Environment variables (never commit real values)

`backend/.env` (live) and `backend/.env.test` (test project):
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

## Out of scope

Quotations, delivery notes, multiple companies, HR, withholding tax,
multiple warehouses, LINE. Bonus only: purchasing and PDF invoice.
