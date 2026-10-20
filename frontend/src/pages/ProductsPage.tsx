import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import LowStockBadge from "../components/LowStockBadge";
import { formatTHB } from "../lib/money";
import { listProducts, type Product } from "../lib/products";
import "../components/DataTable.css";

// Owner: Part 1
export default function ProductsPage() {
  const [products, setProducts] = useState<Product[] | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    listProducts().then(setProducts, setError);
  }, []);

  return (
    <section>
      <h1>Products</h1>
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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
