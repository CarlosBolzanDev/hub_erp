import { pretty } from '../utils.js';

export function renderTable({ columns, rows, actions }) {
  const table = document.createElement('table');
  table.className = 'data-table';
  table.innerHTML = `
    <thead><tr>${columns.map((c) => `<th>${c}</th>`).join('')}<th>Ações</th></tr></thead>
    <tbody>
      ${rows
        .map(
          (row) =>
            `<tr>${columns.map((c) => `<td>${pretty(row[c])}</td>`).join('')}<td>${actions(row)}</td></tr>`
        )
        .join('')}
    </tbody>
  `;
  return table;
}
