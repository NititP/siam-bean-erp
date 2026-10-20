# 12: Part 2: Cancel a draft sales order

Part: 2
Status: ready-for-agent

**What to build:** A Sales user cancels a draft they made by mistake. Only drafts can be cancelled.

**Blocked by:** 10 (Part 2: Create a draft sales order)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `POST /orders/{id}/cancel` sets a draft to `cancelled`
- [ ] Cancelling a confirmed or cancelled order returns 422 "Only draft orders can be cancelled"
- [ ] An unknown order returns 404; Warehouse and Accountant get 403
- [ ] Order detail has a Cancel button on drafts only
