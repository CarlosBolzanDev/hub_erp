export function openModal({ title, body, footer = '' }) {
  const root = document.getElementById('modal-root');
  root.classList.remove('hidden');
  root.innerHTML = `
    <div class="modal">
      <div class="modal-header">
        <h3>${title}</h3>
        <button class="btn" data-close-modal>Fechar</button>
      </div>
      <div>${body}</div>
      <div class="modal-footer">${footer}</div>
    </div>
  `;
  root.querySelector('[data-close-modal]').onclick = closeModal;
}

export function closeModal() {
  const root = document.getElementById('modal-root');
  root.classList.add('hidden');
  root.innerHTML = '';
}
