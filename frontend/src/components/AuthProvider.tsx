import { useEffect, useState, type ReactNode } from "react";
import type { Session } from "@supabase/supabase-js";
import { api } from "../lib/api";
import { AuthContext, type Me } from "../lib/auth";
import { supabase } from "../lib/supabase";

/** Tracks the Supabase login and loads who the user is from GET /me. */
export default function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null | undefined>(undefined);
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data } = supabase.auth.onAuthStateChange((_event, next) => setSession(next));
    return () => data.subscription.unsubscribe();
  }, []);

  // Reload /me only when a different user logs in, not on every token refresh.
  const userId = session?.user.id;
  useEffect(() => {
    setMe(null);
    setError(null);
    if (!userId) return;
    api<Me>("/me").then(setMe, setError);
  }, [userId]);

  async function logOut() {
    await supabase.auth.signOut();
  }

  return (
    <AuthContext.Provider value={{ session, me, error, logOut }}>{children}</AuthContext.Provider>
  );
}
