import { useCallback, useEffect, useState, type FormEvent } from "react";
import ErrorMessage from "../components/ErrorMessage";
import { listProducts, type Product } from "../lib/products";
import { stockIn } from "../lib/stock";
import "../components/RecordForm.css";

// Owner: Part 1 (ticket 13 built by Part 2)
export default function StockInPage() {
  const [products, setProducts] = useState<Product[] | null>(null);
  const [loadError, setLoadError] = useState<unknown>(null);
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(() => {
    listProducts().then((next) => {
      setProducts(next);
      setLoadError(null);
    }, setLoadError);
  }, []);

  useEffect(load, [load]);

  const product = products?.find((p) => String(p.id) === productId);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setNotice(null);
    const value = Number(quantity);
    if (!product) {
      setError(new Error("Choose a product."));
      return;
    }
    if (!quantity.trim() || !Number.isInteger(value) || value <= 0) {
      setError(new Error("Quantity must be a whole number more than 0, for example 30."));
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const saved = await stockIn(product.id, value, note);
      setNotice(`Added ${saved.quantity} ${saved.unit} of ${saved.sku}. On hand is now ${saved.on_hand}.`);
      setQuantity("");
      setNote("");
      load();
    } catch (err) {
      setError(err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section>
      <h1>Stock in</h1>
      <p className="muted">Record goods arriving. Stock on hand goes up as soon as you save.</p>
      {notice && (
        <p className="success" role="status">
          {notice}
        </p>
      )}
      <ErrorMessage error={loadError} />
      {!products && !loadError && <p className="muted">Loading…</p>}
      {products && (
        <form className="record-form" onSubmit={submit} noValidate>
          <label>
            Product
            <select value={productId} onChange={(e) => setProductId(e.target.value)}>
              <option value="">Choose a product</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.sku}: {p.name} ({p.on_hand} {p.unit} on hand{p.low_stock ? ", low stock" : ""})
                </option>
              ))}
            </select>
          </label>
          <label>
            Quantity{product ? ` (${product.unit})` : ""}
            <input value={quantity} inputMode="numeric" onChange={(e) => setQuantity(e.target.value)} />
          </label>
          <label>
            Note (optional)
            <input value={note} placeholder="e.g. Doi Chang delivery" onChange={(e) => setNote(e.target.value)} />
          </label>
          <ErrorMessage error={error} />
          <div className="form-actions">
            <button type="submit" disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
