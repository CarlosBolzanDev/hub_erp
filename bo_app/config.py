from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "bo.db"
ATTACHMENTS_DIR = DATA_DIR / "attachments"
PREVIEWS_DIR = DATA_DIR / "previews"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUPS_DIR = DATA_DIR / "backups"

for p in [DATA_DIR, ATTACHMENTS_DIR, PREVIEWS_DIR, EXPORTS_DIR, BACKUPS_DIR]:
    p.mkdir(parents=True, exist_ok=True)
