# 16: Part 2: Accounting screen with receivables

Part: 2
Status: resolved

**What to build:** The Accountant and the Admin open the Accounting screen and see every open invoice with what is still owed. Sales cannot.

**Blocked by:** 14 (Part 2: Confirm sales order to invoice)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `GET /accounting/receivables` returns open invoices in the shared invoice shape, with `outstanding`
- [ ] Sales gets 403 from the API and the access-denied page in the browser (US-3)
- [ ] Admin and Accountant get 200 and the page loads (US-3)
- [ ] Accounting page lists receivables with money in THB format and a message when nothing is owed
