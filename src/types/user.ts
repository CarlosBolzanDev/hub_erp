export type UserRole = "admin" | "operator";

export type AppUser = {
  id: string;
  auth_user_id: string;
  name: string | null;
  email: string | null;
  avatar_url: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};
