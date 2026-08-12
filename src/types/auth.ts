import type { User } from "@supabase/supabase-js";
import type { AppUser } from "./user";

export type CurrentUser = {
  authUser: User;
  profile: AppUser | null;
};
