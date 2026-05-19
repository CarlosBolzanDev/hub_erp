from loguru import logger
from registro_operacional.app.config.settings import LOGS_DIR

logger.add(LOGS_DIR / "app.log", rotation="2 MB", retention=10)
