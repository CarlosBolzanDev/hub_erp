export function toast(message, type = 'ok') {
  const root = document.getElementById('toast-root');
  const div = document.createElement('div');
  div.className = 'toast';
  div.style.borderColor = `var(--${type === 'error' ? 'danger' : type === 'warn' ? 'warn' : 'ok'})`;
  div.textContent = message;
  root.appendChild(div);
  setTimeout(() => div.remove(), 2200);
}
