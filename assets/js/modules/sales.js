import { salesService } from '../services/salesService.js';
import { renderTable } from '../components/table.js';
import { openModal } from '../components/modal.js';
import { fmtMoney } from '../utils.js';

export async function renderSales(container) {
  const sales = await salesService.list();
  container.innerHTML = `<div class="stack"><h2>Vendas</h2><div id="sales-table"></div></div>`;
  container.querySelector('#sales-table').innerHTML = renderTable({
    columns: [
      { key: 'id', label: 'Pedido' },
      { key: 'buyer', label: 'Comprador' },
      { key: 'paymentStatus', label: 'Pagamento' },
      { key: 'status', label: 'Status' },
      { key: 'total', label: 'Total', render: (s) => fmtMoney(s.total) },
    ],
    rows: sales,
    rowActions: (s) => `<button class="btn" data-sale="${s.id}">Detalhes</button>`,
  });
  container.onclick = (e) => {
    const id = e.target.dataset.sale;
    if (!id) return;
    const sale = sales.find((s) => s.id === id);
    openModal({ title: `Pedido ${id}`, body: `<div class="stack"><p>Comprador: ${sale.buyer}</p><p>Total: ${fmtMoney(sale.total)}</p><h4>Itens</h4><ul>${sale.items.map((i) => `<li>${i.name}</li>`).join('')}</ul></div>` });
  };
}
