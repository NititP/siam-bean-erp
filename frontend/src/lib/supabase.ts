import { createClient } from "@supabase/supabase-js";

// Used only to log in. All data goes through our FastAPI (see api.ts).
export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY,
);
