import { api } from "./api";

// Owner: Part 1

/** One row of GET /products. */
export type Product = {
  id: number;
  sku: string;
  name: string;
  unit: string;
  cost: number;
  price: number;
  reorder_level: number;
  active: boolean;
  on_hand: number;
  low_stock: boolean;
};

/** What the Admin types in to create or edit a product. */
export type ProductInput = Pick<Product, "sku" | "name" | "unit" | "cost" | "price" | "reorder_level">;

/** Active products with stock on hand; inactive ones too when asked for. */
export function listProducts({ includeInactive = false } = {}): Promise<Product[]> {
  return api<Product[]>(`/products${includeInactive ? "?include_inactive=true" : ""}`);
}

/** Admin only. */
export function createProduct(input: ProductInput): Promise<Product> {
  return api<Product>("/products", { method: "POST", body: input });
}

/** Admin only. */
export function editProduct(id: number, input: ProductInput): Promise<Product> {
  return api<Product>(`/products/${id}`, { method: "PATCH", body: input });
}
