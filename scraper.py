import logging
import os
import random
import re
import time
from dataclasses import dataclass
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import DBConfig, get_engine
from models import Base, CatalogRecord

URL = os.getenv(
    "TARGET_URL",
    "https://tecfil-catalago.gruposofape.com.br/CatalogoTecfil/resultadoPorCategoria.xhtml?search-term=categoria-automoveis",
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("tecfil_scraper")


HEADER_TO_FIELD = {
    "montadora": "montadora",
    "modelo": "modelo",
    "motor": "motor",
    "ano de": "ano_de",
    "até": "ano_ate",
    "ate": "ano_ate",
    "descricao": "descricao",
    "descrição": "descricao",
    "combustível": "combustivel",
    "combustivel": "combustivel",
    "local ar cabine": "local_ar_cabine",
    "ar cabine": "ar_cabine",
    "ar cabine com carvão": "ar_cabine_com_carvao",
    "ar cabine com carvao": "ar_cabine_com_carvao",
    "ar 1": "ar_1",
    "ar 2": "ar_2",
    "lubrificante 1": "lubrificante_1",
    "lubrificante 2": "lubrificante_2",
    "combustível 1": "combustivel_1",
    "combustivel 1": "combustivel_1",
    "combustível 2": "combustivel_2",
    "combustivel 2": "combustivel_2",
    "câmbio automático": "cambio_automatico",
    "cambio automatico": "cambio_automatico",
    "sedimentador blindado": "sedimentador_blindado",
    "sedimentador com copo": "sedimentador_com_copo",
    "sedimentador sem copo": "sedimentador_sem_copo",
    "direção": "direcao",
    "direcao": "direcao",
    "transmissão": "transmissao",
    "transmissao": "transmissao",
    "outros": "outros",
    "outros 2": "outros_2",
    "outros 3": "outros_3",
}


@dataclass
class ScraperConfig:
    timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    delay_min: float = float(os.getenv("DELAY_MIN", "0.8"))
    delay_max: float = float(os.getenv("DELAY_MAX", "1.8"))


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned or None


def make_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=5, connect=5, read=5, backoff_factor=1.0, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        }
    )
    return session


def map_headers(table: BeautifulSoup) -> list[str | None]:
    headers = []
    for th in table.select("thead th"):
        key = normalize_text(th.get_text(" ", strip=True))
        key = key.lower() if key else ""
        headers.append(HEADER_TO_FIELD.get(key))
    return headers


def parse_table(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table")
    if not table:
        return []

    fields = map_headers(table)
    if not fields:
        return []

    rows: list[dict[str, Any]] = []
    for tr in table.select("tbody tr"):
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        data = {f: None for f in HEADER_TO_FIELD.values()}
        for idx, cell in enumerate(cells):
            if idx >= len(fields):
                break
            field = fields[idx]
            if not field:
                continue
            data[field] = normalize_text(cell.get_text(" ", strip=True))
        rows.append(data)
    return rows


def find_next_payload(soup: BeautifulSoup) -> tuple[str, dict[str, str]] | None:
    view_state_el = soup.select_one("input[name='javax.faces.ViewState']")
    form = soup.select_one("form")
    next_btn = soup.select_one("a[aria-label*='Próximo'], a[aria-label*='Prximo'], a[title*='Próximo'], a[title*='Prximo']")

    if not view_state_el or not form or not next_btn:
        return None

    view_state = view_state_el.get("value")
    form_id = form.get("id")
    next_id = next_btn.get("id")
    if not (view_state and form_id and next_id):
        return None

    payload = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": next_id,
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "@all",
        next_id: next_id,
        form_id: form_id,
        "javax.faces.ViewState": view_state,
    }
    action = form.get("action") or URL
    return action, payload


def scrape_catalog(config: ScraperConfig) -> list[dict[str, Any]]:
    logger.info("Iniciando scraping via requests")
    session = make_session()
    all_rows: list[dict[str, Any]] = []
    visited_signatures: set[str] = set()

    resp = session.get(URL, timeout=config.timeout)
    resp.raise_for_status()
    page_html = resp.text
    page = 1

    while True:
        rows = parse_table(page_html)
        signature = f"{len(rows)}:{hash(tuple(tuple(sorted((k, v) for k, v in row.items())) for row in rows[:3]))}"
        if signature in visited_signatures:
            logger.info("Assinatura repetida detectada, encerrando paginação")
            break
        visited_signatures.add(signature)

        logger.info("Página %s: %s registros", page, len(rows))
        all_rows.extend(rows)

        soup = BeautifulSoup(page_html, "html.parser")
        next_payload = find_next_payload(soup)
        if not next_payload:
            logger.info("Sem paginação detectada")
            break

        action, payload = next_payload
        try:
            nxt = session.post(action, data=payload, timeout=config.timeout)
            nxt.raise_for_status()
            if "<partial-response" in nxt.text and "<![CDATA[" in nxt.text:
                chunks = re.findall(r"<!\[CDATA\[(.*?)\]\]>", nxt.text, flags=re.S)
                page_html = "\n".join(chunks) if chunks else nxt.text
            else:
                page_html = nxt.text
        except Exception:
            logger.exception("Falha ao carregar próxima página")
            break

        page += 1
        time.sleep(random.uniform(config.delay_min, config.delay_max))

    return all_rows


def upsert_records(session: Session, records: list[dict[str, Any]]) -> int:
    if not records:
        return 0

    count = 0
    for row in records:
        row = {k: normalize_text(v) if isinstance(v, str) else v for k, v in row.items()}
        row["source_url"] = URL
        filters = {
            "montadora": row.get("montadora"),
            "modelo": row.get("modelo"),
            "motor": row.get("motor"),
            "ano_de": row.get("ano_de"),
            "ano_ate": row.get("ano_ate"),
            "descricao": row.get("descricao"),
            "combustivel": row.get("combustivel"),
            "local_ar_cabine": row.get("local_ar_cabine"),
        }
        existing = session.scalar(select(CatalogRecord).filter_by(**filters))
        if existing:
            for key, value in row.items():
                setattr(existing, key, value)
        else:
            session.add(CatalogRecord(**row))
        count += 1

    session.commit()
    return count


def main() -> None:
    config = ScraperConfig()
    engine = get_engine(DBConfig())
    Base.metadata.create_all(engine)
    logger.info("Tabela SQLite verificada/criada")

    records = scrape_catalog(config)
    if not records:
        logger.warning("Nenhum dado encontrado")
        return

    with Session(engine) as session:
        total = upsert_records(session, records)
    logger.info("Processamento finalizado. Registros processados: %s", total)


if __name__ == "__main__":
    main()
