import "./InactiveBadge.css";

// Owner: Part 1. Used by the Products and Customers lists.

/** Marks a deactivated product or customer when "Show inactive" is on. */
export default function InactiveBadge({ active }: { active: boolean }) {
  if (active) return null;
  return <span className="badge-inactive">Inactive</span>;
}
