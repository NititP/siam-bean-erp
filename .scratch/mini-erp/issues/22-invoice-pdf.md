# 22: Part 2: Bonus: invoice PDF

Part: 2
Status: ready-for-agent

**What to build:** Sales, the Accountant and the Admin download an invoice as a PDF with the company and customer tax IDs, lines, subtotal, VAT and total.

**Blocked by:** 15 (Part 2: Invoice list and detail)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `GET /invoices/{id}/pdf` returns a PDF for Admin, Sales and Accountant; Warehouse gets 403
- [ ] The PDF shows invoice number, dates, company and customer names and tax IDs, lines, subtotal, VAT 7% and total, matching the invoice detail
- [ ] Invoice detail page has a Download PDF button
