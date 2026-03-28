import { api } from '../api.js';

export async function shippingModule() {
  const root = document.createElement('div');
  root.innerHTML = `<h2>Frete</h2><pre>${JSON.stringify((await api.shipping()).data, null, 2)}</pre>`;
  return root;
}
