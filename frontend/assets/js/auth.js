import { apiRequest } from './api.js';

export async function requireSession() {
  if (!localStorage.getItem('accessToken')) {
    location.href = '../login.html';
    return null;
  }
  try { return await apiRequest('/api/auth/me'); }
  catch { return null; }
}

export function logout() {
  localStorage.removeItem('accessToken');
  location.href = '../login.html';
}
