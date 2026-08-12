"use client";

import { Menu } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function Header({ onOpenMenu }: { onOpenMenu: () => void }) {
  return <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-[var(--color-border)] bg-[var(--color-background)]/80 px-4 backdrop-blur lg:hidden"><strong>Bibly</strong><Button type="button" variant="ghost" onClick={onOpenMenu} aria-label="Abrir menu"><Menu className="h-5 w-5" /></Button></header>;
}
