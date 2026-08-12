"use client";

import { useState, type ReactNode } from "react";
import { X } from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/Button";
import type { CurrentUser } from "@/types/auth";

export function AppShell({ user, children }: { user: CurrentUser; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text)]">
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex"><Sidebar user={user} /></div>
      {open ? <div className="fixed inset-0 z-40 lg:hidden"><button aria-label="Fechar menu" className="absolute inset-0 bg-black/60" onClick={() => setOpen(false)} /><div className="relative h-full w-72"><Sidebar user={user} onNavigate={() => setOpen(false)} /></div><Button type="button" variant="ghost" className="absolute right-4 top-4" onClick={() => setOpen(false)} aria-label="Fechar menu"><X className="h-5 w-5" /></Button></div> : null}
      <div className="lg:pl-72"><Header onOpenMenu={() => setOpen(true)} /><main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-10">{children}</main></div>
    </div>
  );
}
