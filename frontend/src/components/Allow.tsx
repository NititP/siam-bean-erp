import type { ReactNode } from "react";
import { useAuth } from "../lib/auth";
import type { Role } from "../lib/roles";
import AccessDeniedPage from "../pages/AccessDeniedPage";

/** Shows the page to these roles; everyone else sees the access-denied page. */
export default function Allow({ roles, children }: { roles: Role[]; children: ReactNode }) {
  const { me } = useAuth();
  return me && roles.includes(me.role) ? children : <AccessDeniedPage />;
}
