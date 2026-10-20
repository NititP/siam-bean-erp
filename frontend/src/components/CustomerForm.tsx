import { useState, type FormEvent } from "react";
import ErrorMessage from "./ErrorMessage";
import type { Customer, CustomerInput } from "../lib/customers";
import "./RecordForm.css";

// Owner: Part 1

type Field = keyof CustomerInput;
type Values = Record<Field, string>;

const LABELS: Record<Field, string> = {
  name: "Name",
  tax_id: "Tax ID",
  payment_terms_days: "Payment terms (days, 0 = cash)",
};

function startingValues(customer?: Customer): Values {
  return {
    name: customer?.name ?? "",
    tax_id: customer?.tax_id ?? "",
    payment_terms_days: customer ? String(customer.payment_terms_days) : "0",
  };
}

/** The message for each field that needs fixing; empty when the form can be sent. */
function problems(values: Values): Partial<Record<Field, string>> {
  const found: Partial<Record<Field, string>> = {};
  if (!values.name.trim()) found.name = "Name is required.";
  if (!values.tax_id.trim()) found.tax_id = "Tax ID is required.";
  const days = Number(values.payment_terms_days);
  if (!values.payment_terms_days.trim()) found.payment_terms_days = "Payment terms are required.";
  else if (!Number.isInteger(days) || days < 0) found.payment_terms_days = "Enter a whole number of days, 0 or more.";
  return found;
}

type Props = {
  /** The customer being edited; none to create a new one. */
  customer?: Customer;
  onSave: (input: CustomerInput) => Promise<unknown>;
  onDone: () => void;
};

/** Create or edit form for Sales and the Admin. Shows the API's detail text if saving fails. */
export default function CustomerForm({ customer, onSave, onDone }: Props) {
  const [values, setValues] = useState(() => startingValues(customer));
  const [tried, setTried] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const found = problems(values);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setTried(true);
    if (Object.keys(found).length > 0) return;
    setSaving(true);
    setError(null);
    try {
      await onSave({
        name: values.name.trim(),
        tax_id: values.tax_id.trim(),
        payment_terms_days: Number(values.payment_terms_days),
      });
      onDone();
    } catch (err) {
      setError(err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="record-form" onSubmit={submit} noValidate>
      <h2>{customer ? `Edit ${customer.name}` : "Add customer"}</h2>
      {(Object.keys(LABELS) as Field[]).map((field) => (
        <label key={field}>
          {LABELS[field]}
          <input
            value={values[field]}
            inputMode={field === "name" ? undefined : "numeric"}
            aria-invalid={tried && Boolean(found[field])}
            onChange={(e) => setValues({ ...values, [field]: e.target.value })}
          />
          {tried && found[field] && <span className="error">{found[field]}</span>}
        </label>
      ))}
      <ErrorMessage error={error} />
      <div className="form-actions">
        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save"}
        </button>
        <button type="button" onClick={onDone} disabled={saving}>
          Cancel
        </button>
      </div>
    </form>
  );
}
