import type { ReactNode } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { requireCurrentUser } from "@/lib/auth/get-current-user";

export default async function ProtectedLayout({ children }: { children: ReactNode }) {
  const user = await requireCurrentUser();
  return <AppShell user={user}>{children}</AppShell>;
}
