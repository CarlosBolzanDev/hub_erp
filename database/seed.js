require('./init');
const db = require('./db');
const exists = db.prepare('SELECT COUNT(*) c FROM imoveis').get().c;
if (exists) { console.log('Seed ignorado: já existem imóveis.'); process.exit(0); }
const { history } = require('../backend/services/financeService');
const p = db.prepare('INSERT INTO proprietarios (nome,cpf_cnpj,telefone,email) VALUES (?,?,?,?)').run('Maria Silva','123.456.789-09','(11) 99999-0000','maria@example.com').lastInsertRowid;
const i = db.prepare(`INSERT INTO imoveis (codigo_interno,tipo,finalidade,endereco,bairro,cidade,estado,cep,area_total,area_construida,quartos,banheiros,vagas,descricao,status,proprietario_id,observacoes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).run('IMO-001','apartamento','venda','Rua Central, 100','Centro','São Paulo','SP','01000-000',90,72,2,2,1,'Apartamento pronto para venda.','disponível',p,'Cadastro inicial').lastInsertRowid;
db.prepare('INSERT INTO financeiro_imovel (imovel_id,valor_total,valor_entrada,valor_parcela,quantidade_parcelas,valor_aberto,data_inicio_contrato,dia_vencimento,forma_pagamento,juros_correcao,observacoes) VALUES (?,?,?,?,?,?,?,?,?,?,?)').run(i,450000,50000,4000,100,450000,'2026-01-10',10,'transferência',0,'Condição padrão');
history(i,'seed','Registro inicial de demonstração');
console.log('Seed concluído.');
