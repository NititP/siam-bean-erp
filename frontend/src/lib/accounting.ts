import { api } from "./api";
import type { Invoice } from "./invoices";

// Owner: Part 3 (tickets 16 and 17 built by Part 2)

/** Open invoices with what is still owed, in the shared invoice shape. Admin and accountant only. */
export function listReceivables(): Promise<Invoice[]> {
  return api<Invoice[]>("/accounting/receivables");
}
