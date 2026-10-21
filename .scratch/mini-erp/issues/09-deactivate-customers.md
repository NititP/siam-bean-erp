# 09: Part 1: Deactivate and reactivate customers

Part: 1
Status: resolved

**What to build:** Sales and the Admin deactivate a customer so no new orders go to them, and can reactivate them. The customer list has a "Show inactive" toggle.

**Blocked by:** 08 (Part 1: Create and edit customers)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `POST /customers/{id}/deactivate` hides the customer from the default list
- [ ] `PATCH /customers/{id}` with `active: true` brings it back
- [ ] Accountant and Warehouse get 403 on deactivate
- [ ] "Show inactive" toggle on the Customers page
