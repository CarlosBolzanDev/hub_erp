from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "database"
DB_PATH = DB_DIR / "registro_operacional.db"
ATTACHMENTS_DIR = DATA_DIR / "attachments"
PREVIEWS_DIR = DATA_DIR / "previews"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUPS_DIR = DATA_DIR / "backups"
LOGS_DIR = DATA_DIR / "logs"

for p in [DATA_DIR, DB_DIR, ATTACHMENTS_DIR, PREVIEWS_DIR, EXPORTS_DIR, BACKUPS_DIR, LOGS_DIR]:
    p.mkdir(parents=True, exist_ok=True)
