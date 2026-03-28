export function buildSearchFilter(placeholder = 'Buscar...') {
  const wrap = document.createElement('div');
  wrap.className = 'filters';
  wrap.innerHTML = `<input type="search" placeholder="${placeholder}"/>`;
  return wrap;
}
