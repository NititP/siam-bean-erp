# 08: Part 1: Create and edit customers

Part: 1
Status: ready-for-agent

**What to build:** Sales and the Admin create customers and edit their details and payment terms. A tax ID is required.

**Blocked by:** 07 (Part 1: Customer list with search and paging)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] Admin and Sales can create a customer (name, tax ID, payment terms in days)
- [ ] A missing or blank tax ID or name returns 422 with a clear message
- [ ] Negative payment terms return 422
- [ ] Admin and Sales can edit a customer
- [ ] Accountant and Warehouse get 403 on create and edit
- [ ] Customers page has create and edit forms for Admin and Sales only
