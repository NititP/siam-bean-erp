# 15: Part 2: Invoice list and detail

Part: 2
Status: resolved

**What to build:** Sales, the Accountant and the Admin see every invoice with its paid and outstanding amounts, and open one to see its lines, payments and totals.

**Blocked by:** 14 (Part 2: Confirm sales order to invoice)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `GET /invoices` and `GET /invoices/{id}` return the shared invoice shape: number, order number, customer name, issue date, due date, subtotal, vat, total, status, paid, outstanding
- [ ] Detail also returns lines and payments (amount, paid at)
- [ ] After US-1, `INV-0001` shows total 9,630.00, paid 0.00, outstanding 9,630.00, status open
- [ ] Warehouse gets 403
- [ ] Invoices page and Invoice detail page; no "Record payment" button; a message when the list is empty
