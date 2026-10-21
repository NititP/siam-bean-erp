# 13: Part 2: Stock in

Part: 2
Status: resolved

**What to build:** A Warehouse user records goods arriving: product, quantity and an optional note. Stock on hand goes up immediately.

**Blocked by:** 04 (Part 1: Product list with stock on hand and low-stock badge)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `POST /stock/in` adds one positive stock movement; the product's `on_hand` rises by the quantity
- [ ] The movement's reference is `STOCK-IN`, or `STOCK-IN: <note>` when a note is given
- [ ] A quantity of 0 or below returns 422; an unknown product returns 404
- [ ] Sales and Accountant get 403
- [ ] Stock in page with product picker, quantity and note; shows the new stock on hand after saving
