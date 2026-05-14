"""Cliente para el Boletín Oficial de la Provincia de Mendoza.

URL base: https://boletinoficial.mendoza.gov.ar

Esta implementación es un primer cut: el sitio del BO Mza no expone una API
JSON oficial. Se hace scraping del frontend público.

Notas:
- Algunas ediciones son PDF; el scraping debe contemplar ambas modalidades.
- El BO Mza no publica fines de semana ni feriados provinciales.
"""

import logging
from datetime import date, datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://boletinoficial.mendoza.gov.ar"
USER_AGENT = (
    "Mozilla/5.0 (compatible; ar-legal-sources-mcp/0.1.0; "
    "https://github.com/MNVadillo/claude-for-legal-ar)"
)
TIMEOUT = 20.0


async def publicaciones_recientes(
    fecha: Optional[str] = None,
    palabra_clave: Optional[str] = None,
) -> str:
    """Listar publicaciones del BO Mendoza."""
    target_date = _parsear_fecha(fecha)
    fecha_iso = target_date.strftime("%Y-%m-%d")

    # Endpoint conocido del sitio; ajustar si el sitio cambia su estructura.
    url = f"{BASE_URL}/ediciones?fecha={fecha_iso}"
    logger.info(f"BO Mendoza consulta: {url}")

    async with httpx.AsyncClient(
        timeout=TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return (
                    f"No se encontró edición del BO Mendoza para el {fecha_iso}. "
                    "Probá con otro día o verificá si fue feriado provincial."
                )
            raise

    items = _parsear_listado(response.text, limite=50)

    # Filtro por palabra clave si se solicitó
    if palabra_clave:
        clave = palabra_clave.lower()
        items = [
            i for i in items
            if clave in i["titulo"].lower() or clave in i.get("contexto", "").lower()
        ]

    if not items:
        return (
            f"Sin items en BO Mendoza para el {fecha_iso}"
            f"{f' con palabra clave {palabra_clave!r}' if palabra_clave else ''}."
            f" Verificar en {url}"
        )

    return _formatear_items(fecha_iso, palabra_clave, url, items)


def _parsear_fecha(fecha: Optional[str]) -> date:
    if not fecha:
        return date.today()
    try:
        return datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Fecha inválida: '{fecha}'. Formato esperado: YYYY-MM-DD.")


def _parsear_listado(html: str, limite: int = 50) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    items: list[dict] = []

    enlaces = (
        soup.select("a[href*='/edicion/']")
        or soup.select("a[href*='/publicacion/']")
        or soup.select("a.norma")
    )

    for enlace in enlaces:
        titulo = enlace.get_text(strip=True)
        href = enlace.get("href", "")
        if not titulo or not href:
            continue

        url_completa = href if href.startswith("http") else f"{BASE_URL}{href}"
        contenedor = enlace.find_parent("div") or enlace.find_parent("article")
        contexto = contenedor.get_text(" ", strip=True)[:300] if contenedor else ""

        items.append({
            "titulo": titulo,
            "url": url_completa,
            "contexto": contexto,
        })

        if len(items) >= limite:
            break

    return items


def _formatear_items(
    fecha_iso: str,
    palabra_clave: Optional[str],
    url_origen: str,
    items: list[dict],
) -> str:
    lineas = [
        f"# BO Mendoza — {fecha_iso}",
        f"",
        f"**Fuente:** {url_origen}",
    ]
    if palabra_clave:
        lineas.append(f"**Filtro palabra clave:** {palabra_clave}")
    lineas.extend([
        f"**Items:** {len(items)}",
        f"",
        f"---",
        f"",
    ])

    for i, item in enumerate(items, 1):
        lineas.append(f"## {i}. {item['titulo']}")
        lineas.append(f"- **URL:** {item['url']}")
        if item.get("contexto"):
            lineas.append(f"- **Contexto:** {item['contexto']}")
        lineas.append("")

    return "\n".join(lineas)
