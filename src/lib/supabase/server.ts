import { createServerClient } from "@supabase/ssr";
import { createClient } from "@supabase/supabase-js";
import { cookies } from "next/headers";
export function createSupabaseServerClient() { const cookieStore = cookies(); return createServerClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!, { cookies: { get: (n) => cookieStore.get(n)?.value, set: (n,v,o) => cookieStore.set({ name:n, value:v, ...o }), remove: (n,o) => cookieStore.set({ name:n, value:"", ...o }) } }); }
export function createSupabaseAdminClient() { return createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!, { auth: { persistSession: false } }); }
export async function requireUser() { const supabase = createSupabaseServerClient(); const { data: { user } } = await supabase.auth.getUser(); if (!user) throw new Error("Não autenticado"); const { data } = await createSupabaseAdminClient().from("users").select("role").eq("id", user.id).single(); return { user, role: data?.role as "ADMIN" | "PERSONAL" | undefined }; }
export async function requireAdmin() { const ctx = await requireUser(); if (ctx.role !== "ADMIN") throw new Error("Acesso negado"); return ctx; }
