import { useState, type FormEvent } from "react";
import ErrorMessage from "./ErrorMessage";
import type { Product, ProductInput } from "../lib/products";
import "./ProductForm.css";

// Owner: Part 1

type Field = keyof ProductInput;
type Values = Record<Field, string>;

const LABELS: Record<Field, string> = {
  sku: "SKU",
  name: "Name",
  unit: "Unit",
  cost: "Cost (THB)",
  price: "Price (THB, without VAT)",
  reorder_level: "Reorder level",
};

function startingValues(product?: Product): Values {
  return {
    sku: product?.sku ?? "",
    name: product?.name ?? "",
    unit: product?.unit ?? "kg",
    cost: product ? String(product.cost) : "",
    price: product ? String(product.price) : "",
    reorder_level: product ? String(product.reorder_level) : "0",
  };
}

/** The message for each field that needs fixing; empty when the form can be sent. */
function problems(values: Values): Partial<Record<Field, string>> {
  const found: Partial<Record<Field, string>> = {};
  for (const field of ["sku", "name", "unit"] as const) {
    if (!values[field].trim()) found[field] = `${LABELS[field]} is required.`;
  }
  for (const field of ["cost", "price"] as const) {
    const n = Number(values[field]);
    if (!values[field].trim()) found[field] = `${LABELS[field]} is required.`;
    else if (!Number.isFinite(n) || n < 0) found[field] = "Enter an amount of 0 or more.";
  }
  const level = Number(values.reorder_level);
  if (!values.reorder_level.trim()) found.reorder_level = "Reorder level is required.";
  else if (!Number.isInteger(level) || level < 0) found.reorder_level = "Enter a whole number of 0 or more.";
  return found;
}

type Props = {
  /** The product being edited; none to create a new one. */
  product?: Product;
  onSave: (input: ProductInput) => Promise<unknown>;
  onDone: () => void;
};

/** Create or edit form for the Admin. Shows the API's detail text if saving fails. */
export default function ProductForm({ product, onSave, onDone }: Props) {
  const [values, setValues] = useState(() => startingValues(product));
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
        sku: values.sku.trim(),
        name: values.name.trim(),
        unit: values.unit.trim(),
        cost: Number(values.cost),
        price: Number(values.price),
        reorder_level: Number(values.reorder_level),
      });
      onDone();
    } catch (err) {
      setError(err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="product-form" onSubmit={submit} noValidate>
      <h2>{product ? `Edit ${product.sku}` : "Add product"}</h2>
      {(Object.keys(LABELS) as Field[]).map((field) => (
        <label key={field}>
          {LABELS[field]}
          <input
            value={values[field]}
            inputMode={["cost", "price", "reorder_level"].includes(field) ? "decimal" : undefined}
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
