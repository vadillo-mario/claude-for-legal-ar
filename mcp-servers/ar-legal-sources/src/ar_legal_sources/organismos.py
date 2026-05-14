"""Cliente para organismos administrativos y judiciales argentinos.

Este módulo unifica el acceso a fuentes que todavía no tienen MCP propio
maduro y no están en SAIJ ni Infoleg con buena cobertura:

- SCJM       — Suprema Corte de Justicia de Mendoza (jus.mendoza.gov.ar)
- CIJur      — Centro de Información Jurídica de Mendoza
- CSJN       — Corte Suprema de Justicia de la Nación (csjn.gov.ar)
- ATM        — Administración Tributaria Mendoza
- EPRE       — Ente Provincial Regulador Eléctrico (Mendoza)
- Irrigación — Departamento General de Irrigación (Mendoza)
- ARCA       — Agencia de Recaudación y Control Aduanero (ex AFIP)

Estrategia v0.1:
- Para cada organismo, definir base URL, ruta de búsqueda conocida (si existe),
  y selectores de parseo del HTML público.
- Si el organismo no expone búsqueda HTML utilizable, devolver la URL del sitio
  + recomendación al modelo de usar web_fetch directo.
- Cobertura realista: cada organismo es un trabajo aparte. Este módulo es el
  esqueleto unificador y un primer cut funcional para los más usados (SCJM y
  CIJur). Los demás devuelven URL builders + parsing best-effort.

Mejoras futuras (por organismo, en orden de prioridad):
1. SCJM: parsing de resultados de búsqueda de fallos.
2. CIJur: parsing de tesauro y fallos provinciales.
3. ATM: agenda de resoluciones generales.
4. EPRE: agenda de resoluciones y cuadros tarifarios.
5. Irrigación: agenda de resoluciones de Superintendencia.
6. ARCA: agenda de resoluciones generales (suceden mucho — alta prioridad).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (compatible; ar-legal-sources-mcp/0.1.0; "
    "https://github.com/MNVadillo/claude-for-legal-ar)"
)
TIMEOUT = 25.0


@dataclass
class OrganismoConfig:
    """Configuración de scraping para un organismo."""
    alias: str
    nombre: str
    base_url: str
    search_url_template: Optional[str] = None  # con {q} para consulta
    selector_resultados: str = "a[href]"
    descripcion: str = ""
    cobertura_v1: str = "URL + búsqueda básica"


ORGANISMOS: dict[str, OrganismoConfig] = {
    "scjm": OrganismoConfig(
        alias="scjm",
        nombre="Suprema Corte de Justicia de Mendoza",
        base_url="https://www2.jus.mendoza.gov.ar",
        search_url_template=(
            "https://www2.jus.mendoza.gov.ar/jurisprudencia/index.php?"
            "buscar=1&texto={q}"
        ),
        selector_resultados="a[href*='fallo']",
        descripcion=(
            "Jurisprudencia de la SCJM. Sala I (civil/comercial), Sala II "
            "(laboral/familia), Sala III (penal). Cobertura: fallos plenarios "
            "y precedentes destacados publicados online."
        ),
        cobertura_v1="Búsqueda por texto + listado de resultados",
    ),
    "cijur": OrganismoConfig(
        alias="cijur",
        nombre="Centro de Información Jurídica de Mendoza",
        base_url="https://cijur.jus.mendoza.gov.ar",
        search_url_template="https://cijur.jus.mendoza.gov.ar/buscar?q={q}",
        selector_resultados="a[href]",
        descripcion=(
            "Centro de información jurídica de Mendoza. Doctrina, "
            "jurisprudencia, normativa con anotaciones."
        ),
        cobertura_v1="URL del buscador + parseo de resultados básico",
    ),
    "csjn": OrganismoConfig(
        alias="csjn",
        nombre="Corte Suprema de Justicia de la Nación",
        base_url="https://www.csjn.gov.ar",
        search_url_template="https://sj.csjn.gov.ar/sj/busqueda.do?txtSearch={q}",
        descripcion="Jurisprudencia de la CSJN. Sistema de búsqueda oficial.",
        cobertura_v1="URL del buscador (recomendado complementar con SAIJ)",
    ),
    "atm": OrganismoConfig(
        alias="atm",
        nombre="Administración Tributaria de Mendoza",
        base_url="https://www.atm.mendoza.gov.ar",
        search_url_template=None,
        descripcion=(
            "Administración Tributaria de Mendoza. Resoluciones generales, "
            "cuadros tarifarios, agendas, calendarios fiscales."
        ),
        cobertura_v1="URL base + listado de novedades de la portada",
    ),
    "epre": OrganismoConfig(
        alias="epre",
        nombre="Ente Provincial Regulador Eléctrico (Mendoza)",
        base_url="https://www.epremendoza.gov.ar",
        search_url_template=None,
        descripcion=(
            "Ente regulador del servicio eléctrico en Mendoza. "
            "Resoluciones, cuadros tarifarios EDEMSA/EDESTE/EDESUR. "
            "Reglamento de servicio."
        ),
        cobertura_v1="URL base + portada de resoluciones",
    ),
    "irrigacion": OrganismoConfig(
        alias="irrigacion",
        nombre="Departamento General de Irrigación (Mendoza)",
        base_url="https://www.irrigacion.gov.ar",
        search_url_template=None,
        descripcion=(
            "DGI Mendoza — autoridad del agua. Resoluciones de "
            "Superintendencia, canon de riego, padrones."
        ),
        cobertura_v1="URL base + listado de resoluciones",
    ),
    "arca": OrganismoConfig(
        alias="arca",
        nombre="Agencia de Recaudación y Control Aduanero (ex AFIP)",
        base_url="https://www.arca.gob.ar",
        search_url_template="https://www.arca.gob.ar/normativa?q={q}",
        descripcion=(
            "Ex AFIP. Resoluciones generales, instrucciones, dictámenes. "
            "Renombrada ARCA por Decreto 953/2024."
        ),
        cobertura_v1="URL del buscador + listado de novedades",
    ),
}


async def listar_organismos() -> str:
    """Devolver el catálogo de organismos disponibles."""
    lineas = ["# Organismos disponibles", ""]
    for org in ORGANISMOS.values():
        lineas.extend([
            f"## {org.alias} — {org.nombre}",
            f"- **Sitio:** {org.base_url}",
            f"- **Descripción:** {org.descripcion}",
            f"- **Cobertura v0.1:** {org.cobertura_v1}",
            "",
        ])
    return "\n".join(lineas)


async def consultar_organismo(
    alias: str,
    consulta: Optional[str] = None,
    limite: int = 10,
) -> str:
    """Consultar un organismo específico.

    Si el organismo tiene URL de búsqueda configurada, la usa.
    Si no, devuelve la URL base + listado de novedades de la portada.
    """
    alias_norm = alias.lower().strip()
    if alias_norm not in ORGANISMOS:
        disponibles = ", ".join(ORGANISMOS.keys())
        return (
            f"Alias desconocido: '{alias}'. Disponibles: {disponibles}. "
            "Usá `listar_organismos_ar` para ver el catálogo completo."
        )

    org = ORGANISMOS[alias_norm]

    async with httpx.AsyncClient(
        timeout=TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        if consulta and org.search_url_template:
            url = org.search_url_template.format(q=consulta)
            try:
                response = await client.get(url)
                response.raise_for_status()
            except httpx.HTTPError as e:
                return (
                    f"Error consultando {org.nombre}: {e}\n\n"
                    f"URL intentada: {url}\n\n"
                    f"Sugerencia: abrir manualmente {org.base_url} y buscar desde ahí."
                )

            items = _parsear_resultados(
                response.text,
                org.base_url,
                org.selector_resultados,
                limite=limite,
            )
            return _formatear_resultados_busqueda(org, consulta, url, items)

        # Sin búsqueda — devolver portada
        try:
            response = await client.get(org.base_url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            return (
                f"Error accediendo a {org.nombre} ({org.base_url}): {e}\n"
                "Probablemente el sitio esté caído o haya cambiado de URL."
            )

        items = _extraer_novedades_portada(response.text, org.base_url, limite=limite)
        return _formatear_portada(org, items)


def _parsear_resultados(
    html: str,
    base_url: str,
    selector: str,
    limite: int = 10,
) -> list[dict]:
    """Parsear resultados de búsqueda con un selector dado."""
    from urllib.parse import urljoin

    soup = BeautifulSoup(html, "lxml")
    items: list[dict] = []
    vistos: set[str] = set()

    for tag in soup.select(selector):
        href = tag.get("href", "")
        titulo = tag.get_text(strip=True)
        if not href or not titulo or len(titulo) < 8:
            continue

        url_completa = urljoin(base_url, href)
        if url_completa in vistos:
            continue
        vistos.add(url_completa)

        # Contexto cercano
        contenedor = tag.find_parent(["div", "article", "li", "tr"])
        contexto = ""
        if contenedor:
            contexto = contenedor.get_text(" ", strip=True)[:250]

        items.append({"titulo": titulo, "url": url_completa, "contexto": contexto})

        if len(items) >= limite:
            break

    return items


def _extraer_novedades_portada(html: str, base_url: str, limite: int = 10) -> list[dict]:
    """Heurística genérica para extraer novedades de la portada de un organismo."""
    from urllib.parse import urljoin

    soup = BeautifulSoup(html, "lxml")
    items: list[dict] = []
    vistos: set[str] = set()

    # Buscar artículos / noticias / novedades
    candidatos = (
        soup.find_all(["article"])
        or soup.select("[class*='noticia']")
        or soup.select("[class*='novedad']")
        or soup.select("[class*='news']")
    )

    if not candidatos:
        # Fallback: títulos de la página con enlaces
        candidatos = soup.find_all(["h2", "h3"])

    for tag in candidatos:
        link = tag.find("a", href=True) if tag.name != "a" else tag
        if not link or not link.get("href"):
            continue

        href = link["href"]
        titulo = link.get_text(strip=True)
        if not titulo or len(titulo) < 10:
            continue

        url_completa = urljoin(base_url, href)
        if url_completa in vistos:
            continue
        vistos.add(url_completa)

        items.append({"titulo": titulo, "url": url_completa})

        if len(items) >= limite:
            break

    return items


def _formatear_resultados_busqueda(
    org: OrganismoConfig,
    consulta: str,
    url_busqueda: str,
    items: list[dict],
) -> str:
    if not items:
        return (
            f"# {org.nombre}\n\n"
            f"**Consulta:** {consulta}\n"
            f"**URL de búsqueda:** {url_busqueda}\n\n"
            "Sin resultados detectables (puede ser que el sitio cambió su HTML "
            "o que no haya coincidencias). Probá abrir la URL directamente o "
            "ajustar los términos de búsqueda."
        )

    lineas = [
        f"# Resultados — {org.nombre}",
        "",
        f"**Consulta:** {consulta}",
        f"**URL de búsqueda:** {url_busqueda}",
        f"**Resultados:** {len(items)}",
        "",
        "---",
        "",
    ]

    for i, item in enumerate(items, 1):
        lineas.append(f"## {i}. {item['titulo']}")
        lineas.append(f"- **URL:** {item['url']}")
        if item.get("contexto"):
            lineas.append(f"- **Contexto:** {item['contexto']}")
        lineas.append("")

    return "\n".join(lineas)


def _formatear_portada(org: OrganismoConfig, items: list[dict]) -> str:
    lineas = [
        f"# {org.nombre} — Novedades de portada",
        "",
        f"**URL:** {org.base_url}",
        f"**Items detectados:** {len(items)}",
        "",
        "---",
        "",
    ]

    if not items:
        lineas.append(
            "Sin items detectables en la portada. El sitio puede haber "
            "cambiado de layout. Para inspección manual usar la URL base."
        )
        return "\n".join(lineas)

    for i, item in enumerate(items, 1):
        lineas.append(f"## {i}. {item['titulo']}")
        lineas.append(f"- **URL:** {item['url']}")
        lineas.append("")

    return "\n".join(lineas)
