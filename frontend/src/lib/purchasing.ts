import { api } from "./api";

// Owner: Part 1 (bonus)

export type Supplier = {
  id: number;
  name: string;
  location: string | null;
  lead_time_days: number;
  payment_terms_days: number;
};

export type PurchaseOrderStatus = "draft" | "received" | "cancelled";

export type PurchaseOrderLine = {
  id: number;
  product_id: number;
  sku: string;
  name: string;
  unit: string;
  quantity: number;
  unit_cost: number;
  line_total: number;
};

export type PurchaseOrder = {
  id: number;
  number: string;
  supplier_id: number;
  supplier_name: string;
  status: PurchaseOrderStatus;
  order_date: string;
  received_at: string | null;
  lines: PurchaseOrderLine[];
  total: number;
};

/** What Admin or Warehouse sends to create a draft. */
export type PurchaseOrderInput = {
  supplier_id: number;
  lines: { product_id: number; quantity: number; unit_cost: number }[];
};

/** Admin and warehouse only, like every call below. Active suppliers. */
export function listSuppliers(): Promise<Supplier[]> {
  return api<Supplier[]>("/suppliers");
}

/** Newest first, with lines. */
export function listPurchaseOrders(): Promise<PurchaseOrder[]> {
  return api<PurchaseOrder[]>("/purchase-orders");
}

/** Saves a draft with the next PO number. */
export function createPurchaseOrder(input: PurchaseOrderInput): Promise<PurchaseOrder> {
  return api<PurchaseOrder>("/purchase-orders", { method: "POST", body: input });
}

/** Adds every line's quantity to stock on hand, once. */
export function receivePurchaseOrder(id: number): Promise<ReceiveResult> {
  return api<ReceiveResult>(`/purchase-orders/${id}/receive`, { method: "POST" });
}

/** What POST /purchase-orders/{id}/receive returns. */
export type ReceiveResult = { po_number: string; status: "received" };

export const PO_STATUS_LABELS: Record<PurchaseOrderStatus, string> = {
  draft: "Draft",
  received: "Received",
  cancelled: "Cancelled",
};
