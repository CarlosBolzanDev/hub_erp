export function showLoader(text = 'Carregando...') {
  const el = document.getElementById('global-loader');
  el.classList.remove('hidden');
  el.innerHTML = `<div class="card"><strong>${text}</strong></div>`;
}

export function hideLoader() {
  const el = document.getElementById('global-loader');
  el.classList.add('hidden');
  el.innerHTML = '';
}
