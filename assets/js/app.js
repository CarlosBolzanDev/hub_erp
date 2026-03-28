import { setTheme } from './state.js';
import { navigate } from './router.js';
import { renderSidebar } from './components/sidebar.js';
import { renderHeader } from './components/header.js';

function wireGlobalEvents() {
  window.addEventListener('hashchange', async () => {
    renderSidebar();
    await navigate();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === '/') {
      e.preventDefault();
      document.getElementById('global-search')?.focus();
    }
  });
}

async function bootstrap() {
  setTheme(localStorage.getItem('hub_theme') || 'dark');
  renderSidebar();
  renderHeader();
  wireGlobalEvents();
  await navigate();
}

bootstrap();
