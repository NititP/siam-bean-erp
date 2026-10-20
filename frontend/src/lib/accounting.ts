import { api } from "./api";
import type { Invoice } from "./invoices";

// Owner: Part 3 (tickets 16 and 17 built by Part 2)

/** Open invoices with what is still owed, in the shared invoice shape. Admin and accountant only. */
export function listReceivables(): Promise<Invoice[]> {
  return api<Invoice[]>("/accounting/receivables");
}

/** Admin and accountant only. Returns the invoice after the payment: paid once nothing is outstanding. */
export function recordPayment(invoiceId: number, amount: number): Promise<Invoice> {
  return api<Invoice>(`/invoices/${invoiceId}/payments`, { method: "POST", body: { amount } });
}
