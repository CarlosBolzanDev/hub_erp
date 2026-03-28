import { api } from '../api.js';
import { openModal } from '../components/modal.js';

export async function descriptionsModule() {
  const root = document.createElement('div');
  const rows = (await api.descriptions()).data;
  root.innerHTML = `<h2>Descrições</h2><ul>${rows.slice(0, 50).map((r) => `<li><button data-id="${r.id || r.item_id}">Editar ${r.id || r.item_id}</button></li>`).join('')}</ul>`;
  root.querySelectorAll('button[data-id]').forEach((btn) => {
    btn.onclick = async () => {
      const d = await api.description(btn.dataset.id);
      openModal('Editar descrição', `<textarea id="payload" rows="10">${JSON.stringify(d.data, null, 2)}</textarea>`, async (mr) => {
        await api.updateDescription(btn.dataset.id, JSON.parse(mr.querySelector('#payload').value));
      });
    };
  });
  return root;
}
