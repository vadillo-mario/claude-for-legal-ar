"""Cliente para Infoleg (servicios.infoleg.gob.ar).

Infoleg es la base oficial de legislación nacional argentina, dependiente del
Ministerio de Justicia.

Esta implementación hace scraping del frontend público. No hay API JSON oficial
estable.

Endpoints relevantes:
- Búsqueda: https://servicios.infoleg.gob.ar/infolegInternet/verBusqueda.do
- Norma individual: https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=<id>
- Texto actualizado: https://servicios.infoleg.gob.ar/infolegInternet/anexos/<carpeta>/<id>/texact.htm
"""

import logging
from typing import Optional
from urllib.parse import urlencode

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://servicios.infoleg.gob.ar/infolegInternet"
USER_AGENT = (
    "Mozilla/5.0 (compatible; ar-legal-sources-mcp/0.1.0; "
    "https://github.com/MNVadillo/claude-for-legal-ar)"
)
TIMEOUT = 20.0


async def buscar(
    consulta: str,
    tipo_norma: str = "todos",
    limite: int = 10,
) -> str:
    """Buscar normas en Infoleg por palabra clave.

    Retorna un texto formateado con resultados.
    """
    if len(consulta.strip()) < 3:
        return "La consulta debe tener al menos 3 caracteres."

    # Mapeo de tipos a los códigos que usa Infoleg
    tipo_map = {
        "ley": "LEY",
        "decreto": "DEC",
        "resolucion": "RES",
        "todos": "",
    }
    tipo_codigo = tipo_map.get(tipo_norma, "")

    params = {
        "modo": "1",  # búsqueda por texto
        "texto": consulta,
    }
    if tipo_codigo:
        params["tipo"] = tipo_codigo

    url = f"{BASE_URL}/verBusqueda.do?{urlencode(params)}"
    logger.info(f"Infoleg búsqueda: {url}")

    async with httpx.AsyncClient(
        timeout=TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    resultados = _parsear_resultados_busqueda(response.text, limite=limite)

    if not resultados:
        return (
            f"Sin resultados en Infoleg para '{consulta}' "
            f"(tipo={tipo_norma}). Probá con términos más amplios o "
            "verificá la ortografía."
        )

    return _formatear_resultados(consulta, tipo_norma, resultados)


async def obtener_norma(id_infoleg: str) -> str:
    """Recuperar el texto completo de una norma específica."""
    url = f"{BASE_URL}/verNorma.do?id={id_infoleg}"
    logger.info(f"Infoleg norma: {url}")

    async with httpx.AsyncClient(
        timeout=TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    return _parsear_norma(response.text, id_infoleg)


def _parsear_resultados_busqueda(html: str, limite: int = 10) -> list[dict]:
    """Parsear el HTML de la página de resultados.

    El layout de Infoleg cambia; esta función debe mantenerse. La estructura
    típica es una tabla con filas que contienen tipo, número, título y link.
    """
    soup = BeautifulSoup(html, "lxml")
    resultados: list[dict] = []

    # Heurística: buscar tablas con resultados. Infoleg usa una tabla con
    # class "table" o similar; si cambia, esto necesita ajuste.
    filas = soup.select("table tr")

    for fila in filas:
        celdas = fila.find_all("td")
        if len(celdas) < 3:
            continue

        # Buscar el link a la norma
        link = fila.find("a", href=lambda h: h and "verNorma.do" in h)
        if not link:
            continue

        href = link.get("href", "")
        id_match = href.split("id=")[-1].split("&")[0] if "id=" in href else None

        titulo = link.get_text(strip=True)
        if not titulo:
            continue

        # Intentar extraer tipo y número de las celdas
        texto_fila = " ".join(c.get_text(strip=True) for c in celdas)

        resultados.append({
            "id_infoleg": id_match,
            "titulo": titulo,
            "contexto": texto_fila[:200],
            "url": (
                f"{BASE_URL}/verNorma.do?id={id_match}"
                if id_match else href
            ),
        })

        if len(resultados) >= limite:
            break

    return resultados


def _parsear_norma(html: str, id_infoleg: str) -> str:
    """Parsear la página de una norma individual y devolver texto formateado."""
    soup = BeautifulSoup(html, "lxml")

    # Título / encabezado
    titulo_tag = soup.find(["h1", "h2", "title"])
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Sin título"

    # Cuerpo principal — heurística
    cuerpo_tag = soup.find("div", class_="contenido") or soup.find("body")
    cuerpo = cuerpo_tag.get_text("\n", strip=True) if cuerpo_tag else ""

    # Truncar si es muy largo
    if len(cuerpo) > 10000:
        cuerpo = cuerpo[:10000] + "\n\n[... truncado — consultar URL para texto completo ...]"

    return (
        f"# {titulo}\n\n"
        f"**ID Infoleg:** {id_infoleg}\n"
        f"**URL:** {BASE_URL}/verNorma.do?id={id_infoleg}\n\n"
        f"---\n\n"
        f"{cuerpo}"
    )


def _formatear_resultados(consulta: str, tipo_norma: str, resultados: list[dict]) -> str:
    """Formatear los resultados de búsqueda para consumo del modelo."""
    lineas = [
        f"# Resultados Infoleg",
        f"",
        f"**Consulta:** {consulta}",
        f"**Filtro tipo:** {tipo_norma}",
        f"**Resultados:** {len(resultados)}",
        f"",
        f"---",
        f"",
    ]

    for i, r in enumerate(resultados, 1):
        lineas.append(f"## {i}. {r['titulo']}")
        if r.get("id_infoleg"):
            lineas.append(f"- **ID Infoleg:** `{r['id_infoleg']}`")
        lineas.append(f"- **URL:** {r['url']}")
        if r.get("contexto"):
            lineas.append(f"- **Contexto:** {r['contexto']}")
        lineas.append("")

    lineas.append(
        "_Para recuperar el texto completo de cualquier norma, usar "
        "`infoleg_obtener_norma` con el ID correspondiente._"
    )

    return "\n".join(lineas)
