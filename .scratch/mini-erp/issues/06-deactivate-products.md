# 06: Part 1: Deactivate and reactivate products

Part: 1
Status: ready-for-agent

**What to build:** The Admin deactivates a product so it can no longer be sold but is kept for old documents, and can reactivate it. The product list has a "Show inactive" toggle.

**Blocked by:** 05 (Part 1: Create and edit products)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `POST /products/{id}/deactivate` hides the product from the default list
- [ ] `PATCH /products/{id}` with `active: true` brings it back
- [ ] Other roles get 403 on deactivate
- [ ] "Show inactive" toggle on the Products page shows inactive products, marked as inactive
