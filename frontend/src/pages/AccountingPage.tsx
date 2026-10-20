import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { listReceivables, recordPayment } from "../lib/accounting";
import type { Invoice } from "../lib/invoices";
import { formatTHB } from "../lib/money";
import "../components/DataTable.css";
import "./Accounting.css";

// Owner: Part 3 (tickets 16 and 17 built by Part 2)
export default function AccountingPage() {
  const [invoices, setInvoices] = useState<Invoice[] | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [paying, setPaying] = useState<Invoice | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(() => {
    listReceivables().then((next) => {
      setInvoices(next);
      setError(null);
    }, setError);
  }, []);

  useEffect(load, [load]);

  function paid(invoice: Invoice) {
    setPaying(null);
    setNotice(
      invoice.status === "paid"
        ? `${invoice.number} is now paid.`
        : `Payment recorded. ${invoice.number} still has ${formatTHB(invoice.outstanding)} outstanding.`,
    );
    load();
  }

  return (
    <section>
      <h1>Accounting</h1>
      {notice && (
        <p className="success" role="status">
          {notice}
        </p>
      )}
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
                  <th></th>
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
                    <td className="row-actions">
                      {paying?.id === i.id ? (
                        <PaymentForm invoice={i} onPaid={paid} onCancel={() => setPaying(null)} />
                      ) : (
                        <button
                          onClick={() => {
                            setNotice(null);
                            setPaying(i);
                          }}
                        >
                          Record payment
                        </button>
                      )}
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

type FormProps = { invoice: Invoice; onPaid: (invoice: Invoice) => void; onCancel: () => void };

/** Amount starts at the full outstanding; the API checks the range and says what is allowed. */
function PaymentForm({ invoice, onPaid, onCancel }: FormProps) {
  const [amount, setAmount] = useState(invoice.outstanding.toFixed(2));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    const value = Number(amount);
    if (!amount.trim() || !Number.isFinite(value)) {
      setError(new Error("Enter the amount paid, for example 9630.00."));
      return;
    }
    setSaving(true);
    setError(null);
    try {
      onPaid(await recordPayment(invoice.id, value));
    } catch (err) {
      setError(err);
      setSaving(false);
    }
  }

  return (
    <form className="payment-form" onSubmit={submit} noValidate>
      <label>
        Amount (THB)
        <input value={amount} inputMode="decimal" onChange={(e) => setAmount(e.target.value)} autoFocus />
      </label>
      <button type="submit" disabled={saving}>
        {saving ? "Saving…" : "Save payment"}
      </button>
      <button type="button" onClick={onCancel} disabled={saving}>
        Cancel
      </button>
      <ErrorMessage error={error} />
    </form>
  );
}
