# 20: Part 1: Bonus: purchase orders

Part: 1
Status: resolved

**What to build:** Admin and Warehouse see suppliers and create a draft purchase order with lines (product, quantity, unit cost), numbered `PO-0001`.

**Blocked by:** 04 (Part 1: Product list with stock on hand and low-stock badge)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `GET /suppliers` returns active suppliers
- [ ] `POST /purchase-orders` creates draft `PO-0001` with its lines; `GET /purchase-orders` lists them
- [ ] A quantity of 0 or below or a negative cost returns 422
- [ ] Sales and Accountant get 403
- [ ] Purchase orders page: list and create form
