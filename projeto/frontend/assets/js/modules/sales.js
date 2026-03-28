import { api } from '../api.js';

export async function salesModule() {
  const root = document.createElement('div');
  const sales = (await api.sales()).data;
  root.innerHTML = `<h2>Vendas</h2><ul>${sales.slice(0, 100).map((s) => `<li><button data-id="${s.id || s.sale_id || s.order_id}">${s.id || s.sale_id || s.order_id}</button></li>`).join('')}</ul><pre id="items"></pre>`;
  root.querySelectorAll('button[data-id]').forEach((btn) => {
    btn.onclick = async () => {
      const items = await api.saleItems(btn.dataset.id);
      root.querySelector('#items').textContent = JSON.stringify(items.data, null, 2);
    };
  });
  return root;
}
