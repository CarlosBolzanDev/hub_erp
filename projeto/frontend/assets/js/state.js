export const state = {
  theme: localStorage.getItem('theme') || 'light',
  route: 'dashboard',
  apiBaseUrl: localStorage.getItem('apiBaseUrl') || 'http://127.0.0.1:5000/api',
};

export function setTheme(theme) {
  state.theme = theme;
  localStorage.setItem('theme', theme);
  document.documentElement.setAttribute('data-theme', theme);
}

export function setRoute(route) {
  state.route = route;
}
