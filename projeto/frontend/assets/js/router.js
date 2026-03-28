import { setRoute } from './state.js';
import { modules } from './modules/index.js';

export function navigate(route) {
  window.location.hash = route;
}

export async function renderRoute(root) {
  const route = (window.location.hash.replace('#', '') || 'dashboard');
  setRoute(route);
  const renderer = modules[route] || modules.dashboard;
  const content = await renderer();
  root.querySelector('#main-content').innerHTML = '';
  root.querySelector('#main-content').appendChild(content);
}
