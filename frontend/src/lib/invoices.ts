import { api, apiBlob } from "./api";

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
export type InvoiceDetail = Invoice & { customer_tax_id: string; lines: InvoiceLine[]; payments: Payment[] };

/** Every invoice, newest first. */
export function listInvoices(): Promise<Invoice[]> {
  return api<Invoice[]>("/invoices");
}

export function getInvoice(id: number | string): Promise<InvoiceDetail> {
  return api<InvoiceDetail>(`/invoices/${id}`);
}

/** Admin, sales and accountant. Saves the tax invoice as e.g. INV-0001.pdf. */
export async function downloadInvoicePdf(invoice: Pick<Invoice, "id" | "number">): Promise<void> {
  const url = URL.createObjectURL(await apiBlob(`/invoices/${invoice.id}/pdf`));
  const link = document.createElement("a");
  link.href = url;
  link.download = `${invoice.number}.pdf`;
  link.click();
  URL.revokeObjectURL(url);
}

export const INVOICE_STATUS_LABELS: Record<InvoiceStatus, string> = {
  open: "Open",
  paid: "Paid",
  cancelled: "Cancelled",
};
