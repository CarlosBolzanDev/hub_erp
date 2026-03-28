import { renderSidebar } from './components/sidebar.js';
import { renderHeader } from './components/header.js';
import { renderRoute } from './router.js';
import { setTheme, state } from './state.js';

const app = document.querySelector('#app');
app.innerHTML = `
  <aside id="sidebar"></aside>
  <section class="content-wrap">
    <header id="header"></header>
    <main id="main-content"></main>
  </section>
  <div id="modal-root"></div>
  <div id="toast-root"></div>
`;

renderSidebar(app.querySelector('#sidebar'));
renderHeader(app.querySelector('#header'));
setTheme(state.theme);

window.addEventListener('hashchange', () => renderRoute(app));
renderRoute(app);
