# 04: Part 1: Product list with stock on hand and low-stock badge

Part: 1
Status: ready-for-agent

**What to build:** Every staff member sees the product list: SKU, name, unit, price, stock on hand and a low-stock badge for products below their reorder level. Inactive products are hidden unless asked for.

**Blocked by:** 02 (Part 3: Login, current user and roles)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `GET /products` returns each active product with `on_hand` and `low_stock`, for all four roles
- [ ] At the starting state ROB-1KG has 35 on hand and is low stock; ARB-1KG has 170 and is not (US-2)
- [ ] `?include_inactive=true` also returns inactive products
- [ ] Products page shows the list with money in THB format and the low-stock badge
- [ ] An empty list shows a message
