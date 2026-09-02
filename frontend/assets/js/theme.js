const THEME_KEY = 'hub_erp_theme';
function applyTheme(theme) { document.documentElement.dataset.theme = theme; }
function initializeTheme() { const saved = localStorage.getItem(THEME_KEY); applyTheme(saved || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')); }
function toggleTheme() { const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; localStorage.setItem(THEME_KEY, theme); applyTheme(theme); }
