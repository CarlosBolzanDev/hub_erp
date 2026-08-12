import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { MetricCard } from "./MetricCard";

const metrics = [
  { label: "Pedidos", value: "0", description: "Total recebido na operação" },
  { label: "Pedidos hoje", value: "0", description: "Entradas registradas hoje" },
  { label: "Pedidos conferidos", value: "0", description: "Separações validadas" },
  { label: "Pedidos pendentes", value: "0", description: "Aguardando conferência" },
];

export function DashboardOverview() {
  return <div className="space-y-8"><section><Badge>Operação</Badge><h1 className="mt-4 text-4xl font-bold tracking-tight text-white">Bibly</h1><p className="mt-2 text-lg text-[var(--color-text-muted)]">Visão geral da operação</p></section><section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{metrics.map((metric) => <MetricCard key={metric.label} {...metric} />)}</section><Card><div className="flex items-center justify-between gap-4"><div><h2 className="text-xl font-semibold text-white">Atividade recente</h2><p className="mt-1 text-sm text-[var(--color-text-muted)]">Eventos operacionais aparecerão aqui conforme os módulos forem ativados.</p></div><Badge>Em breve</Badge></div><div className="mt-6 rounded-[var(--radius-md)] border border-dashed border-[var(--color-border)] p-8 text-center text-sm text-[var(--color-text-muted)]">Nenhuma atividade registrada nesta primeira versão.</div></Card></div>;
}
