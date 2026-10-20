import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import ErrorMessage from "./ErrorMessage";

/** Shows its children only to a logged-in user whose role is known. */
export default function RequireLogin({ children }: { children: ReactNode }) {
  const { session, me, error, logOut } = useAuth();

  if (session === undefined) return <p className="muted page-message">Loading…</p>;
  if (session === null) return <Navigate to="/login" replace />;
  if (error) {
    return (
      <div className="page-message">
        <ErrorMessage error={error} />
        <button onClick={logOut}>Log out</button>
      </div>
    );
  }
  if (!me) return <p className="muted page-message">Loading…</p>;
  return children;
}
