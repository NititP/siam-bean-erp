import { api } from "./api";

// Owner: Part 1

/** The five live numbers from dashboard_numbers. Money in THB. */
export type DashboardNumbers = {
  sales_today: number;
  low_stock_count: number;
  open_invoices_count: number;
  open_receivables: number;
  stock_value: number;
};

/** Every role. */
export function getDashboard(): Promise<DashboardNumbers> {
  return api<DashboardNumbers>("/dashboard");
}
