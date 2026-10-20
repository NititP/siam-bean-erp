import { api } from "./api";

// Owner: Part 1

/** One row of GET /products. */
export type Product = {
  id: number;
  sku: string;
  name: string;
  unit: string;
  price: number;
  reorder_level: number;
  active: boolean;
  on_hand: number;
  low_stock: boolean;
};

/** Active products with stock on hand; inactive ones too when asked for. */
export function listProducts({ includeInactive = false } = {}): Promise<Product[]> {
  return api<Product[]>(`/products${includeInactive ? "?include_inactive=true" : ""}`);
}
