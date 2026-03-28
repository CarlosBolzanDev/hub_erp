import { api } from '../api.js';

export async function syncModule() {
  const root = document.createElement('div');
  const logs = await api.syncLogs();
  root.innerHTML = `<h2>Sincronização</h2><button id="runSync">Rodar sync</button><pre id="logs">${JSON.stringify(logs.data, null, 2)}</pre>`;
  root.querySelector('#runSync').onclick = async () => {
    await api.runSync();
    const refreshed = await api.syncLogs();
    root.querySelector('#logs').textContent = JSON.stringify(refreshed.data, null, 2);
  };
  return root;
}
