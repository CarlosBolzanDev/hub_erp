-- Kit merge layer tables (keeping catalog_record untouched).
-- Note: adjust `catalog_record` table name if your legacy table uses a different name.

CREATE TABLE IF NOT EXISTS kit_family (
  id INTEGER PRIMARY KEY,
  montadora TEXT NULL,
  ar_1 TEXT NULL,
  ar_2 TEXT NULL,
  lubrificante_1 TEXT NULL,
  lubrificante_2 TEXT NULL,
  combustivel_1 TEXT NULL,
  family_key TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kit_variant (
  id INTEGER PRIMARY KEY,
  kit_family_id INTEGER NOT NULL,
  combustivel_2 TEXT NULL,
  variant_key TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (kit_family_id) REFERENCES kit_family(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS kit_application (
  id INTEGER PRIMARY KEY,
  catalog_record_id INTEGER NOT NULL UNIQUE,
  kit_variant_id INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (catalog_record_id) REFERENCES catalog_record(id) ON DELETE CASCADE,
  FOREIGN KEY (kit_variant_id) REFERENCES kit_variant(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_kit_family_family_key ON kit_family (family_key);
CREATE INDEX IF NOT EXISTS ix_kit_variant_variant_key ON kit_variant (variant_key);
CREATE INDEX IF NOT EXISTS ix_kit_variant_kit_family_id ON kit_variant (kit_family_id);
CREATE INDEX IF NOT EXISTS ix_kit_application_catalog_record_id ON kit_application (catalog_record_id);
