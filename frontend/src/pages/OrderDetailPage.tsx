import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import { formatTHB } from "../lib/money";
import { confirmOrder, getOrder, STATUS_LABELS, type ConfirmResult, type Order } from "../lib/orders";
import "../components/DataTable.css";
import "./Orders.css";

// Owner: Part 2
export default function OrderDetailPage() {
  const { id = "" } = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [confirming, setConfirming] = useState(false);
  const [confirmError, setConfirmError] = useState<unknown>(null);
  const [issued, setIssued] = useState<ConfirmResult | null>(null);

  useEffect(() => {
    getOrder(id).then(setOrder, setError);
  }, [id]);

  const isDraft = order?.status === "draft";

  async function confirm() {
    if (!order) return;
    setConfirming(true);
    setConfirmError(null);
    try {
      setIssued(await confirmOrder(order.id));
      setOrder(await getOrder(order.id));
    } catch (err) {
      setConfirmError(err);
    } finally {
      setConfirming(false);
    }
  }

  return (
    <section>
      <p>
        <Link to="/orders">← Sales orders</Link>
      </p>
      <ErrorMessage error={error} />
      {!order && !error && <p className="muted">Loading…</p>}
      {order && (
        <>
          <h1>{order.number}</h1>
          <dl className="order-facts">
            <dt>Customer</dt>
            <dd>{order.customer_name}</dd>
            <dt>Status</dt>
            <dd>{STATUS_LABELS[order.status]}</dd>
            <dt>Order date</dt>
            <dd>{order.order_date}</dd>
          </dl>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Product</th>
                  <th className="num">Quantity</th>
                  <th className="num">Unit price</th>
                  <th className="num">Line total</th>
                  {isDraft && <th className="num">On hand</th>}
                </tr>
              </thead>
              <tbody>
                {order.lines.map((line) => (
                  <tr key={line.id}>
                    <td data-label="SKU">{line.sku}</td>
                    <td data-label="Product">{line.name}</td>
                    <td data-label="Quantity" className="num">
                      {line.quantity} {line.unit}
                    </td>
                    <td data-label="Unit price" className="num">
                      {formatTHB(line.unit_price)}
                    </td>
                    <td data-label="Line total" className="num">
                      {formatTHB(line.line_total)}
                    </td>
                    {isDraft && (
                      <td data-label="On hand" className="num">
                        {line.on_hand} {line.unit}
                        {line.on_hand !== null && line.quantity > line.on_hand && (
                          <div className="warning">
                            Only {line.on_hand} {line.unit} on hand
                          </div>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <td colSpan={4}>Total (before VAT)</td>
                  <td className="num">{formatTHB(order.total)}</td>
                  {isDraft && <td></td>}
                </tr>
              </tfoot>
            </table>
          </div>
          {issued && (
            <p className="success" role="status">
              Confirmed. Invoice <Link to={`/invoices/${issued.invoice_id}`}>{issued.invoice_number}</Link> issued for{" "}
              {formatTHB(issued.total)} (incl. VAT).
            </p>
          )}
          <ErrorMessage error={confirmError} />
          {isDraft && (
            <p>
              <button onClick={confirm} disabled={confirming}>
                {confirming ? "Confirming…" : "Confirm order"}
              </button>
            </p>
          )}
        </>
      )}
    </section>
  );
}
