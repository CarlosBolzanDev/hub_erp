import { api } from '../api.js';
import { openModal } from '../components/modal.js';
import { renderTable } from '../components/table.js';
import { toast } from '../components/toast.js';

export async function productsModule() {
  const root = document.createElement('div');
  root.innerHTML = '<h2>Produtos</h2><div class="toolbar"><input id="search" placeholder="Buscar"/><button id="new">Novo</button></div><div id="table"></div>';

  async function load() {
    const search = root.querySelector('#search').value;
    const result = await api.products(`?search=${encodeURIComponent(search)}&per_page=50`);
    const rows = result.data;
    const cols = rows[0] ? Object.keys(rows[0]).slice(0, 6) : ['id'];
    const table = renderTable({
      columns: cols,
      rows,
      actions: (r) => `<button data-a="view">Ver</button><button data-a="edit">Editar</button><button data-a="del">Excluir</button>`,
    });
    table.querySelectorAll('tbody tr').forEach((tr, idx) => {
      tr.onclick = (e) => {
        const act = e.target?.dataset?.a;
        const item = rows[idx];
        const id = item.id || item.item_id || item.product_id;
        if (act === 'view') openModal('Detalhes', `<pre>${JSON.stringify(item, null, 2)}</pre>`);
        if (act === 'edit') openModal('Editar produto', `<textarea id="payload" rows="8">${JSON.stringify(item, null, 2)}</textarea>`, async (modalRoot) => {
          await api.updateProduct(id, JSON.parse(modalRoot.querySelector('#payload').value));
          toast('Produto atualizado');
          load();
        });
        if (act === 'del') openModal('Confirmar exclusão', '<p>Excluir este produto?</p>', async () => {
          await api.deleteProduct(id);
          toast('Produto excluído');
          load();
        });
      };
    });
    root.querySelector('#table').innerHTML = '';
    root.querySelector('#table').appendChild(table);
  }

  root.querySelector('#search').addEventListener('input', load);
  root.querySelector('#new').addEventListener('click', () => openModal('Novo produto', '<textarea id="payload" rows="8">{"title":"Novo Produto"}</textarea>', async (modalRoot) => {
    await api.createProduct(JSON.parse(modalRoot.querySelector('#payload').value));
    toast('Produto criado');
    load();
  }));
  await load();
  return root;
}
