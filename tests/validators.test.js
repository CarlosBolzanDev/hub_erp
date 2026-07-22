const test = require('node:test');
const assert = require('node:assert/strict');
const { validateProperty, validatePayment } = require('../backend/services/validators');

test('valida imóvel obrigatório e documento', () => {
  assert.equal(validateProperty({}).length > 0, true);
  const errors = validateProperty({ codigo_interno:'A1', tipo:'casa', finalidade:'venda', endereco:'Rua', bairro:'Centro', cidade:'SP', estado:'SP', cep:'00000-000', status:'disponível', proprietario_nome:'Ana', proprietario_cpf_cnpj:'123.456.789-09', proprietario_email:'ana@site.com' });
  assert.deepEqual(errors, []);
});

test('pagamento maior que saldo exige observação', () => {
  assert.match(validatePayment({ data_pagamento:'2026-01-01', valor_pago:200, numero_parcela:1, forma_pagamento:'pix', situacao:'pago' }, 100).join(' '), /exige observação/);
});
