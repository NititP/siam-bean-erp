import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { CUSTOMERS_PER_PAGE, formatTerms, listCustomers, type CustomerPage } from "../lib/customers";
import "../components/DataTable.css";
import "./CustomersPage.css";

const TYPING_PAUSE_MS = 300;

// Owner: Part 1
export default function CustomersPage() {
  const [search, setSearch] = useState("");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [result, setResult] = useState<CustomerPage | null>(null);
  const [error, setError] = useState<unknown>(null);

  // Search once typing pauses, starting again from page 1.
  useEffect(() => {
    const timer = setTimeout(() => {
      setQ(search.trim());
      setPage(1);
    }, TYPING_PAUSE_MS);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    let current = true; // ignore answers to an older search that arrive late
    listCustomers({ q, page }).then(
      (next) => {
        if (!current) return;
        setResult(next);
        setError(null);
      },
      (err) => current && setError(err),
    );
    return () => {
      current = false;
    };
  }, [q, page]);

  const pages = result ? Math.max(1, Math.ceil(result.total / CUSTOMERS_PER_PAGE)) : 1;

  return (
    <section>
      <h1>Customers</h1>
      <input
        className="customer-search"
        type="search"
        placeholder="Search by name"
        aria-label="Search customers by name"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <ErrorMessage error={error} />
      {!result && !error && <p className="muted">Loading…</p>}
      {result?.items.length === 0 && <EmptyState message="No customers match" />}
      {result && result.items.length > 0 && (
        <>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Tax ID</th>
                  <th>Payment terms</th>
                </tr>
              </thead>
              <tbody>
                {result.items.map((c) => (
                  <tr key={c.id}>
                    <td data-label="Name">{c.name}</td>
                    <td data-label="Tax ID">{c.tax_id}</td>
                    <td data-label="Payment terms">{formatTerms(c.payment_terms_days)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <nav className="pager" aria-label="Customer pages">
            <button disabled={page <= 1} onClick={() => setPage(page - 1)}>
              Previous
            </button>
            <span className="muted">
              Page {page} of {pages} · {result.total} customers
            </span>
            <button disabled={page >= pages} onClick={() => setPage(page + 1)}>
              Next
            </button>
          </nav>
        </>
      )}
    </section>
  );
}
