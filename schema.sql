-- Schema SQLite local
CREATE TABLE IF NOT EXISTS catalog_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    montadora TEXT NULL,
    modelo TEXT NULL,
    motor TEXT NULL,
    ano_de TEXT NULL,
    ano_ate TEXT NULL,
    descricao TEXT NULL,
    combustivel TEXT NULL,
    local_ar_cabine TEXT NULL,
    ar_cabine TEXT NULL,
    ar_cabine_com_carvao TEXT NULL,
    ar_1 TEXT NULL,
    ar_2 TEXT NULL,
    lubrificante_1 TEXT NULL,
    lubrificante_2 TEXT NULL,
    combustivel_1 TEXT NULL,
    combustivel_2 TEXT NULL,
    cambio_automatico TEXT NULL,
    sedimentador_blindado TEXT NULL,
    sedimentador_com_copo TEXT NULL,
    sedimentador_sem_copo TEXT NULL,
    direcao TEXT NULL,
    transmissao TEXT NULL,
    outros TEXT NULL,
    outros_2 TEXT NULL,
    outros_3 TEXT NULL,
    source_url TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_catalog_record_core
ON catalog_records (
    montadora, modelo, motor, ano_de, ano_ate, descricao, combustivel, local_ar_cabine
);
