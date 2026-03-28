import { kitService } from '../services/kitService.js';
import { productService } from '../services/productService.js';
import { renderTable } from '../components/table.js';
import { openModal, closeModal } from '../components/modal.js';
import { toast } from '../components/toast.js';
import { uid } from '../utils.js';

export async function renderKits(container) {
  const [kits, products] = await Promise.all([kitService.list(), productService.list()]);
  container.innerHTML = `<div class="stack"><div class="row"><h2>Kits</h2><button class="btn primary" id="new-kit">Novo Kit</button></div><div id="kits-table"></div></div>`;
  container.querySelector('#kits-table').innerHTML = renderTable({
    columns: [{ key: 'id', label: 'ID' }, { key: 'name', label: 'Nome' }, { key: 'items', label: 'Itens', render: (k) => k.items.length }],
    rows: kits,
    rowActions: (k) => `<button class="btn" data-view="${k.id}">Composição</button><button class="btn danger" data-del="${k.id}">Excluir</button>`,
  });

  container.querySelector('#new-kit').onclick = () => {
    openModal({
      title: 'Criar Kit',
      body: `<div class="form-group"><label>Nome do kit</label><input id="kit-name" class="input" /></div><div class="form-group"><label>Produtos (IDs separados por vírgula)</label><input id="kit-items" class="input" placeholder="1000,1001"></div>`,
      footer: '<button class="btn" data-close-modal>Cancelar</button><button class="btn primary" id="save-kit">Salvar</button>',
    });
    document.getElementById('save-kit').onclick = async () => {
      const ids = document.getElementById('kit-items').value.split(',').map((x) => +x.trim());
      const payload = { id: uid(), name: document.getElementById('kit-name').value, items: products.filter((p) => ids.includes(p.id)) };
      await kitService.create(payload); closeModal(); toast('Kit criado'); renderKits(container);
    };
  };

  container.onclick = async (e) => {
    const id = e.target.dataset.view || e.target.dataset.del;
    if (!id) return;
    const kit = kits.find((k) => String(k.id) === String(id));
    if (e.target.dataset.view) openModal({ title: `Composição: ${kit.name}`, body: `<ul>${kit.items.map((i) => `<li>${i.name}</li>`).join('')}</ul>` });
    if (e.target.dataset.del) { await kitService.remove(id); toast('Kit removido'); renderKits(container); }
  };
}
