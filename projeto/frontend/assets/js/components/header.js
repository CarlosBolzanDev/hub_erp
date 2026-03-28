import { setTheme, state } from '../state.js';

export function renderHeader(root) {
  root.innerHTML = `
    <div class="header-title">Dashboard SQLite</div>
    <div class="header-actions">
      <input id="globalSearch" placeholder="Busca global" />
      <button id="themeToggle">Tema</button>
    </div>
  `;
  root.querySelector('#themeToggle').addEventListener('click', () => {
    setTheme(state.theme === 'light' ? 'dark' : 'light');
  });
}
