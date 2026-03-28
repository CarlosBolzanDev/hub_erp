import { shippingService } from '../services/shippingService.js';
import { renderTable } from '../components/table.js';
import { renderFilters } from '../components/filters.js';
import { openModal } from '../components/modal.js';
import { fmtMoney } from '../utils.js';

export async function renderShipping(container) {
  const quotes = await shippingService.list();
  container.innerHTML = `<div class="stack"><div class="row"><h2>Frete</h2><button class="btn" id="sim-frete">Simular cotação</button></div>${renderFilters([{ key:'cep', label:'Filtrar CEP' }])}<div id="ship-table"></div></div>`;
  container.querySelector('#ship-table').innerHTML = renderTable({
    columns: [
      { key: 'productId', label: 'Produto' },
      { key: 'method', label: 'Método' },
      { key: 'logistics', label: 'Logística' },
      { key: 'cost', label: 'Custo', render: (q) => fmtMoney(q.cost) },
      { key: 'days', label: 'Prazo(dias)' },
    ],
    rows: quotes,
    rowActions: () => '<span class="text-muted">-</span>',
  });
  container.querySelector('#sim-frete').onclick = () => openModal({ title: 'Simular cotação', body: '<div class="form-grid"><div><label>CEP</label><input class="input" value="01310-100" /></div><div><label>Tipo</label><select><option>PAC</option><option>SEDEX</option></select></div></div>' });
}
