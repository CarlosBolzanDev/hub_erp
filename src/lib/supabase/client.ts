import { createBrowserClient } from "@supabase/ssr";
import type { Database } from "@/types/database";

// Creates a typed Supabase client for Client Components and browser-side interactions.
export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL ?? "",
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "",
  );
}
