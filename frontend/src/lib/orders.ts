import { api } from "./api";

// Owner: Part 2

export type OrderStatus = "draft" | "confirmed" | "cancelled";

/** One order line: price and cost were copied from the product when the order was made. */
export type OrderLine = {
  id: number;
  product_id: number;
  sku: string;
  name: string;
  unit: string;
  quantity: number;
  unit_price: number;
  unit_cost: number;
  line_total: number;
  /** Stock on hand now; only for lines of a draft, otherwise null. */
  on_hand: number | null;
};

/** GET /orders/{id}. `total` is before VAT; the invoice adds VAT on confirm. */
export type Order = {
  id: number;
  number: string;
  customer_id: number;
  customer_name: string;
  status: OrderStatus;
  order_date: string;
  confirmed_at: string | null;
  lines: OrderLine[];
  total: number;
};

/** One row of GET /orders, newest first. */
export type OrderSummary = Pick<Order, "id" | "number" | "customer_name" | "order_date" | "status" | "total">;

/** What Sales sends to create a draft. */
export type OrderInput = {
  customer_id: number;
  lines: { product_id: number; quantity: number }[];
};

export function listOrders(): Promise<OrderSummary[]> {
  return api<OrderSummary[]>("/orders");
}

export function getOrder(id: number | string): Promise<Order> {
  return api<Order>(`/orders/${id}`);
}

/** Admin and sales only. Saves a draft with the next SO number. */
export function createOrder(input: OrderInput): Promise<Order> {
  return api<Order>("/orders", { method: "POST", body: input });
}

export const STATUS_LABELS: Record<OrderStatus, string> = {
  draft: "Draft",
  confirmed: "Confirmed",
  cancelled: "Cancelled",
};
