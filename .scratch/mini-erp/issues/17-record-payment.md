# 17: Part 2: Record a payment

Part: 2
Status: resolved

**What to build:** The Accountant records a payment against an open invoice. A full payment marks it paid; a partial payment lowers what is outstanding.

**Blocked by:** 16 (Part 2: Accounting screen with receivables)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `POST /invoices/{id}/payments` with the full 9,630.00 on `INV-0001` makes its status paid and outstanding 0.00 (US-4)
- [ ] A partial payment keeps the invoice open and lowers outstanding
- [ ] An amount of 0 or below, or above outstanding, returns 422 with the allowed range
- [ ] Paying a paid invoice returns 422; an unknown invoice returns 404
- [ ] Sales and Warehouse get 403
- [ ] Accounting page has a record-payment form per invoice; the list refreshes after saving
