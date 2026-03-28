import { navigate } from '../router.js';

const links = ['dashboard', 'products', 'descriptions', 'kits', 'reviews', 'sales', 'shipping', 'sync', 'settings'];

export function renderSidebar(root) {
  root.innerHTML = `<div class="brand">Invex</div><nav>${links
    .map((l) => `<button data-route="${l}">${l}</button>`)
    .join('')}</nav>`;
  root.querySelectorAll('button').forEach((btn) =>
    btn.addEventListener('click', () => navigate(btn.dataset.route))
  );
}
