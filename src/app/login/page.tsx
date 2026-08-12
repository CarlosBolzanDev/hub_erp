import { redirect } from "next/navigation";
import { PackageCheck } from "lucide-react";
import { LoginForm } from "@/components/auth/LoginForm";
import { Card } from "@/components/ui/Card";
import { getCurrentUser } from "@/lib/auth/get-current-user";

export default async function LoginPage() {
  const user = await getCurrentUser();
  if (user) redirect("/dashboard");

  return <main className="grid min-h-screen place-items-center px-4 py-10"><div className="w-full max-w-md"><div className="mb-8 text-center"><div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-[var(--color-primary)] shadow-[var(--shadow-button)]"><PackageCheck className="h-7 w-7 text-white" /></div><h1 className="text-3xl font-bold text-white">Entrar no Bibly</h1><p className="mt-2 text-[var(--color-text-muted)]">Gerencie conferências e expedições com segurança.</p></div><Card><LoginForm /></Card></div></main>;
}
