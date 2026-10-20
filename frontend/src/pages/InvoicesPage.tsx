import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { INVOICE_STATUS_LABELS, listInvoices, type Invoice } from "../lib/invoices";
import { formatTHB } from "../lib/money";
import "../components/DataTable.css";

// Owner: Part 2
export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[] | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    listInvoices().then(setInvoices, setError);
  }, []);

  return (
    <section>
      <h1>Invoices</h1>
      <ErrorMessage error={error} />
      {!invoices && !error && <p className="muted">Loading…</p>}
      {invoices?.length === 0 && <EmptyState message="No invoices yet. Confirming a sales order issues one." />}
      {invoices && invoices.length > 0 && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Number</th>
                <th>Order</th>
                <th>Customer</th>
                <th>Issued</th>
                <th>Due</th>
                <th className="num">Total</th>
                <th>Status</th>
                <th className="num">Paid</th>
                <th className="num">Outstanding</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((i) => (
                <tr key={i.id}>
                  <td data-label="Number">
                    <Link to={`/invoices/${i.id}`}>{i.number}</Link>
                  </td>
                  <td data-label="Order">{i.order_number}</td>
                  <td data-label="Customer">{i.customer_name}</td>
                  <td data-label="Issued">{i.issue_date}</td>
                  <td data-label="Due">{i.due_date}</td>
                  <td data-label="Total" className="num">
                    {formatTHB(i.total)}
                  </td>
                  <td data-label="Status">{INVOICE_STATUS_LABELS[i.status]}</td>
                  <td data-label="Paid" className="num">
                    {formatTHB(i.paid)}
                  </td>
                  <td data-label="Outstanding" className="num">
                    {formatTHB(i.outstanding)}
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
