import { api } from '../api.js';

export async function dashboardModule() {
  const root = document.createElement('div');
  root.innerHTML = '<p>Carregando dashboard...</p>';
  try {
    const [health, products, reviews, sales] = await Promise.all([
      api.health(),
      api.products('?per_page=1'),
      api.reviews(),
      api.sales(),
    ]);
    root.innerHTML = `
      <section class="cards-grid">
        <article class="card"><h4>Status Banco</h4><p>${health.data.database}</p></article>
        <article class="card"><h4>Total Produtos</h4><p>${products.meta?.total ?? products.data.length}</p></article>
        <article class="card"><h4>Total Reviews</h4><p>${reviews.data.length}</p></article>
        <article class="card"><h4>Total Vendas</h4><p>${sales.data.length}</p></article>
      </section>
    `;
  } catch (e) {
    root.innerHTML = `<p class="error">${e.message}</p>`;
  }
  return root;
}
