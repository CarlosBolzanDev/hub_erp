export function openModal(title, bodyHtml, onConfirm) {
  const root = document.querySelector('#modal-root');
  root.innerHTML = `
    <div class="modal-backdrop">
      <div class="modal">
        <h3>${title}</h3>
        <div class="modal-body">${bodyHtml}</div>
        <div class="modal-actions">
          <button id="modalCancel">Cancelar</button>
          <button id="modalConfirm">Confirmar</button>
        </div>
      </div>
    </div>
  `;
  root.querySelector('#modalCancel').onclick = () => (root.innerHTML = '');
  root.querySelector('#modalConfirm').onclick = async () => {
    await onConfirm?.(root);
    root.innerHTML = '';
  };
}
