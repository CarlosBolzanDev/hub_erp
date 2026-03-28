import { api } from '../api.js';
import { openModal } from '../components/modal.js';

export async function kitsModule() {
  const root = document.createElement('div');
  const rows = (await api.kits()).data;
  root.innerHTML = `<h2>Kits</h2><button id="newKit">Novo kit</button><pre>${JSON.stringify(rows, null, 2)}</pre>`;
  root.querySelector('#newKit').onclick = () => openModal('Novo kit', '<textarea id="payload" rows="8">{"name":"Kit Novo"}</textarea>', async (mr) => {
    await api.createKit(JSON.parse(mr.querySelector('#payload').value));
  });
  return root;
}
