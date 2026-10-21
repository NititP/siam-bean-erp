# 10: Part 2: Create a draft sales order

Part: 2
Status: resolved

**What to build:** A Sales user picks a customer, adds order lines (product and quantity) and saves a draft sales order. It gets the next `SO-` number, and every line copies the product's current price and cost. Creating the order is all or nothing. The New order page shows stock on hand and the low-stock badge for each product, and warns (without blocking) when a line asks for more than is on hand. After saving, the user lands on the order detail.

**Blocked by:** 04 (Part 1: Product list with stock on hand and low-stock badge); 07 (Part 1: Customer list with search and paging)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] New Postgres function `create_order` appended to `docs/schema.sql` and run once in the SQL Editor; no existing object changed
- [ ] `POST /orders` creates draft `SO-0001` with lines whose `unit_price` and `unit_cost` match the product
- [ ] An inactive customer or product returns 422 naming it; an unknown one returns 404; no order or number is left behind
- [ ] A quantity of 0 or below, or no lines, returns 422
- [ ] `GET /orders/{id}` returns the order with its lines
- [ ] Warehouse and Accountant get 403
- [ ] New order page: customer and product pickers show only active records; the product picker shows stock on hand and the low-stock badge; a line over stock on hand shows "Only N <unit> on hand" but can be saved
- [ ] Order detail page shows number, customer, status, lines and, for drafts, stock on hand per line
