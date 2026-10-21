import { useCallback, useEffect, useState, type FormEvent } from "react";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { formatTHB } from "../lib/money";
import { listProducts, type Product } from "../lib/products";
import {
  PO_STATUS_LABELS,
  createPurchaseOrder,
  listPurchaseOrders,
  listSuppliers,
  receivePurchaseOrder,
  type PurchaseOrder,
  type Supplier,
} from "../lib/purchasing";
import "../components/DataTable.css";
import "../components/RecordForm.css";
import "./PurchaseOrders.css";

// Owner: Part 1 (bonus)
export default function PurchaseOrdersPage() {
  const [orders, setOrders] = useState<PurchaseOrder[] | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [creating, setCreating] = useState(false);
  const [receiving, setReceiving] = useState<number | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(() => {
    listPurchaseOrders().then((next) => {
      setOrders(next);
      setError(null);
    }, setError);
  }, []);

  useEffect(load, [load]);

  async function receive(po: PurchaseOrder) {
    setReceiving(po.id);
    setNotice(null);
    setError(null);
    try {
      await receivePurchaseOrder(po.id);
      setNotice(`${po.number} received: its quantities are now in stock on hand.`);
      load();
    } catch (err) {
      setError(err);
    } finally {
      setReceiving(null);
    }
  }

  return (
    <section>
      <div className="page-head">
        <h1>Purchase orders</h1>
        {!creating && (
          <button
            onClick={() => {
              setNotice(null);
              setCreating(true);
            }}
          >
            New purchase order
          </button>
        )}
      </div>
      {creating && (
        <PurchaseOrderForm
          onSaved={(po) => {
            setCreating(false);
            setNotice(`${po.number} saved as a draft.`);
            load();
          }}
          onCancel={() => setCreating(false)}
        />
      )}
      {notice && (
        <p className="success" role="status">
          {notice}
        </p>
      )}
      <ErrorMessage error={error} />
      {!orders && !error && <p className="muted">Loading…</p>}
      {orders?.length === 0 && <EmptyState message="No purchase orders yet." />}
      {orders && orders.length > 0 && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Number</th>
                <th>Supplier</th>
                <th>Date</th>
                <th>Lines</th>
                <th className="num">Total</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {orders.map((po) => (
                <tr key={po.id}>
                  <td data-label="Number">{po.number}</td>
                  <td data-label="Supplier">{po.supplier_name}</td>
                  <td data-label="Date">{po.order_date}</td>
                  <td data-label="Lines">
                    {po.lines.map((line) => (
                      <div key={line.id}>
                        {line.quantity} {line.unit} {line.sku} @ {formatTHB(line.unit_cost)}
                      </div>
                    ))}
                  </td>
                  <td data-label="Total" className="num">
                    {formatTHB(po.total)}
                  </td>
                  <td data-label="Status">{PO_STATUS_LABELS[po.status]}</td>
                  <td className="row-actions">
                    {po.status === "draft" && (
                      <button onClick={() => receive(po)} disabled={receiving !== null}>
                        {receiving === po.id ? "Receiving…" : "Receive"}
                      </button>
                    )}
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

/** One line as typed: kept as text until saved. */
type Line = { key: number; productId: string; quantity: string; unitCost: string };

let nextKey = 1;
const emptyLine = (): Line => ({ key: nextKey++, productId: "", quantity: "", unitCost: "" });

type FormProps = { onSaved: (po: PurchaseOrder) => void; onCancel: () => void };

function PurchaseOrderForm({ onSaved, onCancel }: FormProps) {
  const [suppliers, setSuppliers] = useState<Supplier[] | null>(null);
  const [products, setProducts] = useState<Product[] | null>(null);
  const [supplierId, setSupplierId] = useState("");
  const [lines, setLines] = useState<Line[]>(() => [emptyLine()]);
  const [tried, setTried] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    listSuppliers().then(setSuppliers, setError);
    listProducts().then(setProducts, setError);
  }, []);

  const productById = new Map((products ?? []).map((p) => [String(p.id), p]));

  function changeLine(key: number, change: Partial<Line>) {
    setLines(lines.map((line) => (line.key === key ? { ...line, ...change } : line)));
  }

  /** Picking a product fills in its current cost; the user can change it. */
  function pickProduct(line: Line, productId: string) {
    const product = productById.get(productId);
    changeLine(line.key, { productId, unitCost: line.unitCost || (product ? String(product.cost) : "") });
  }

  function lineProblem(line: Line): string | null {
    if (!line.productId) return "Pick a product.";
    const quantity = Number(line.quantity);
    if (!line.quantity.trim() || !Number.isInteger(quantity) || quantity <= 0) return "Enter a whole number above 0.";
    const cost = Number(line.unitCost);
    if (!line.unitCost.trim() || !Number.isFinite(cost) || cost < 0) return "Enter a unit cost of 0 or more.";
    return null;
  }

  const problems = [!supplierId ? "Pick a supplier." : null, ...lines.map(lineProblem)].filter(Boolean);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setTried(true);
    if (problems.length > 0) return;
    setSaving(true);
    setError(null);
    try {
      onSaved(
        await createPurchaseOrder({
          supplier_id: Number(supplierId),
          lines: lines.map((line) => ({
            product_id: Number(line.productId),
            quantity: Number(line.quantity),
            unit_cost: Number(line.unitCost),
          })),
        }),
      );
    } catch (err) {
      setError(err);
      setSaving(false);
    }
  }

  return (
    <form className="record-form po-form" onSubmit={submit} noValidate>
      <h2>New purchase order</h2>
      <label>
        Supplier
        <select value={supplierId} aria-invalid={tried && !supplierId} onChange={(e) => setSupplierId(e.target.value)}>
          <option value="">{suppliers ? "Choose a supplier" : "Loading…"}</option>
          {suppliers?.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
        {tried && !supplierId && <span className="error">Pick a supplier.</span>}
      </label>

      {lines.map((line) => {
        const problem = tried ? lineProblem(line) : null;
        return (
          <div className="po-line" key={line.key}>
            <label>
              Product
              <select value={line.productId} onChange={(e) => pickProduct(line, e.target.value)}>
                <option value="">{products ? "Choose a product" : "Loading…"}</option>
                {products?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.sku}: {p.name} ({p.on_hand} {p.unit} on hand)
                  </option>
                ))}
              </select>
            </label>
            <label>
              Quantity
              <input
                value={line.quantity}
                inputMode="numeric"
                onChange={(e) => changeLine(line.key, { quantity: e.target.value })}
              />
            </label>
            <label>
              Unit cost (THB)
              <input
                value={line.unitCost}
                inputMode="decimal"
                onChange={(e) => changeLine(line.key, { unitCost: e.target.value })}
              />
            </label>
            <button
              type="button"
              onClick={() => setLines(lines.filter((l) => l.key !== line.key))}
              disabled={lines.length === 1}
            >
              Remove
            </button>
            {problem && <span className="error">{problem}</span>}
          </div>
        );
      })}

      <ErrorMessage error={error} />
      <div className="form-actions">
        <button type="button" onClick={() => setLines([...lines, emptyLine()])}>
          Add line
        </button>
        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save draft"}
        </button>
        <button type="button" onClick={onCancel} disabled={saving}>
          Cancel
        </button>
      </div>
    </form>
  );
}
