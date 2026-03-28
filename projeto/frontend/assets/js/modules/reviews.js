import { api } from '../api.js';

export async function reviewsModule() {
  const root = document.createElement('div');
  const rows = (await api.reviews()).data;
  root.innerHTML = `<h2>Reviews</h2><pre>${JSON.stringify(rows.slice(0, 200), null, 2)}</pre>`;
  return root;
}
