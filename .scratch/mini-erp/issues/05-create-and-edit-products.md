# 05: Part 1: Create and edit products

Part: 1
Status: resolved

**What to build:** The Admin creates products and edits them, including the price. Bad input is rejected with a message that says what to fix. Other roles are refused.

**Blocked by:** 04 (Part 1: Product list with stock on hand and low-stock badge)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] Admin can create a product (SKU, name, unit, cost, price, reorder level) and it appears in the list
- [ ] Duplicate SKU returns 422 naming the SKU
- [ ] Negative price or cost, or an empty SKU or name, returns 422
- [ ] Admin can edit a product, including its price
- [ ] Sales, Warehouse and Accountant get 403 on create and edit
- [ ] Products page has create and edit forms for the Admin only, showing the API's `detail` on error
