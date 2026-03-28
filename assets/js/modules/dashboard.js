import { productService } from '../services/productService.js';
import { kitService } from '../services/kitService.js';
import { reviewService } from '../services/reviewService.js';
import { salesService } from '../services/salesService.js';
import { shippingService } from '../services/shippingService.js';

export async function renderDashboard(container) {
  const [products, kits, reviews, sales, shipping] = await Promise.all([
    productService.list(), kitService.list(), reviewService.list(), salesService.list(), shippingService.list(),
  ]);
  container.innerHTML = `
    <div class="stack">
      <h2>Dashboard</h2>
      <div class="kpi-grid">
        <div class="kpi-card"><div class="text-muted">Produtos</div><div class="kpi">${products.length}</div></div>
        <div class="kpi-card"><div class="text-muted">Kits</div><div class="kpi">${kits.length}</div></div>
        <div class="kpi-card"><div class="text-muted">Vendas</div><div class="kpi">${sales.length}</div></div>
        <div class="kpi-card"><div class="text-muted">Reviews</div><div class="kpi">${reviews.length}</div></div>
        <div class="kpi-card"><div class="text-muted">Fretes</div><div class="kpi">${shipping.length}</div></div>
        <div class="kpi-card"><div class="text-muted">Ativos</div><div class="kpi">${products.filter(p=>p.status==='active').length}</div></div>
      </div>
      <div class="grid-2">
        <div class="card">
          <h3>Resumo de sincronização</h3>
          <p class="text-muted">Última execução simulada sem erros.</p>
          <div class="progress"><span style="width:100%"></span></div>
        </div>
        <div class="card">
          <h3>Atalhos rápidos</h3>
          <div class="row">
            <a class="btn" href="#products">Novo Produto</a>
            <a class="btn" href="#kits">Novo Kit</a>
            <a class="btn" href="#sync">Sincronizar Agora</a>
          </div>
        </div>
      </div>
    </div>`;
}
