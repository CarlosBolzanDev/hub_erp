import { Button } from "@/components/ui/Button";

// Fixed application sidebar with branding and reserved navigation actions.
export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-20 flex w-64 flex-col border-r border-slate-200 bg-white px-4 py-6 shadow-sm">
      <div className="mb-8">
        <span className="text-xl font-bold tracking-tight text-slate-950">Hub ERP</span>
        <p className="text-sm text-slate-500">Gestão integrada</p>
      </div>

      <nav aria-label="Navegação principal" className="space-y-2">
        <Button className="w-full justify-start" variant="ghost">
          Itens
        </Button>
      </nav>
    </aside>
  );
}
