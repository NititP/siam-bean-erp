# 11: Part 2: Sales order list

Part: 2
Status: ready-for-agent

**What to build:** Sales and the Admin see all sales orders with number, customer, date, status and total, and open any of them.

**Blocked by:** 10 (Part 2: Create a draft sales order)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `GET /orders` returns orders newest first with number, customer name, order date, status and total of lines
- [ ] Warehouse and Accountant get 403
- [ ] Orders page lists them, links to order detail, and shows a message when empty
