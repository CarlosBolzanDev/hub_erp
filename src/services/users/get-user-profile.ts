import type { SupabaseClient } from "@supabase/supabase-js";
import type { AppUser } from "@/types/user";

export async function getUserProfile(supabase: SupabaseClient, authUserId: string) {
  const { data, error } = await supabase
    .from("users")
    .select("id, auth_user_id, name, email, avatar_url, role, is_active, created_at, updated_at")
    .eq("auth_user_id", authUserId)
    .maybeSingle<AppUser>();

  if (error) {
    throw new Error("Não foi possível carregar o perfil do usuário.");
  }

  return data;
}
