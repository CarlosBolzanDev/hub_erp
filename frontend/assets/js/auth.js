function saveSession(data) { localStorage.setItem('hub_erp_token', data.access_token); localStorage.setItem('hub_erp_user', JSON.stringify(data.user)); }
function getSessionUser() { try { return JSON.parse(localStorage.getItem('hub_erp_user')); } catch { return null; } }
function clearSession() { localStorage.removeItem('hub_erp_token'); localStorage.removeItem('hub_erp_user'); }
async function requireAuth() { if (!localStorage.getItem('hub_erp_token')) { location.href = '/login.html'; return null; } try { const user = await apiRequest('/api/auth/me'); localStorage.setItem('hub_erp_user', JSON.stringify(user)); return user; } catch { clearSession(); location.href = '/login.html'; return null; } }
async function logout() { try { await apiRequest('/api/auth/logout', { method: 'POST' }); } catch { /* local logout is enough for a stateless JWT */ } clearSession(); location.href = '/login.html'; }
