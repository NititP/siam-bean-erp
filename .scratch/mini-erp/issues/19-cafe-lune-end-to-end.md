# 19: Part 3: Café Lune end-to-end

Part: 3
Status: ready-for-agent

**What to build:** The scenario's success criterion, proven twice: once as an API test and once by hand on the live URL. Café Lune's 20 kg order goes from order to stock to invoice to payment to dashboard, and the numbers agree on every screen.

**Blocked by:** 03 (Part 3: Deploy live); 15 (Part 2: Invoice list and detail); 17 (Part 2: Record a payment); 18 (Part 1: Dashboard)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [x] One API test: create and confirm Café Lune's 20 kg ARB-1KG order; check 150 kg on hand, `INV-0001` 9,630.00, dashboard sales today 9,630.00 and open receivables 9,630.00; record the full payment; the invoice is paid and open receivables drop by 9,630.00 (US-1, US-4)
- [ ] The same flow done by hand on the live URL after `reset_demo_data`, with the same numbers on Order, Invoice, Accounting and Dashboard
- [ ] On the live URL a Warehouse user cannot confirm an order, even by calling the API
- [ ] Any mismatch is filed as a new ticket for the owning Part
