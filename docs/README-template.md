# Siam Bean Mini ERP

A small cloud ERP for Siam Bean Co., a Bangkok coffee-bean distributor:
sales orders, stock, invoices with 7% VAT, payments and a live dashboard,
in one database with role-based login.

**Live app:** https://YOUR-APP.pages.dev
**API:** https://YOUR-API.onrender.com/health

## Demo accounts

| Role | Email | Password |
| --- | --- | --- |
| Admin (Khun Somchai) | somchai@example.com | (demo password) |
| Sales (Nok) | nok@example.com | (demo password) |
| Sales (Ploy) | ploy@example.com | (demo password) |
| Warehouse (Lek) | lek@example.com | (demo password) |
| Accountant (Fon) | fon@example.com | (demo password) |

## User stories

| Story | Status |
| --- | --- |
| US-1 Sales order to invoice | Done / Not done |
| US-2 Low stock | Done / Not done |
| US-3 Roles | Done / Not done |
| US-4 Payment | Done / Not done |
| US-5 Customer search | Done / Not done |

## Bonus

| Feature | Status | How to see it |
| --- | --- | --- |
| Purchasing: PO to goods receipt to stock in | Done / Not done | Log in as Lek, Purchase orders |
| PDF invoice | Done / Not done | Any invoice, Download PDF |

## Who did what

| Member | Student ID | Module | GitHub |
| --- | --- | --- | --- |
| | | Foundation, login and roles, payments, dashboard, deploy | |
| | | Products, customers, stock, purchasing | |
| | | Sales orders, confirm to invoice, invoices, PDF | |
| | | Presentation | |
| | | Presentation | |

## Stack

Supabase (Postgres + Auth), FastAPI with uv (Render), React + TypeScript +
Vite (Cloudflare Pages). Business rules that must be all-or-nothing run as
Postgres functions (`docs/schema.sql`), and FastAPI checks the role on every
endpoint (wrong role = 403).

## Setup

1. Create a Supabase project. In the SQL Editor run `docs/schema.sql`, then
   `docs/seed.sql`. Create the demo users under Authentication, then run
   `docs/demo_users.sql`.
2. Backend:
   ```bash
   cd backend
   cp .env.example .env      # fill in SUPABASE_URL and SUPABASE_SECRET_KEY
   uv sync
   uv run uvicorn app.main:app --reload
   ```
3. Frontend:
   ```bash
   cd frontend
   cp .env.example .env      # fill in the three VITE_ values
   npm install
   npm run dev
   ```
4. Tests (use a separate test Supabase project in `backend/.env.test`):
   ```bash
   cd backend
   uv run pytest
   ```

## Database schema

```mermaid
erDiagram
  companies ||--o{ users : employs
  companies ||--o{ customers : has
  companies ||--o{ suppliers : has
  companies ||--o{ products : sells
  products ||--o{ stock_movements : "moves"
  customers ||--o{ sales_orders : places
  sales_orders ||--|{ order_items : contains
  products ||--o{ order_items : "ordered as"
  sales_orders ||--o| invoices : "billed by"
  customers ||--o{ invoices : owes
  invoices ||--o{ payments : "paid by"
  suppliers ||--o{ purchase_orders : supplies
  purchase_orders ||--|{ po_items : contains
  products ||--o{ po_items : "bought as"
  companies ||--o{ doc_counters : numbers

  companies { bigint id PK
    text name
    text tax_id }
  users { uuid id PK
    bigint company_id FK
    text email
    text full_name
    text role }
  customers { bigint id PK
    bigint company_id FK
    text name
    text tax_id
    int payment_terms_days
    bool active }
  suppliers { bigint id PK
    bigint company_id FK
    text name
    text location
    int lead_time_days
    int payment_terms_days }
  products { bigint id PK
    bigint company_id FK
    text sku
    text name
    text unit
    numeric cost
    numeric price
    int reorder_level
    bool active }
  stock_movements { bigint id PK
    bigint product_id FK
    int quantity
    text ref_doc
    uuid created_by FK
    timestamptz created_at }
  doc_counters { bigint company_id PK
    text doc_type PK
    int last_no }
  sales_orders { bigint id PK
    text number
    bigint customer_id FK
    text status
    date order_date
    uuid created_by FK }
  order_items { bigint id PK
    bigint order_id FK
    bigint product_id FK
    int quantity
    numeric unit_price
    numeric unit_cost }
  invoices { bigint id PK
    text number
    bigint order_id FK
    bigint customer_id FK
    numeric subtotal
    numeric vat
    numeric total
    text status
    date due_date }
  payments { bigint id PK
    bigint invoice_id FK
    numeric amount
    timestamptz paid_at }
  purchase_orders { bigint id PK
    text number
    bigint supplier_id FK
    text status
    timestamptz received_at }
  po_items { bigint id PK
    bigint po_id FK
    bigint product_id FK
    int quantity
    numeric unit_cost }
```

Stock on hand is the `stock_on_hand` view: the sum of `stock_movements` per
product. Nobody types a stock number.

## Docs

`docs/scenario.md` (brief), `docs/plan.md` (decisions), `GLOSSARY.md`,
spec and tickets in `.scratch/`.
