import { Link } from "react-router-dom";
import { useAuth } from "../lib/auth";

// Owner: Part 3
export default function AccessDeniedPage() {
  const { me } = useAuth();
  return (
    <section>
      <h1>Access denied</h1>
      <p>Your role{me ? ` (${me.role})` : ""} cannot open this page.</p>
      <Link to="/dashboard">Back to the dashboard</Link>
    </section>
  );
}
