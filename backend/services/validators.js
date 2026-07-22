const required = (v) => v !== undefined && v !== null && String(v).trim() !== '';
const emailOk = (v) => !v || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
const docOk = (v) => /^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$/.test(v || '') || /^\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}$/.test(v || '');
const dateOk = (v) => !v || !Number.isNaN(Date.parse(v));
const num = (v) => Number.isFinite(Number(v)) && Number(v) >= 0;
function validateProperty(body) {
  const errors = [];
  ['codigo_interno','tipo','finalidade','endereco','bairro','cidade','estado','cep','status','proprietario_nome','proprietario_cpf_cnpj'].forEach(f => { if (!required(body[f])) errors.push(`${f} é obrigatório`); });
  if (!docOk(body.proprietario_cpf_cnpj)) errors.push('CPF/CNPJ inválido');
  if (!emailOk(body.proprietario_email)) errors.push('E-mail inválido');
  ['area_total','area_construida','quartos','banheiros','vagas'].forEach(f => { if (body[f] !== undefined && body[f] !== '' && !num(body[f])) errors.push(`${f} deve ser numérico positivo`); });
  return errors;
}
function validateFinance(body) {
  const errors = [];
  ['valor_total','valor_entrada','valor_parcela','quantidade_parcelas','juros_correcao'].forEach(f => { if (body[f] !== undefined && !num(body[f])) errors.push(`${f} deve ser numérico positivo`); });
  if (body.quantidade_parcelas < 0) errors.push('Parcelas não podem ser negativas');
  if (!dateOk(body.data_inicio_contrato)) errors.push('Data de contrato inválida');
  if (body.dia_vencimento && (Number(body.dia_vencimento) < 1 || Number(body.dia_vencimento) > 31)) errors.push('Dia de vencimento inválido');
  return errors;
}
function validatePayment(body, saldo = Infinity) {
  const errors = [];
  ['data_pagamento','valor_pago','numero_parcela','forma_pagamento','situacao'].forEach(f => { if (!required(body[f])) errors.push(`${f} é obrigatório`); });
  if (!dateOk(body.data_pagamento)) errors.push('Data de pagamento inválida');
  if (!num(body.valor_pago) || Number(body.valor_pago) <= 0) errors.push('Valor pago deve ser positivo');
  if (!Number.isInteger(Number(body.numero_parcela)) || Number(body.numero_parcela) < 0) errors.push('Número da parcela inválido');
  if (Number(body.valor_pago) > saldo && !required(body.observacao)) errors.push('Pagamento maior que saldo exige observação');
  return errors;
}
module.exports = { validateProperty, validateFinance, validatePayment };
