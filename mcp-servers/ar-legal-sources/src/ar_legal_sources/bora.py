"""Cliente para el Boletín Oficial de la República Argentina (BORA).

URL base: https://www.boletinoficial.gob.ar

El BORA publica diariamente leyes, decretos, resoluciones y avisos en tres
secciones:
- Primera: Legislación y Avisos Oficiales (decretos, resoluciones, leyes)
- Segunda: Sociedades, sucesorias, edictos judiciales
- Tercera: Contrataciones (licitaciones)

Esta implementación consulta la portada del día buscado.

Para producción se recomienda:
- Cachear el HTML de cada día
- Implementar paginación si la primera sección tiene mucho contenido
- Considerar el formato PDF como fuente más estable que el HTML
"""

import logging
from datetime import date, datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.boletinoficial.gob.ar"
USER_AGENT = (
    "Mozilla/5.0 (compatible; ar-legal-sources-mcp/0.1.0; "
    "https://github.com/MNVadillo/claude-for-legal-ar)"
)
TIMEOUT = 20.0


async def publicaciones_recientes(
    fecha: Optional[str] = None,
    seccion: str = "primera",
) -> str:
    """Listar publicaciones del BORA en una fecha dada."""
    target_date = _parsear_fecha(fecha)
    fecha_str = target_date.strftime("%d-%m-%Y")
    fecha_iso = target_date.strftime("%Y-%m-%d")

    # URL de la portada por fecha (estructura conocida del sitio)
    url = f"{BASE_URL}/edicion/{seccion}/{fecha_str}"
    logger.info(f"BORA consulta: {url}")

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
                    f"No se encontró edición del BORA para el {fecha_iso} "
                    f"(sección {seccion}). Probá con otro día — el Boletín "
                    "no se publica fines de semana ni feriados."
                )
            raise

    items = _parsear_portada(response.text, limite=50)

    if not items:
        return (
            f"Edición del BORA para el {fecha_iso} sección {seccion} sin "
            "items detectables. Puede que el layout haya cambiado — verificá "
            f"manualmente en {url}"
        )

    return _formatear_items(fecha_iso, seccion, url, items)


def _parsear_fecha(fecha: Optional[str]) -> date:
    """Parsear la fecha o usar hoy."""
    if not fecha:
        return date.today()
    try:
        return datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(
            f"Fecha inválida: '{fecha}'. Formato esperado: YYYY-MM-DD."
        )


def _parsear_portada(html: str, limite: int = 50) -> list[dict]:
    """Extraer items de la portada del BORA.

    Heurística: los items suelen estar en divs con clase 'item' o similar,
    cada uno con un título (norma + número + organismo) y un detalle.
    """
    soup = BeautifulSoup(html, "lxml")
    items: list[dict] = []

    # Heurística: buscar enlaces a detalle de norma
    enlaces = soup.select("a[href*='/detalleAviso/']") or soup.select("a[href*='/norma/']")

    for enlace in enlaces:
        titulo = enlace.get_text(strip=True)
        href = enlace.get("href", "")

        if not titulo or not href:
            continue

        url_completa = href if href.startswith("http") else f"{BASE_URL}{href}"

        # Intentar capturar el contexto cercano (organismo, número)
        contenedor = enlace.find_parent("div") or enlace.find_parent("article")
        contexto = ""
        if contenedor:
            contexto_texto = contenedor.get_text(" ", strip=True)
            contexto = contexto_texto[:300]

        items.append({
            "titulo": titulo,
            "url": url_completa,
            "contexto": contexto,
        })

        if len(items) >= limite:
            break

    return items


def _formatear_items(fecha_iso: str, seccion: str, url_origen: str, items: list[dict]) -> str:
    """Formatear los items para consumo del modelo."""
    lineas = [
        f"# BORA — {fecha_iso} (Sección {seccion})",
        f"",
        f"**Fuente:** {url_origen}",
        f"**Items detectados:** {len(items)}",
        f"",
        f"---",
        f"",
    ]

    for i, item in enumerate(items, 1):
        lineas.append(f"## {i}. {item['titulo']}")
        lineas.append(f"- **URL:** {item['url']}")
        if item.get("contexto"):
            lineas.append(f"- **Contexto:** {item['contexto']}")
        lineas.append("")

    return "\n".join(lineas)
