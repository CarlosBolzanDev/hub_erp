import { productService } from '../services/productService.js';
import { renderTable } from '../components/table.js';
import { renderFilters } from '../components/filters.js';
import { openModal, closeModal } from '../components/modal.js';
import { toast } from '../components/toast.js';
import { fmtMoney } from '../utils.js';

function matches(p, q, status) {
  return (!q || `${p.name} ${p.sku} ${p.id}`.toLowerCase().includes(q.toLowerCase())) && (!status || p.status === status);
}

export async function renderProducts(container) {
  const products = await productService.list();
  let filtered = [...products];
  container.innerHTML = `<div class="stack"><h2>Produtos</h2>${renderFilters([
    { key: 'q', label: 'Buscar por nome, SKU, ID' },
    { key: 'status', label: 'Status', type: 'select', options: ['active', 'paused', 'draft'] },
  ])}<div id="products-table"></div></div>`;

  const draw = () => {
    container.querySelector('#products-table').innerHTML = renderTable({
      columns: [
        { key: 'id', label: 'ID' },
        { key: 'name', label: 'Nome' },
        { key: 'price', label: 'Preço', render: (r) => fmtMoney(r.price) },
        { key: 'stock', label: 'Estoque' },
        { key: 'status', label: 'Status', render: (r) => `<span class="badge ${r.status === 'active' ? 'ok' : r.status === 'paused' ? 'warn' : 'danger'}">${r.status}</span>` },
      ],
      rows: filtered,
      rowActions: (r) => `<div class="table-actions"><button class="btn" data-view="${r.id}">Detalhes</button><button class="btn" data-edit="${r.id}">Editar</button><button class="btn danger" data-del="${r.id}">Excluir</button></div>`,
    });
  };
  draw();

  container.querySelectorAll('[data-filter]').forEach((el) => el.addEventListener('input', () => {
    const q = container.querySelector('[data-filter="q"]').value;
    const status = container.querySelector('[data-filter="status"]').value;
    filtered = products.filter((p) => matches(p, q, status));
    draw();
  }));

  container.onclick = async (e) => {
    const id = e.target.dataset.view || e.target.dataset.edit || e.target.dataset.del;
    if (!id) return;
    const product = products.find((p) => String(p.id) === String(id));
    if (e.target.dataset.view) {
      openModal({ title: `Produto #${id}`, body: `<div class="stack"><p><strong>${product.name}</strong></p><p>${product.description}</p><p>Categoria: ${product.category}</p><p>Frete grátis: ${product.freeShipping ? 'Sim':'Não'}</p></div>` });
    }
    if (e.target.dataset.edit) {
      openModal({
        title: `Editar ${product.name}`,
        body: `<div class="form-grid"><div class="form-group"><label>Preço</label><input id="edit-price" class="input" value="${product.price}"></div><div class="form-group"><label>Estoque</label><input id="edit-stock" class="input" value="${product.stock}"></div></div>`,
        footer: '<button class="btn" data-close-modal>Cancelar</button><button class="btn primary" id="save-product">Salvar</button>',
      });
      document.getElementById('save-product').onclick = async () => {
        await productService.update(id, { price: +document.getElementById('edit-price').value, stock: +document.getElementById('edit-stock').value });
        closeModal(); toast('Produto atualizado com sucesso'); renderProducts(container);
      };
    }
    if (e.target.dataset.del) {
      openModal({ title: 'Confirma exclusão', body: `<p>Excluir ${product.name}?</p>`, footer: `<button class="btn" data-close-modal>Cancelar</button><button class="btn danger" id="confirm-del">Excluir</button>` });
      document.getElementById('confirm-del').onclick = async () => { await productService.remove(id); closeModal(); toast('Produto removido'); renderProducts(container); };
    }
  };
}
