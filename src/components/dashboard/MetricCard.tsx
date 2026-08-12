import { Card } from "@/components/ui/Card";

export function MetricCard({ label, value, description }: { label: string; value: string; description: string }) {
  return <Card><p className="text-sm text-[var(--color-text-muted)]">{label}</p><strong className="mt-3 block text-3xl text-white">{value}</strong><p className="mt-2 text-sm text-[var(--color-text-subtle)]">{description}</p></Card>;
}
