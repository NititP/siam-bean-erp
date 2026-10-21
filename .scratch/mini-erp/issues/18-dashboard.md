# 18: Part 1: Dashboard

Part: 1
Status: resolved

**What to build:** Every staff member opens the dashboard and sees five live numbers: sales today (incl. VAT), low-stock count, open invoices count, open receivables and stock value.

**Blocked by:** 02 (Part 3: Login, current user and roles); 06 (Part 1: Deactivate and reactivate products)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `GET /dashboard` returns the five numbers from `dashboard_numbers` for all four roles
- [ ] At the starting state the low-stock count is 1 (ROB-1KG) (US-2) and stock value is the sum of on hand x cost for active products
- [ ] A deactivated low-stock product is not counted in the low-stock count or stock value
- [ ] Dashboard page shows five tiles; the first is labelled "Sales today (incl. VAT)"; money in THB format
- [ ] It is the landing page after login
