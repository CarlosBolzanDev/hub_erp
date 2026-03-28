export function toast(message, kind = 'success') {
  const root = document.querySelector('#toast-root');
  const el = document.createElement('div');
  el.className = `toast ${kind}`;
  el.textContent = message;
  root.appendChild(el);
  setTimeout(() => el.remove(), 2500);
}
