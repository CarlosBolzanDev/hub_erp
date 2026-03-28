export function renderFilters(fields = []) {
  return `<div class="row">${fields.map((f) =>
    f.type === 'select'
      ? `<select class="input" data-filter="${f.key}"><option value="">${f.label}</option>${f.options.map((o) => `<option value="${o}">${o}</option>`).join('')}</select>`
      : `<input class="input" data-filter="${f.key}" placeholder="${f.label}" />`
  ).join('')}</div>`;
}
