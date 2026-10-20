import "./LowStockBadge.css";

// Owner: Part 1. Also used by the New order product picker.

/** Shown next to a product whose stock on hand is below its reorder level. */
export default function LowStockBadge({ lowStock }: { lowStock: boolean }) {
  if (!lowStock) return null;
  return <span className="badge-low-stock">Low stock</span>;
}
