import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { getUserProfile } from "@/services/users/get-user-profile";

export async function getCurrentUser() {
  const supabase = await createClient();
  const { data, error } = await supabase.auth.getUser();

  if (error || !data.user) return null;

  const profile = await getUserProfile(supabase, data.user.id);

  if (profile && !profile.is_active) return null;

  return { authUser: data.user, profile };
}

export async function requireCurrentUser() {
  const currentUser = await getCurrentUser();
  if (!currentUser) redirect("/login");
  return currentUser;
}
