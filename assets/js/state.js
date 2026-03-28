export const state = {
  theme: localStorage.getItem('hub_theme') || 'dark',
  currentRoute: 'dashboard',
  filters: {},
  selected: null,
  sync: { running: false, step: '', progress: 0 },
  preferences: JSON.parse(localStorage.getItem('hub_preferences') || '{"language":"pt-BR"}'),
};

export function setTheme(theme) {
  state.theme = theme;
  document.documentElement.dataset.theme = theme;
  localStorage.setItem('hub_theme', theme);
}

export function savePreferences(partial) {
  state.preferences = { ...state.preferences, ...partial };
  localStorage.setItem('hub_preferences', JSON.stringify(state.preferences));
}
