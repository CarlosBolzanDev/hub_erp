import { reviewService } from '../services/reviewService.js';
import { renderTable } from '../components/table.js';
import { openModal } from '../components/modal.js';

export async function renderReviews(container) {
  const reviews = await reviewService.list();
  const avg = (reviews.reduce((s, r) => s + r.rating, 0) / reviews.length).toFixed(1);
  container.innerHTML = `<div class="stack"><h2>Reviews</h2><div class="card">Média: <strong>${avg}</strong></div><div id="reviews-table"></div></div>`;
  container.querySelector('#reviews-table').innerHTML = renderTable({
    columns: [{ key: 'id', label: 'ID' }, { key: 'rating', label: 'Nota' }, { key: 'date', label: 'Data' }, { key: 'comment', label: 'Comentário' }],
    rows: reviews,
    rowActions: (r) => `<button class="btn" data-detail="${r.id}">Detalhes</button>`,
  });
  container.onclick = (e) => {
    const id = e.target.dataset.detail;
    if (!id) return;
    const r = reviews.find((x) => String(x.id) === String(id));
    openModal({ title: `Review #${id}`, body: `<p>Nota: ${r.rating}</p><p>${r.comment}</p>` });
  };
}
