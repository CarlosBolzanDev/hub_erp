import { setTheme, state } from '../state.js';

export function renderHeader() {
  const el = document.getElementById('header');
  el.innerHTML = `
    <div class="row" style="flex:1">
      <input id="global-search" class="input" placeholder="Busca global (atalho /)" />
    </div>
    <div class="row">
      <button id="theme-toggle" class="btn">Tema: ${state.theme === 'dark' ? 'Escuro' : 'Claro'}</button>
      <div class="badge">Admin Local</div>
    </div>
  `;
  el.querySelector('#theme-toggle').onclick = () => {
    const next = state.theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    renderHeader();
  };
}
