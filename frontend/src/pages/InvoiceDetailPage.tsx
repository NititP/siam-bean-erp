import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { downloadInvoicePdf, getInvoice, INVOICE_STATUS_LABELS, type InvoiceDetail } from "../lib/invoices";
import { formatTHB } from "../lib/money";
import "../components/DataTable.css";
import "./Orders.css";

// Owner: Part 2. Payments are recorded only on the Accounting screen: no button here.
export default function InvoiceDetailPage() {
  const { id = "" } = useParams();
  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<unknown>(null);

  useEffect(() => {
    getInvoice(id).then(setInvoice, setError);
  }, [id]);

  async function download(of: InvoiceDetail) {
    setDownloading(true);
    setDownloadError(null);
    try {
      await downloadInvoicePdf(of);
    } catch (err) {
      setDownloadError(err);
    } finally {
      setDownloading(false);
    }
  }

  return (
    <section>
      <p>
        <Link to="/invoices">← Invoices</Link>
      </p>
      <ErrorMessage error={error} />
      {!invoice && !error && <p className="muted">Loading…</p>}
      {invoice && (
        <>
          <h1>{invoice.number}</h1>
          <p>
            <button onClick={() => download(invoice)} disabled={downloading}>
              {downloading ? "Preparing PDF…" : "Download PDF"}
            </button>
          </p>
          <ErrorMessage error={downloadError} />
          <dl className="order-facts">
            <dt>Customer</dt>
            <dd>{invoice.customer_name}</dd>
            <dt>Customer tax ID</dt>
            <dd>{invoice.customer_tax_id}</dd>
            <dt>Sales order</dt>
            <dd>{invoice.order_number}</dd>
            <dt>Issued</dt>
            <dd>{invoice.issue_date}</dd>
            <dt>Due</dt>
            <dd>{invoice.due_date}</dd>
            <dt>Status</dt>
            <dd>{INVOICE_STATUS_LABELS[invoice.status]}</dd>
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
                </tr>
              </thead>
              <tbody>
                {invoice.lines.map((line, n) => (
                  <tr key={n}>
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
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <td colSpan={4}>Subtotal</td>
                  <td className="num">{formatTHB(invoice.subtotal)}</td>
                </tr>
                <tr>
                  <td colSpan={4}>VAT 7%</td>
                  <td className="num">{formatTHB(invoice.vat)}</td>
                </tr>
                <tr>
                  <td colSpan={4}>Total</td>
                  <td className="num">{formatTHB(invoice.total)}</td>
                </tr>
                <tr>
                  <td colSpan={4}>Paid</td>
                  <td className="num">{formatTHB(invoice.paid)}</td>
                </tr>
                <tr>
                  <td colSpan={4}>Outstanding</td>
                  <td className="num">{formatTHB(invoice.outstanding)}</td>
                </tr>
              </tfoot>
            </table>
          </div>

          <h2>Payments</h2>
          {invoice.payments.length === 0 && <EmptyState message="No payments yet." />}
          {invoice.payments.length > 0 && (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Paid at</th>
                    <th className="num">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.payments.map((p, n) => (
                    <tr key={n}>
                      <td data-label="Paid at">{new Date(p.paid_at).toLocaleString("en-GB")}</td>
                      <td data-label="Amount" className="num">
                        {formatTHB(p.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  );
}
