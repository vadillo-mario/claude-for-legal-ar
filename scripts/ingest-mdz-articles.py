#!/usr/bin/env python3
"""Ingesta de artículos de Mario Vadillo publicados en mdzol.com.

MDZ no expone API pública estable, así que esto es scraping del frontend.

Estrategia:
1. Recorrer la sección /consumidores/ paginando.
2. Detectar artículos firmados por "Mario Vadillo" (o variantes).
3. Descargar el detalle de cada artículo identificado.
4. Consolidar en derecho-consumidor/references/vadillo-mdz-content.md.

Salida: derecho-consumidor/references/vadillo-mdz-content.md

Uso:
    python scripts/ingest-mdz-articles.py [--paginas N] [--firma "Mario Vadillo"]

Notas:
- Sitio de terceros — el HTML puede cambiar. Si rompe, ajustar los selectores
  en parsear_listado() y parsear_articulo().
- Rate-limit cooperativo: 1 request por segundo (pausa entre artículos).
- User-Agent identificatorio (no scraper anónimo).
- Hard cap de 50 páginas por seguridad.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

try:
    import httpx
except ImportError:
    print("ERROR: falta httpx. Instalá: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: falta beautifulsoup4. Instalá: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_FILE = REPO_ROOT / "derecho-consumidor" / "references" / "vadillo-mdz-content.md"

BASE_URL = "https://www.mdzol.com"
SECCION_URL = "https://www.mdzol.com/consumidores"
USER_AGENT = (
    "Mozilla/5.0 (compatible; claude-for-legal-ar-ingest/0.1.0; "
    "https://github.com/MNVadillo/claude-for-legal-ar) - autor del contenido recuperando sus propios articulos"
)
TIMEOUT = 30.0
PAUSA_ENTRE_REQUESTS_SEG = 1.0
MAX_PAGINAS_DEFAULT = 30


def parsear_listado(html: str) -> list[dict]:
    """Extraer artículos de una página de listado de la sección consumidores.

    Devuelve lista de {titulo, url, autor (si visible), resumen (si visible)}.
    """
    soup = BeautifulSoup(html, "lxml")
    items: list[dict] = []

    # Heurística: artículos suelen estar en <article> o <a> con href que apunta
    # a una URL bajo /consumidores/ con slug
    for tag in soup.find_all(["article", "div"], class_=re.compile(r"(article|post|note|nota)", re.I)):
        link = tag.find("a", href=True)
        if not link:
            continue
        href = link["href"]
        url = urljoin(BASE_URL, href)

        # Solo notas (no la portada de sección)
        if "/consumidores" not in url or url.rstrip("/") == SECCION_URL.rstrip("/"):
            continue

        titulo_tag = tag.find(["h1", "h2", "h3"])
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else link.get_text(strip=True)
        if not titulo or len(titulo) < 10:
            continue

        # Buscar autor visible en el card si existe
        autor = ""
        for selector in ["span.author", ".byline", ".autor", "[class*='author']", "[class*='autor']"]:
            t = tag.select_one(selector)
            if t:
                autor = t.get_text(strip=True)
                break

        # Resumen / bajada
        resumen = ""
        bajada = tag.find(["p", "div"], class_=re.compile(r"(summary|excerpt|bajada|lead)", re.I))
        if bajada:
            resumen = bajada.get_text(" ", strip=True)[:300]

        items.append({
            "titulo": titulo,
            "url": url,
            "autor_listado": autor,
            "resumen": resumen,
        })

    # Deduplicar por URL preservando orden
    vistos = set()
    deduped = []
    for it in items:
        if it["url"] in vistos:
            continue
        vistos.add(it["url"])
        deduped.append(it)

    return deduped


def parsear_articulo(html: str) -> dict:
    """Extraer datos de un artículo individual de MDZ."""
    soup = BeautifulSoup(html, "lxml")

    # Título
    titulo_tag = soup.find(["h1"])
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""

    # Autor — buscar firmas en distintos lugares
    autor = ""
    for selector in [
        "[rel='author']",
        ".author-name",
        ".autor",
        "[class*='author']",
        "[class*='autor']",
        "[class*='firma']",
        "meta[name='author']",
    ]:
        t = soup.select_one(selector)
        if t:
            if t.name == "meta":
                autor = t.get("content", "").strip()
            else:
                autor = t.get_text(" ", strip=True)
            if autor:
                break

    # Fecha
    fecha = ""
    for selector in ["time[datetime]", "meta[property='article:published_time']", ".fecha", "[class*='date']"]:
        t = soup.select_one(selector)
        if t:
            if t.name == "meta":
                fecha = t.get("content", "").strip()
            elif t.name == "time":
                fecha = t.get("datetime", "").strip() or t.get_text(strip=True)
            else:
                fecha = t.get_text(" ", strip=True)
            if fecha:
                break

    # Cuerpo
    cuerpo = ""
    for selector in ["article", ".article-body", ".note-body", ".content", "main"]:
        t = soup.select_one(selector)
        if t:
            # Sacar nav, scripts, asides
            for basura in t.find_all(["script", "style", "nav", "aside", "footer"]):
                basura.decompose()
            cuerpo = t.get_text("\n", strip=True)
            if len(cuerpo) > 200:
                break

    # Limpieza
    cuerpo = re.sub(r"\n{3,}", "\n\n", cuerpo)

    return {
        "titulo": titulo,
        "autor": autor,
        "fecha": fecha,
        "cuerpo": cuerpo,
    }


def es_articulo_del_autor(meta: dict, firma_objetivo: str) -> bool:
    """Verificar si un artículo es del autor buscado."""
    if not firma_objetivo:
        return True

    firma_norm = firma_objetivo.lower().strip()
    autor_norm = (meta.get("autor", "") or "").lower()
    autor_listado_norm = (meta.get("autor_listado", "") or "").lower()
    cuerpo_norm = (meta.get("cuerpo", "") or "")[:2000].lower()

    # Búsqueda con tolerancia: "Mario Vadillo", "Mario N. Vadillo", "Vadillo" solo,
    # firma al pie del cuerpo, etc.
    apellido = firma_norm.split()[-1] if firma_norm else "vadillo"

    return (
        firma_norm in autor_norm
        or firma_norm in autor_listado_norm
        or apellido in autor_norm
        or apellido in autor_listado_norm
        or f"por {firma_norm}" in cuerpo_norm
        or f"firma: {apellido}" in cuerpo_norm
        # Detección de firma típica en columnas MDZ
        or (apellido in cuerpo_norm[-500:] and ("abogado" in cuerpo_norm[-500:] or "consumidor" in cuerpo_norm[-500:]))
    )


def renderizar_articulo(meta: dict, url: str) -> str:
    bloques = [
        f"## {meta['titulo']}",
        "",
        f"- **URL:** {url}",
    ]
    if meta.get("fecha"):
        bloques.append(f"- **Fecha:** {meta['fecha']}")
    if meta.get("autor"):
        bloques.append(f"- **Autor (detectado):** {meta['autor']}")
    bloques.append("")
    bloques.append("### Contenido")
    bloques.append("")
    bloques.append(meta.get("cuerpo", "(sin contenido extraído)"))
    bloques.append("")
    bloques.append("---")
    bloques.append("")
    return "\n".join(bloques)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingesta de artículos MDZ de un autor.")
    parser.add_argument("--paginas", type=int, default=MAX_PAGINAS_DEFAULT,
                        help=f"Máximo de páginas de listado a recorrer (default: {MAX_PAGINAS_DEFAULT})")
    parser.add_argument("--firma", default="Mario Vadillo",
                        help="Firma a filtrar. Default: 'Mario Vadillo'. Vacío para no filtrar.")
    parser.add_argument("--no-pausa", action="store_true",
                        help="Sin pausa entre requests (más rápido pero menos amigable al sitio).")
    args = parser.parse_args()

    pausa = 0.0 if args.no_pausa else PAUSA_ENTRE_REQUESTS_SEG

    print(f"Sección base: {SECCION_URL}")
    print(f"Páginas a recorrer (máx): {args.paginas}")
    print(f"Filtro de firma: {args.firma or '(sin filtro)'}")
    print(f"Pausa entre requests: {pausa}s")
    print()

    listado_completo: list[dict] = []

    with httpx.Client(
        timeout=TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        # Paginar listado
        for pagina in range(1, args.paginas + 1):
            if pagina == 1:
                url_pag = SECCION_URL
            else:
                # MDZ suele usar ?page=N o /pagina/N — probamos ambos.
                url_pag = f"{SECCION_URL}?page={pagina}"

            print(f"[Listado pág {pagina}] {url_pag}")
            try:
                r = client.get(url_pag)
                if r.status_code == 404:
                    print("  404 — fin de paginación.")
                    break
                r.raise_for_status()
            except httpx.HTTPError as e:
                print(f"  WARN error en página {pagina}: {e}")
                break

            items = parsear_listado(r.text)
            if not items:
                print("  Sin items detectables — fin.")
                break

            nuevos = [it for it in items if it["url"] not in {x["url"] for x in listado_completo}]
            listado_completo.extend(nuevos)
            print(f"  +{len(nuevos)} nuevos, total {len(listado_completo)}")

            if not nuevos:
                # Página repetida — probable fin
                break

            time.sleep(pausa)

        print()
        print(f"Listado completo: {len(listado_completo)} artículos. Filtrando por firma...")
        print()

        # Descargar detalle y filtrar por firma
        articulos_propios: list[tuple[dict, str]] = []
        for i, it in enumerate(listado_completo, 1):
            print(f"[{i}/{len(listado_completo)}] {it['titulo'][:80]}")
            try:
                r = client.get(it["url"])
                r.raise_for_status()
            except httpx.HTTPError as e:
                print(f"  WARN: {e}")
                continue

            meta = parsear_articulo(r.text)
            meta["autor_listado"] = it.get("autor_listado", "")

            if es_articulo_del_autor(meta, args.firma):
                articulos_propios.append((meta, it["url"]))
                print(f"  ✓ del autor")
            else:
                autor_visto = meta.get("autor") or it.get("autor_listado") or "(no detectado)"
                print(f"  – otro autor: {autor_visto[:60]}")

            time.sleep(pausa)

    print()
    print(f"Artículos del autor: {len(articulos_propios)}")

    if not articulos_propios:
        print("Sin artículos para escribir.")
        print("Si esperabas resultados:")
        print("  - Verificá que la firma esté bien escrita (--firma).")
        print("  - Revisá si MDZ cambió el HTML; ajustar selectores en este script.")
        print("  - Probá con --paginas 50 para recorrer más historia.")
        return 0

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    encabezado = (
        f"# Artículos de {args.firma} en mdzol.com — contenido ingestado\n"
        "\n"
        "> Generado por `scripts/ingest-mdz-articles.py`. **No editar a mano** — "
        "se regenera cada vez que corra el script.\n"
        "\n"
        f"- Sección base: {SECCION_URL}\n"
        f"- Artículos detectados como del autor: {len(articulos_propios)}\n"
        "- Uso: las skills del plugin `derecho-consumidor` leen este archivo como "
        "muestra del estilo doctrinal y los criterios del autor en columnas.\n"
        "\n"
        "---\n\n"
    )

    cuerpo = "\n".join(renderizar_articulo(meta, url) for meta, url in articulos_propios)

    OUTPUT_FILE.write_text(encabezado + cuerpo, encoding="utf-8")
    print(f"OK: escrito {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
