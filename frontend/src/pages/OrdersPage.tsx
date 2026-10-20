import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { formatTHB } from "../lib/money";
import { listOrders, STATUS_LABELS, type OrderSummary } from "../lib/orders";
import "../components/DataTable.css";
import "./Orders.css";

// Owner: Part 2
export default function OrdersPage() {
  const [orders, setOrders] = useState<OrderSummary[] | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    listOrders().then(setOrders, setError);
  }, []);

  return (
    <section>
      <div className="page-head">
        <h1>Sales orders</h1>
        <Link className="button-link" to="/orders/new">
          New order
        </Link>
      </div>
      <ErrorMessage error={error} />
      {!orders && !error && <p className="muted">Loading…</p>}
      {orders?.length === 0 && <EmptyState message="No sales orders yet." />}
      {orders && orders.length > 0 && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Number</th>
                <th>Customer</th>
                <th>Date</th>
                <th>Status</th>
                <th className="num">Total (before VAT)</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id}>
                  <td data-label="Number">
                    <Link to={`/orders/${o.id}`}>{o.number}</Link>
                  </td>
                  <td data-label="Customer">{o.customer_name}</td>
                  <td data-label="Date">{o.order_date}</td>
                  <td data-label="Status">{STATUS_LABELS[o.status]}</td>
                  <td data-label="Total (before VAT)" className="num">
                    {formatTHB(o.total)}
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
