import { api } from "./api";

// Owner: Part 1

/** One row of GET /customers. */
export type Customer = {
  id: number;
  name: string;
  tax_id: string;
  payment_terms_days: number;
  active: boolean;
};

/** One page of GET /customers: up to CUSTOMERS_PER_PAGE rows and the full match count. */
export type CustomerPage = { items: Customer[]; total: number };

export const CUSTOMERS_PER_PAGE = 20;

/** Customers whose name contains q (ignoring case), one page at a time from page 1. */
export function listCustomers({ q = "", page = 1, includeInactive = false } = {}): Promise<CustomerPage> {
  const params = new URLSearchParams({ q, page: String(page) });
  if (includeInactive) params.set("include_inactive", "true");
  return api<CustomerPage>(`/customers?${params}`);
}

/** Admin and sales only. No new orders go to this customer; old documents keep them. */
export function deactivateCustomer(id: number): Promise<Customer> {
  return api<Customer>(`/customers/${id}/deactivate`, { method: "POST" });
}

/** Admin and sales only. */
export function reactivateCustomer(id: number): Promise<Customer> {
  return api<Customer>(`/customers/${id}`, { method: "PATCH", body: { active: true } });
}

/** What Sales or the Admin types in to create or edit a customer. */
export type CustomerInput = Pick<Customer, "name" | "tax_id" | "payment_terms_days">;

/** Admin and sales only. */
export function createCustomer(input: CustomerInput): Promise<Customer> {
  return api<Customer>("/customers", { method: "POST", body: input });
}

/** Admin and sales only. */
export function editCustomer(id: number, input: CustomerInput): Promise<Customer> {
  return api<Customer>(`/customers/${id}`, { method: "PATCH", body: input });
}

/** 0 -> "Cash", 30 -> "30 days". */
export function formatTerms(days: number): string {
  return days === 0 ? "Cash" : `${days} days`;
}
