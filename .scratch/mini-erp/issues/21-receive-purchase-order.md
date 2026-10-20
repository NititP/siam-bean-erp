# 21: Part 1: Bonus: receive a purchase order

Part: 1
Status: ready-for-agent

**What to build:** Admin or Warehouse receives a draft purchase order and its quantities are added to stock on hand, once.

**Blocked by:** 20 (Part 1: Bonus: purchase orders)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `POST /purchase-orders/{id}/receive` calls `receive_po`; each line's product `on_hand` rises by its quantity
- [ ] Receiving again returns 422 "Purchase order PO-0001 was already received"; stock is unchanged
- [ ] Sales and Accountant get 403
- [ ] Receive button on draft purchase orders
