import { useEffect, useState } from "react";
import CustomerForm from "../components/CustomerForm";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { useAuth } from "../lib/auth";
import {
  CUSTOMERS_PER_PAGE,
  createCustomer,
  editCustomer,
  formatTerms,
  listCustomers,
  type Customer,
  type CustomerPage,
} from "../lib/customers";
import type { Role } from "../lib/roles";
import "../components/DataTable.css";
import "./CustomersPage.css";

const TYPING_PAUSE_MS = 300;
// Who may create, edit and deactivate customers (docs/plan.md roles). The API checks too.
const EDITORS: Role[] = ["admin", "sales"];

/** Which form is open: none, the create form, or the edit form for one customer. */
type Editing = null | "new" | Customer;

// Owner: Part 1
export default function CustomersPage() {
  const { me } = useAuth();
  const canEdit = me !== null && EDITORS.includes(me.role);
  const [editing, setEditing] = useState<Editing>(null);
  const [reloads, setReloads] = useState(0); // bump to fetch the current page again
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
        // Past the last page of this search (it has fewer matches): go to its last page.
        if (next.items.length === 0 && next.total > 0) {
          setPage(Math.ceil(next.total / CUSTOMERS_PER_PAGE));
          return;
        }
        setResult(next);
        setError(null);
      },
      (err) => current && setError(err),
    );
    return () => {
      current = false;
    };
  }, [q, page, reloads]);

  function closeForm() {
    setEditing(null);
    setReloads((n) => n + 1);
  }

  const pages = result ? Math.max(1, Math.ceil(result.total / CUSTOMERS_PER_PAGE)) : 1;

  return (
    <section>
      <h1>Customers</h1>
      {canEdit && editing === null && (
        <p>
          <button onClick={() => setEditing("new")}>Add customer</button>
        </p>
      )}
      {editing !== null && (
        <CustomerForm
          key={editing === "new" ? "new" : editing.id}
          customer={editing === "new" ? undefined : editing}
          onSave={(input) => (editing === "new" ? createCustomer(input) : editCustomer(editing.id, input))}
          onDone={closeForm}
        />
      )}
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
                  {canEdit && <th></th>}
                </tr>
              </thead>
              <tbody>
                {result.items.map((c) => (
                  <tr key={c.id}>
                    <td data-label="Name">{c.name}</td>
                    <td data-label="Tax ID">{c.tax_id}</td>
                    <td data-label="Payment terms">{formatTerms(c.payment_terms_days)}</td>
                    {canEdit && (
                      <td className="row-actions">
                        <button onClick={() => setEditing(c)}>Edit</button>
                      </td>
                    )}
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
