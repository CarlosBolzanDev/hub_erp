"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut, PackageCheck } from "lucide-react";
import { navigationItems } from "@/config/navigation";
import { Button } from "@/components/ui/Button";
import { logoutAction } from "@/services/auth/actions";
import { cn } from "@/utils/cn";
import type { CurrentUser } from "@/types/auth";

export function Sidebar({ user, onNavigate }: { user: CurrentUser; onNavigate?: () => void }) {
  const pathname = usePathname();
  const displayName = user.profile?.name ?? user.authUser.email ?? "Usuário";

  return (
    <aside className="flex h-full w-72 flex-col border-r border-[var(--color-border)] bg-[var(--color-sidebar)] p-5">
      <Link href="/dashboard" className="mb-8 flex items-center gap-3" onClick={onNavigate}>
        <span className="grid h-11 w-11 place-items-center rounded-2xl bg-[var(--color-primary)] shadow-[var(--shadow-button)]"><PackageCheck className="h-5 w-5 text-white" /></span>
        <span><strong className="block text-lg text-white">Bibly</strong><small className="text-[var(--color-text-muted)]">Marketplace Ops</small></span>
      </Link>
      <nav className="flex-1 space-y-2" aria-label="Navegação principal">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return <Link key={item.href} href={item.href} onClick={onNavigate} className={cn("flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-3 text-sm font-medium transition", active ? "bg-[var(--color-primary-soft)] text-white" : "text-[var(--color-text-muted)] hover:bg-[var(--color-surface-muted)] hover:text-white")}><Icon className="h-4 w-4" />{item.label}</Link>;
        })}
      </nav>
      <div className="border-t border-[var(--color-border)] pt-4">
        <p className="truncate text-sm font-medium text-white">{displayName}</p>
        <p className="truncate text-xs text-[var(--color-text-muted)]">{user.profile?.role ?? "operator"}</p>
        <form action={logoutAction} className="mt-4"><Button variant="secondary" className="w-full justify-start"><LogOut className="h-4 w-4" />Sair</Button></form>
      </div>
    </aside>
  );
}
