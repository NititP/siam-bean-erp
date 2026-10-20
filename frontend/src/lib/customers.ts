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
export function listCustomers({ q = "", page = 1 } = {}): Promise<CustomerPage> {
  const params = new URLSearchParams({ q, page: String(page) });
  return api<CustomerPage>(`/customers?${params}`);
}

/** 0 -> "Cash", 30 -> "30 days". */
export function formatTerms(days: number): string {
  return days === 0 ? "Cash" : `${days} days`;
}
