export function initializeNavigation() {
  const sidebar = document.querySelector('#sidebar');
  const toggle = document.querySelector('#menu-toggle');
  toggle?.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.querySelectorAll('.nav a').forEach((link) => {
    link.addEventListener('click', () => sidebar.classList.remove('open'));
  });
}
