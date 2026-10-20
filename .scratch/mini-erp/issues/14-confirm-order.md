# 14: Part 2: Confirm sales order to invoice

Part: 2
Status: ready-for-agent

**What to build:** A Sales user confirms a draft. Stock goes out and an invoice is issued with 7% VAT, all at once or not at all. Too little stock shows a clear error and nothing changes.

**Blocked by:** 10 (Part 2: Create a draft sales order)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] Given 170 kg ARB-1KG, confirming Café Lune's draft of 20 kg at 450 THB leaves 150 kg on hand and returns `INV-0001` with subtotal 9,000.00, VAT 630.00, total 9,630.00 (US-1)
- [ ] Confirming more than on hand returns 409 "Not enough stock for ARB-1KG"; stock, order status and invoice numbers are unchanged (US-1)
- [ ] Warehouse calling confirm directly gets 403 (US-3); Accountant gets 403
- [ ] Confirming a confirmed or cancelled order returns 422; an unknown order returns 404
- [ ] The invoice's due date is the issue date plus the customer's payment terms
- [ ] Changing the product's price after the order is created does not change the invoice
- [ ] Order detail has a Confirm button on drafts; shows the API's `detail` on error and the invoice number on success
