import { Card } from "@/components/ui/Card";

// Initial dashboard page prepared to receive metrics and feature shortcuts.
export default function HomePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">Dashboard</h1>
        <p className="mt-2 text-slate-600">Visão inicial preparada para os próximos módulos do sistema.</p>
      </div>

      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Módulo Itens em construção</h2>
        <p className="mt-2 text-sm text-slate-600">
          A arquitetura do módulo está pronta para autenticação, CRUD, logs e relatórios futuros.
        </p>
      </Card>
    </div>
  );
}
