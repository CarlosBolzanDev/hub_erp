import { requireSession, logout } from './auth.js';
import { initializeNavigation } from './navigation.js';
import { initializeTheme } from './theme.js';

initializeTheme();
initializeNavigation();
const user = await requireSession();
if (user) {
  document.querySelector('#current-user').textContent = user.name;
  document.querySelector('#logout-button')?.addEventListener('click', logout);
  document.dispatchEvent(new CustomEvent('session-ready', { detail: user }));
}
