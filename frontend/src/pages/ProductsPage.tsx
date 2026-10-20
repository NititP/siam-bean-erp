import { useCallback, useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import LowStockBadge from "../components/LowStockBadge";
import ProductForm from "../components/ProductForm";
import { useAuth } from "../lib/auth";
import { formatTHB } from "../lib/money";
import { createProduct, editProduct, listProducts, type Product } from "../lib/products";
import "../components/DataTable.css";

/** Which form is open: none, the create form, or the edit form for one product. */
type Editing = null | "new" | Product;

// Owner: Part 1
export default function ProductsPage() {
  const { me } = useAuth();
  const isAdmin = me?.role === "admin"; // hiding the buttons is not security: the API checks too
  const [products, setProducts] = useState<Product[] | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [editing, setEditing] = useState<Editing>(null);

  const load = useCallback(() => {
    listProducts().then((next) => {
      setProducts(next);
      setError(null);
    }, setError);
  }, []);

  useEffect(load, [load]);

  function closeForm() {
    setEditing(null);
    load();
  }

  return (
    <section>
      <h1>Products</h1>
      {isAdmin && editing === null && <button onClick={() => setEditing("new")}>Add product</button>}
      {editing !== null && (
        <ProductForm
          key={editing === "new" ? "new" : editing.id}
          product={editing === "new" ? undefined : editing}
          onSave={(input) => (editing === "new" ? createProduct(input) : editProduct(editing.id, input))}
          onDone={closeForm}
        />
      )}
      <ErrorMessage error={error} />
      {!products && !error && <p className="muted">Loading…</p>}
      {products?.length === 0 && <EmptyState message="No products yet." />}
      {products && products.length > 0 && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Name</th>
                <th>Unit</th>
                <th className="num">Price</th>
                <th className="num">On hand</th>
                <th></th>
                {isAdmin && <th></th>}
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id}>
                  <td data-label="SKU">{p.sku}</td>
                  <td data-label="Name">{p.name}</td>
                  <td data-label="Unit">{p.unit}</td>
                  <td data-label="Price" className="num">
                    {formatTHB(p.price)}
                  </td>
                  <td data-label="On hand" className="num">
                    {p.on_hand}
                  </td>
                  <td>
                    <LowStockBadge lowStock={p.low_stock} />
                  </td>
                  {isAdmin && (
                    <td>
                      <button onClick={() => setEditing(p)}>Edit</button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
