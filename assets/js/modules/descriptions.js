import { productService } from '../services/productService.js';
import { openModal } from '../components/modal.js';
import { toast } from '../components/toast.js';

export async function renderDescriptions(container) {
  const products = await productService.list();
  container.innerHTML = `<div class="stack"><h2>Descrições</h2><div class="card stack">${products.slice(0,8).map((p)=>`<div class="row" style="justify-content:space-between"><div><strong>${p.name}</strong><p class="text-muted">${p.description}</p></div><div class="row"><button class="btn" data-copy="${p.id}">Copiar</button><button class="btn" data-edit="${p.id}">Editar</button></div></div>`).join('')}</div></div>`;
  container.onclick = (e) => {
    const copyId = e.target.dataset.copy;
    const editId = e.target.dataset.edit;
    if (copyId) {
      const p = products.find((x) => String(x.id) === String(copyId));
      navigator.clipboard?.writeText(p.description);
      toast('Descrição copiada');
    }
    if (editId) {
      const p = products.find((x) => String(x.id) === String(editId));
      openModal({ title: `Editar descrição - ${p.name}`, body: `<textarea class="input" rows="8">${p.description}</textarea>` });
    }
  };
}
