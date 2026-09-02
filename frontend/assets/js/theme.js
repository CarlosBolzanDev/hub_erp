const storageKey = 'theme';
function resolvedTheme(choice) { return choice === 'system' ? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : choice; }
export function applyTheme(choice = localStorage.getItem(storageKey) || 'system') { document.documentElement.dataset.theme = resolvedTheme(choice); localStorage.setItem(storageKey, choice); }
export function initializeTheme() { applyTheme(); document.querySelector('#theme-toggle')?.addEventListener('click', () => applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark')); }
