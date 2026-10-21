import { useEffect, useState } from "react";
import ErrorMessage from "../components/ErrorMessage";
import { getDashboard, type DashboardNumbers } from "../lib/dashboard";
import { formatTHB } from "../lib/money";
import "./Dashboard.css";

// Owner: Part 1
export default function DashboardPage() {
  const [numbers, setNumbers] = useState<DashboardNumbers | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    getDashboard().then(setNumbers, setError);
  }, []);

  return (
    <section>
      <h1>Dashboard</h1>
      <ErrorMessage error={error} />
      {!numbers && !error && <p className="muted">Loading…</p>}
      {numbers && (
        <div className="tiles">
          <Tile label="Sales today (incl. VAT)" value={formatTHB(numbers.sales_today)} />
          <Tile
            label="Low-stock products"
            value={String(numbers.low_stock_count)}
            alert={numbers.low_stock_count > 0}
          />
          <Tile
            label="Open invoices"
            value={String(numbers.open_invoices_count)}
            detail={`${formatTHB(numbers.open_receivables)} owed`}
          />
          <Tile label="Stock value (at cost)" value={formatTHB(numbers.stock_value)} />
        </div>
      )}
    </section>
  );
}

type TileProps = { label: string; value: string; detail?: string; alert?: boolean };

function Tile({ label, value, detail, alert = false }: TileProps) {
  return (
    <div className={alert ? "tile tile-alert" : "tile"}>
      <div className="tile-label">{label}</div>
      <div className="tile-value">{value}</div>
      {detail && <div className="tile-detail">{detail}</div>}
    </div>
  );
}
