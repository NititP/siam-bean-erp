import { useCallback, useEffect, useState, type FormEvent } from "react";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { useAuth } from "../lib/auth";
import type { Role } from "../lib/roles";
import { changeRole, createUser, listUsers, ROLES, type User } from "../lib/users";
import "../components/DataTable.css";
import "../components/RecordForm.css";
import "./Users.css";

const BLANK = { email: "", full_name: "", role: "sales" as Role, password: "" };

// Owner: Part 3
export default function UsersPage() {
  const { me } = useAuth();
  const [users, setUsers] = useState<User[] | null>(null);
  const [loadError, setLoadError] = useState<unknown>(null);
  const [form, setForm] = useState(BLANK);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(() => {
    listUsers().then((next) => {
      setUsers(next);
      setLoadError(null);
    }, setLoadError);
  }, []);

  useEffect(load, [load]);

  async function add(e: FormEvent) {
    e.preventDefault();
    setNotice(null);
    setSaving(true);
    setError(null);
    try {
      const saved = await createUser(form);
      setNotice(`Added ${saved.full_name} as ${saved.role}.`);
      setForm(BLANK);
      load();
    } catch (err) {
      setError(err);
    } finally {
      setSaving(false);
    }
  }

  async function setRole(user: User, role: Role) {
    setNotice(null);
    setError(null);
    try {
      const saved = await changeRole(user.id, role);
      setNotice(`${saved.full_name} is now ${saved.role}.`);
      load();
    } catch (err) {
      setError(err);
    }
  }

  return (
    <section>
      <h1>Users</h1>
      <p className="muted">Add employees and choose what each one may do.</p>
      {notice && (
        <p className="success" role="status">
          {notice}
        </p>
      )}
      <form className="record-form" onSubmit={add} noValidate>
        <h2>Add user</h2>
        <label>
          Email
          <input
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </label>
        <label>
          Full name
          <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
        </label>
        <label>
          Role
          <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value as Role })}>
            {ROLES.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        </label>
        <label>
          Temporary password
          <input
            value={form.password}
            placeholder="At least 8 characters"
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </label>
        <ErrorMessage error={error} />
        <div className="form-actions">
          <button type="submit" disabled={saving}>
            {saving ? "Adding…" : "Add user"}
          </button>
        </div>
      </form>
      <ErrorMessage error={loadError} />
      {!users && !loadError && <p className="muted">Loading…</p>}
      {users?.length === 0 && <EmptyState message="No users yet" />}
      {users && users.length > 0 && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.full_name}</td>
                  <td>{user.email}</td>
                  <td>
                    <select
                      aria-label={`Role for ${user.full_name}`}
                      value={user.role}
                      disabled={user.email === me?.email}
                      title={user.email === me?.email ? "You cannot change your own role." : undefined}
                      onChange={(e) => setRole(user, e.target.value as Role)}
                    >
                      {ROLES.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
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
