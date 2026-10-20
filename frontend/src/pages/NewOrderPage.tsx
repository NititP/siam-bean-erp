import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import LowStockBadge from "../components/LowStockBadge";
import { listCustomers, type Customer } from "../lib/customers";
import { formatTHB } from "../lib/money";
import { createOrder } from "../lib/orders";
import { listProducts, type Product } from "../lib/products";
import "./Orders.css";

/** One line as typed: product id and quantity are kept as text until saved. */
type Line = { key: number; productId: string; quantity: string };

let nextKey = 1;
const emptyLine = (): Line => ({ key: nextKey++, productId: "", quantity: "" });

// Owner: Part 2
export default function NewOrderPage() {
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [products, setProducts] = useState<Product[] | null>(null);
  const [lines, setLines] = useState<Line[]>(() => [emptyLine()]);
  const [tried, setTried] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<unknown>(null);

  // Active customers only (the API's default), searched as the user types.
  useEffect(() => {
    const timer = setTimeout(() => {
      listCustomers({ q }).then((page) => setCustomers(page.items), setError);
    }, 250);
    return () => clearTimeout(timer);
  }, [q]);

  // Active products only, with stock on hand and the low-stock flag.
  useEffect(() => {
    listProducts().then(setProducts, setError);
  }, []);

  const productById = new Map((products ?? []).map((p) => [String(p.id), p]));
  const options = customer && !customers.some((c) => c.id === customer.id) ? [customer, ...customers] : customers;

  function changeLine(key: number, change: Partial<Line>) {
    setLines(lines.map((line) => (line.key === key ? { ...line, ...change } : line)));
  }

  function lineProblem(line: Line): string | null {
    if (!line.productId) return "Pick a product.";
    const quantity = Number(line.quantity);
    if (!line.quantity.trim() || !Number.isInteger(quantity) || quantity <= 0) return "Enter a whole number above 0.";
    return null;
  }

  const problems = [!customer ? "Pick a customer." : null, ...lines.map(lineProblem)].filter(Boolean);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setTried(true);
    if (problems.length > 0 || !customer) return;
    setSaving(true);
    setError(null);
    try {
      const order = await createOrder({
        customer_id: customer.id,
        lines: lines.map((line) => ({ product_id: Number(line.productId), quantity: Number(line.quantity) })),
      });
      navigate(`/orders/${order.id}`);
    } catch (err) {
      setError(err);
      setSaving(false);
    }
  }

  return (
    <section>
      <h1>New order</h1>
      <form className="order-form" onSubmit={submit} noValidate>
        <div className="customer-pick">
          <label>
            Search customers
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Part of the name" />
          </label>
          <label>
            Customer
            <select
              value={customer?.id ?? ""}
              aria-invalid={tried && !customer}
              onChange={(e) => setCustomer(options.find((c) => String(c.id) === e.target.value) ?? null)}
            >
              <option value="">
                {customers.length === 0 ? "No active customers match" : "Choose a customer"}
              </option>
              {options.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            {tried && !customer && <span className="error">Pick a customer.</span>}
          </label>
        </div>

        {!products && <p className="muted">Loading products…</p>}
        {products?.length === 0 && <p className="empty">No active products to sell.</p>}
        {products &&
          lines.map((line) => {
            const product = productById.get(line.productId);
            const quantity = Number(line.quantity);
            const problem = tried ? lineProblem(line) : null;
            return (
              <div className="order-line" key={line.key}>
                <label>
                  Product
                  <select
                    value={line.productId}
                    aria-invalid={Boolean(problem && !line.productId)}
                    onChange={(e) => changeLine(line.key, { productId: e.target.value })}
                  >
                    <option value="">Choose a product</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.sku}: {p.name} ({p.on_hand} {p.unit} on hand{p.low_stock ? ", low stock" : ""})
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Quantity
                  <input
                    value={line.quantity}
                    inputMode="numeric"
                    aria-invalid={Boolean(problem && line.productId)}
                    onChange={(e) => changeLine(line.key, { quantity: e.target.value })}
                  />
                </label>
                <button
                  type="button"
                  onClick={() => setLines(lines.filter((l) => l.key !== line.key))}
                  disabled={lines.length === 1}
                >
                  Remove
                </button>
                <div className="line-notes">
                  {product && (
                    <>
                      <span className="muted">
                        {formatTHB(product.price)} per {product.unit} · {product.on_hand} {product.unit} on hand
                      </span>
                      <LowStockBadge lowStock={product.low_stock} />
                    </>
                  )}
                  {product && quantity > product.on_hand && (
                    <span className="warning">
                      Only {product.on_hand} {product.unit} on hand
                    </span>
                  )}
                  {problem && <span className="error">{problem}</span>}
                </div>
              </div>
            );
          })}

        <ErrorMessage error={error} />
        <div className="form-actions">
          <button type="button" onClick={() => setLines([...lines, emptyLine()])}>
            Add line
          </button>
          <button type="submit" disabled={saving || !products}>
            {saving ? "Saving…" : "Save draft"}
          </button>
          <Link to="/orders">Cancel</Link>
        </div>
      </form>
    </section>
  );
}
