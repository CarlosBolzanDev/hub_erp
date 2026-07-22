PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS proprietarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  cpf_cnpj TEXT NOT NULL UNIQUE,
  telefone TEXT,
  email TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS imoveis (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo_interno TEXT NOT NULL UNIQUE,
  tipo TEXT NOT NULL CHECK(tipo IN ('casa','apartamento','terreno','sala comercial','chácara','outro')),
  finalidade TEXT NOT NULL CHECK(finalidade IN ('venda','aluguel','ambos')),
  endereco TEXT NOT NULL,
  bairro TEXT NOT NULL,
  cidade TEXT NOT NULL,
  estado TEXT NOT NULL,
  cep TEXT NOT NULL,
  area_total REAL DEFAULT 0,
  area_construida REAL DEFAULT 0,
  quartos INTEGER DEFAULT 0,
  banheiros INTEGER DEFAULT 0,
  vagas INTEGER DEFAULT 0,
  descricao TEXT,
  status TEXT NOT NULL CHECK(status IN ('disponível','reservado','vendido','alugado','indisponível')),
  proprietario_id INTEGER NOT NULL,
  observacoes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(proprietario_id) REFERENCES proprietarios(id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS financeiro_imovel (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  imovel_id INTEGER NOT NULL UNIQUE,
  valor_total REAL NOT NULL DEFAULT 0,
  valor_entrada REAL NOT NULL DEFAULT 0,
  valor_parcela REAL NOT NULL DEFAULT 0,
  quantidade_parcelas INTEGER NOT NULL DEFAULT 0,
  valor_pago REAL NOT NULL DEFAULT 0,
  valor_aberto REAL NOT NULL DEFAULT 0,
  data_inicio_contrato TEXT,
  dia_vencimento INTEGER CHECK(dia_vencimento BETWEEN 1 AND 31),
  forma_pagamento TEXT,
  juros_correcao REAL NOT NULL DEFAULT 0,
  observacoes TEXT,
  percentual_quitado REAL NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(imovel_id) REFERENCES imoveis(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS pagamentos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  imovel_id INTEGER NOT NULL,
  data_pagamento TEXT NOT NULL,
  valor_pago REAL NOT NULL,
  numero_parcela INTEGER NOT NULL,
  forma_pagamento TEXT NOT NULL,
  situacao TEXT NOT NULL CHECK(situacao IN ('pago','parcial','em atraso')),
  observacao TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(imovel_id) REFERENCES imoveis(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS historico_alteracoes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  imovel_id INTEGER,
  data_alteracao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  responsavel TEXT NOT NULL DEFAULT 'Sistema',
  tipo_acao TEXT NOT NULL,
  descricao TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(imovel_id) REFERENCES imoveis(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_imoveis_busca ON imoveis(codigo_interno,endereco,cidade,status,tipo,finalidade);
CREATE INDEX IF NOT EXISTS idx_pagamentos_imovel ON pagamentos(imovel_id,numero_parcela,data_pagamento);
