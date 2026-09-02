const API_BASE_URL = 'http://localhost:8000';
async function apiRequest(path, options = {}) {
  const token = localStorage.getItem('hub_erp_token');
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (response.status === 401) { localStorage.removeItem('hub_erp_token'); localStorage.removeItem('hub_erp_user'); }
  if (response.status === 204) return null;
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || 'Não foi possível concluir a solicitação.');
  return payload;
}
