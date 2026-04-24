CREATE DATABASE IF NOT EXISTS tecfil_catalog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tecfil_catalog;

CREATE TABLE IF NOT EXISTS catalog_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    montadora VARCHAR(255) NULL,
    modelo VARCHAR(255) NULL,
    motor VARCHAR(255) NULL,
    ano_de VARCHAR(30) NULL,
    ano_ate VARCHAR(30) NULL,
    descricao TEXT NULL,
    combustivel VARCHAR(100) NULL,
    local_ar_cabine VARCHAR(255) NULL,
    ar_cabine VARCHAR(255) NULL,
    ar_cabine_com_carvao VARCHAR(255) NULL,
    ar_1 VARCHAR(255) NULL,
    ar_2 VARCHAR(255) NULL,
    lubrificante_1 VARCHAR(255) NULL,
    lubrificante_2 VARCHAR(255) NULL,
    combustivel_1 VARCHAR(255) NULL,
    combustivel_2 VARCHAR(255) NULL,
    cambio_automatico VARCHAR(255) NULL,
    sedimentador_blindado VARCHAR(255) NULL,
    sedimentador_com_copo VARCHAR(255) NULL,
    sedimentador_sem_copo VARCHAR(255) NULL,
    direcao VARCHAR(255) NULL,
    transmissao VARCHAR(255) NULL,
    outros VARCHAR(255) NULL,
    outros_2 VARCHAR(255) NULL,
    outros_3 VARCHAR(255) NULL,
    source_url TEXT NOT NULL,
    CONSTRAINT uq_catalog_record_core UNIQUE (
        montadora, modelo, motor, ano_de, ano_ate, descricao, combustivel, local_ar_cabine
    )
);
