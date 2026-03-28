import { state } from './state.js';

async function request(path, options = {}) {
  const response = await fetch(`${state.apiBaseUrl}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const json = await response.json();
  if (!response.ok || !json.success) throw new Error(json.message || 'Erro na API');
  return json;
}

export const api = {
  health: () => request('/health'),
  products: (q = '') => request(`/products${q}`),
  product: (id) => request(`/products/${id}`),
  createProduct: (payload) => request('/products', { method: 'POST', body: JSON.stringify(payload) }),
  updateProduct: (id, payload) => request(`/products/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteProduct: (id) => request(`/products/${id}`, { method: 'DELETE' }),
  descriptions: () => request('/descriptions'),
  description: (id) => request(`/descriptions/${id}`),
  updateDescription: (id, payload) => request(`/descriptions/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  reviews: () => request('/reviews'),
  sales: () => request('/sales'),
  saleItems: (id) => request(`/sales/${id}/items`),
  kits: () => request('/kits'),
  createKit: (payload) => request('/kits', { method: 'POST', body: JSON.stringify(payload) }),
  updateKit: (id, payload) => request(`/kits/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteKit: (id) => request(`/kits/${id}`, { method: 'DELETE' }),
  shipping: () => request('/shipping-quotes'),
  syncLogs: () => request('/sync/logs'),
  runSync: () => request('/sync/run', { method: 'POST' }),
  settings: () => request('/settings'),
  updateSettings: (payload) => request('/settings', { method: 'PUT', body: JSON.stringify(payload) }),
};
