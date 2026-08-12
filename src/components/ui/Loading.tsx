import { Loader2 } from "lucide-react";

export function Loading({ label = "Carregando" }: { label?: string }) {
  return <span className="inline-flex items-center gap-2 text-sm text-[var(--color-text-muted)]"><Loader2 className="h-4 w-4 animate-spin" />{label}</span>;
}
