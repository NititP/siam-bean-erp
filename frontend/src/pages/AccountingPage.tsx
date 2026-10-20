import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { listReceivables } from "../lib/accounting";
import type { Invoice } from "../lib/invoices";
import { formatTHB } from "../lib/money";
import "../components/DataTable.css";

// Owner: Part 3 (tickets 16 and 17 built by Part 2)
export default function AccountingPage() {
  const [invoices, setInvoices] = useState<Invoice[] | null>(null);
  const [error, setError] = useState<unknown>(null);

  const load = useCallback(() => {
    listReceivables().then((next) => {
      setInvoices(next);
      setError(null);
    }, setError);
  }, []);

  useEffect(load, [load]);

  return (
    <section>
      <h1>Accounting</h1>
      <ErrorMessage error={error} />
      {!invoices && !error && <p className="muted">Loading…</p>}
      {invoices?.length === 0 && <EmptyState message="Nothing is owed: every invoice is paid." />}
      {invoices && invoices.length > 0 && (
        <>
          <p className="muted">Open invoices and what is still owed on each.</p>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Customer</th>
                  <th>Issued</th>
                  <th>Due</th>
                  <th className="num">Total</th>
                  <th className="num">Paid</th>
                  <th className="num">Outstanding</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((i) => (
                  <tr key={i.id}>
                    <td data-label="Invoice">
                      <Link to={`/invoices/${i.id}`}>{i.number}</Link>
                    </td>
                    <td data-label="Customer">{i.customer_name}</td>
                    <td data-label="Issued">{i.issue_date}</td>
                    <td data-label="Due">{i.due_date}</td>
                    <td data-label="Total" className="num">
                      {formatTHB(i.total)}
                    </td>
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
        </>
      )}
    </section>
  );
}
