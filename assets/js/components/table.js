export function renderTable({ columns, rows, rowActions = () => '' }) {
  const head = columns.map((c) => `<th>${c.label}</th>`).join('');
  const body = rows.map((r) => `
    <tr>
      ${columns.map((c) => `<td>${c.render ? c.render(r) : r[c.key] ?? '-'}</td>`).join('')}
      <td>${rowActions(r)}</td>
    </tr>`).join('');
  return `<div class="table-wrap"><table><thead><tr>${head}<th>Ações</th></tr></thead><tbody>${body}</tbody></table></div>`;
}
