import { api } from "./api";

// Owner: Part 2

export type InvoiceStatus = "open" | "paid" | "cancelled";

/** The invoice shape shared by the invoice list, invoice detail and accounting receivables. */
export type Invoice = {
  id: number;
  number: string;
  order_number: string;
  customer_name: string;
  issue_date: string;
  due_date: string;
  subtotal: number;
  vat: number;
  total: number;
  status: InvoiceStatus;
  paid: number;
  outstanding: number;
};

export type InvoiceLine = {
  sku: string;
  name: string;
  unit: string;
  quantity: number;
  unit_price: number;
  line_total: number;
};

export type Payment = { amount: number; paid_at: string };

/** GET /invoices/{id}: the shared shape plus lines and payments. */
export type InvoiceDetail = Invoice & { lines: InvoiceLine[]; payments: Payment[] };

/** Every invoice, newest first. */
export function listInvoices(): Promise<Invoice[]> {
  return api<Invoice[]>("/invoices");
}

export function getInvoice(id: number | string): Promise<InvoiceDetail> {
  return api<InvoiceDetail>(`/invoices/${id}`);
}

export const INVOICE_STATUS_LABELS: Record<InvoiceStatus, string> = {
  open: "Open",
  paid: "Paid",
  cancelled: "Cancelled",
};
