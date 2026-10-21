import { api } from "./api";

// Owner: Part 1 (ticket 13 built by Part 2)

/** What POST /stock/in returns: the saved movement and the product's new stock on hand. */
export type StockMovement = {
  id: number;
  product_id: number;
  sku: string;
  unit: string;
  quantity: number;
  ref_doc: string;
  on_hand: number;
};

/** Admin and warehouse only. The note is optional. */
export function stockIn(productId: number, quantity: number, note: string): Promise<StockMovement> {
  return api<StockMovement>("/stock/in", { method: "POST", body: { product_id: productId, quantity, note } });
}
