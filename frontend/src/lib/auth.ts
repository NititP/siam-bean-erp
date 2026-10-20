import { createContext, useContext } from "react";
import type { Session } from "@supabase/supabase-js";
import type { Role } from "./roles";

/** The logged-in user, from GET /me. */
export type Me = { email: string; full_name: string; role: Role };

export type AuthState = {
  /** undefined while we don't know yet; null when logged out. */
  session: Session | null | undefined;
  me: Me | null;
  error: unknown;
  logOut: () => Promise<void>;
};

export const AuthContext = createContext<AuthState | null>(null);

export function useAuth(): AuthState {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error("useAuth must be used inside <AuthProvider>");
  return auth;
}
