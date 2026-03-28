import { state } from './state.js';
import { renderDashboard } from './modules/dashboard.js';
import { renderProducts } from './modules/products.js';
import { renderKits } from './modules/kits.js';
import { renderDescriptions } from './modules/descriptions.js';
import { renderReviews } from './modules/reviews.js';
import { renderSales } from './modules/sales.js';
import { renderShipping } from './modules/shipping.js';
import { renderSync } from './modules/sync.js';
import { renderSettings } from './modules/settings.js';

const routes = {
  dashboard: renderDashboard,
  products: renderProducts,
  kits: renderKits,
  descriptions: renderDescriptions,
  reviews: renderReviews,
  sales: renderSales,
  shipping: renderShipping,
  sync: renderSync,
  settings: renderSettings,
};

export async function navigate() {
  const container = document.getElementById('content');
  const route = location.hash.replace('#', '') || 'dashboard';
  state.currentRoute = routes[route] ? route : 'dashboard';
  await routes[state.currentRoute](container);
}
