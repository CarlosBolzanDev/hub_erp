import { state } from '../state.js';
const items = [
  ['dashboard', '🏠', 'Dashboard'],
  ['products', '📦', 'Produtos'],
  ['kits', '🧩', 'Kits'],
  ['descriptions', '📝', 'Descrições'],
  ['reviews', '⭐', 'Reviews'],
  ['sales', '🛒', 'Vendas'],
  ['shipping', '🚚', 'Frete'],
  ['sync', '🔄', 'Sincronização'],
  ['settings', '⚙️', 'Configurações'],
];

export function renderSidebar() {
  const el = document.getElementById('sidebar');
  el.innerHTML = `
    <div class="sidebar-brand">Hub ERP</div>
    <nav class="menu">
      ${items.map(([route, icon, label]) => `<a href="#${route}" class="${state.currentRoute === route ? 'active' : ''}"><span>${icon}</span><span class="label">${label}</span></a>`).join('')}
    </nav>
  `;
}
