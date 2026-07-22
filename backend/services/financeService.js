const db = require('../../database/db');
function recalc(imovelId) {
  const totalPago = db.prepare('SELECT COALESCE(SUM(valor_pago),0) total FROM pagamentos WHERE imovel_id=?').get(imovelId).total;
  const fin = db.prepare('SELECT * FROM financeiro_imovel WHERE imovel_id=?').get(imovelId);
  if (!fin) return null;
  const valorAberto = Math.max(Number(fin.valor_total) + Number(fin.juros_correcao || 0) - totalPago, 0);
  const percentual = fin.valor_total > 0 ? Math.min((totalPago / (Number(fin.valor_total) + Number(fin.juros_correcao || 0))) * 100, 100) : 0;
  db.prepare('UPDATE financeiro_imovel SET valor_pago=?, valor_aberto=?, percentual_quitado=?, updated_at=CURRENT_TIMESTAMP WHERE imovel_id=?').run(totalPago, valorAberto, percentual, imovelId);
  return db.prepare('SELECT * FROM financeiro_imovel WHERE imovel_id=?').get(imovelId);
}
function history(imovelId, tipo, descricao) {
  db.prepare('INSERT INTO historico_alteracoes (imovel_id,tipo_acao,descricao) VALUES (?,?,?)').run(imovelId, tipo, descricao);
}
module.exports = { recalc, history };
