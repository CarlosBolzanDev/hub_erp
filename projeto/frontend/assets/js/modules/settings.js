import { api } from '../api.js';
import { setTheme, state } from '../state.js';

export async function settingsModule() {
  const root = document.createElement('div');
  const settings = await api.settings();
  root.innerHTML = `
    <h2>Configurações</h2>
    <label>API Base URL <input id="apiUrl" value="${state.apiBaseUrl}"/></label>
    <button id="saveUrl">Salvar URL</button>
    <button id="toggleTheme">Alternar tema</button>
    <pre>${JSON.stringify(settings.data, null, 2)}</pre>
  `;
  root.querySelector('#saveUrl').onclick = () => {
    localStorage.setItem('apiBaseUrl', root.querySelector('#apiUrl').value);
    location.reload();
  };
  root.querySelector('#toggleTheme').onclick = () => setTheme(state.theme === 'light' ? 'dark' : 'light');
  return root;
}
