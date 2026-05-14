#!/usr/bin/env python3
"""Ingesta de guías de mariovadillo.com.ar via WordPress REST API.

Descarga las guías publicadas (categorías bajo /guia/) y las consolida en un
markdown indexable que las skills del plugin derecho-consumidor leen.

Salida: derecho-consumidor/references/vadillo-guias-content.md

Uso:
    cp scripts/.env.example scripts/.env
    # editar scripts/.env con tus credenciales WordPress
    python scripts/ingest-vadillo-wordpress.py

Configuración (vía .env):
    WP_BASE_URL=https://mariovadillo.com.ar
    WP_USER=vadilloedit
    WP_APP_PASSWORD=Xxxx Xxxx Xxxx Xxxx Xxxx Xxxx
    WP_CATEGORY_SLUGS=autoplanes,bancos,danos,datos-personales,educacion,garantias,locaciones-alquileres,multas,salud,seguros,servicios-publicos,turismo

Notas:
- Usa Basic Auth con app password (NO la clave principal de WP).
- Pagina hasta agotar resultados (100 por página, hard cap 1000 por seguridad).
- Strip de HTML básico — para análisis semántico es suficiente.
- No commitear el archivo de salida; está en .gitignore.
"""

from __future__ import annotations

import base64
import html
import os
import re
import sys
from pathlib import Path
from typing import Iterable

try:
    import httpx
except ImportError:
    print(
        "ERROR: falta httpx. Instalá: pip install -r scripts/requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print(
        "ERROR: falta python-dotenv. Instalá: pip install -r scripts/requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
ENV_FILE = SCRIPT_DIR / ".env"
OUTPUT_FILE = REPO_ROOT / "derecho-consumidor" / "references" / "vadillo-guias-content.md"

# Hard cap por seguridad — si en algún momento llegan a haber más posts, ajustar.
MAX_POSTS = 1000
PER_PAGE = 100
TIMEOUT = 30.0


def cargar_config() -> dict[str, str]:
    """Cargar configuración desde .env."""
    if not ENV_FILE.exists():
        print(
            f"ERROR: no existe {ENV_FILE}. Copiá scripts/.env.example a "
            "scripts/.env y completá con tus credenciales.",
            file=sys.stderr,
        )
        sys.exit(1)

    load_dotenv(ENV_FILE)

    required = ["WP_BASE_URL", "WP_USER", "WP_APP_PASSWORD"]
    config = {}
    faltantes = []
    for key in required:
        valor = os.getenv(key, "").strip()
        if not valor:
            faltantes.append(key)
        config[key] = valor

    if faltantes:
        print(
            f"ERROR: faltan variables en .env: {', '.join(faltantes)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Categorías por slug (opcional — si vacío, traemos todo)
    slugs_raw = os.getenv("WP_CATEGORY_SLUGS", "").strip()
    config["WP_CATEGORY_SLUGS"] = slugs_raw

    # Normalizar base URL
    config["WP_BASE_URL"] = config["WP_BASE_URL"].rstrip("/")

    return config


def basic_auth_header(usuario: str, app_password: str) -> str:
    """Construir el header Authorization Basic para WP REST API."""
    raw = f"{usuario}:{app_password}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def resolver_categorias(
    client: httpx.Client,
    base_url: str,
    slugs_csv: str,
) -> list[int] | None:
    """Resolver slugs de categorías a IDs. Devuelve None si no se filtra."""
    slugs = [s.strip() for s in slugs_csv.split(",") if s.strip()]
    if not slugs:
        return None

    ids: list[int] = []
    for slug in slugs:
        url = f"{base_url}/wp-json/wp/v2/categories"
        r = client.get(url, params={"slug": slug, "per_page": 10})
        r.raise_for_status()
        data = r.json()
        if not data:
            print(f"  AVISO: categoría '{slug}' no encontrada, ignorando.")
            continue
        for cat in data:
            ids.append(cat["id"])
            print(f"  + categoría '{slug}' → id={cat['id']} ({cat.get('count', '?')} posts)")
    return ids or None


def fetch_posts(
    client: httpx.Client,
    base_url: str,
    category_ids: list[int] | None,
) -> Iterable[dict]:
    """Iterar todos los posts paginando."""
    page = 1
    total_recibidos = 0

    while total_recibidos < MAX_POSTS:
        params: dict[str, str | int] = {
            "per_page": PER_PAGE,
            "page": page,
            "_fields": "id,slug,title,link,date,modified,excerpt,content,categories",
            "orderby": "modified",
            "order": "desc",
        }
        if category_ids:
            params["categories"] = ",".join(str(i) for i in category_ids)

        url = f"{base_url}/wp-json/wp/v2/posts"
        r = client.get(url, params=params)

        # WP devuelve 400 cuando se pasa el rango de páginas — fin del listado.
        if r.status_code == 400:
            break

        r.raise_for_status()
        batch = r.json()
        if not batch:
            break

        for post in batch:
            yield post
            total_recibidos += 1
            if total_recibidos >= MAX_POSTS:
                break

        # Si esta página vino con menos del max, no hay más.
        if len(batch) < PER_PAGE:
            break

        page += 1


def strip_html(texto: str) -> str:
    """Limpieza básica de HTML. Suficiente para análisis semántico."""
    if not texto:
        return ""
    # Decode entidades HTML
    texto = html.unescape(texto)
    # Remover <script> y <style> con su contenido
    texto = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", texto, flags=re.DOTALL | re.IGNORECASE)
    # Convertir <br> y <p> en saltos de línea
    texto = re.sub(r"<br\s*/?>", "\n", texto, flags=re.IGNORECASE)
    texto = re.sub(r"</p>", "\n\n", texto, flags=re.IGNORECASE)
    # Strip resto de tags
    texto = re.sub(r"<[^>]+>", "", texto)
    # Colapsar espacios múltiples
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto.strip()


def renderizar_post(post: dict) -> str:
    """Convertir un post a markdown."""
    titulo = strip_html(post.get("title", {}).get("rendered", "(sin título)"))
    slug = post.get("slug", "")
    link = post.get("link", "")
    fecha = post.get("date", "")[:10]
    modificado = post.get("modified", "")[:10]
    excerpt = strip_html(post.get("excerpt", {}).get("rendered", ""))
    contenido = strip_html(post.get("content", {}).get("rendered", ""))

    bloques = [
        f"## {titulo}",
        "",
        f"- **Slug:** `{slug}`",
        f"- **URL:** {link}",
        f"- **Publicado:** {fecha}",
    ]
    if modificado and modificado != fecha:
        bloques.append(f"- **Modificado:** {modificado}")
    bloques.append("")

    if excerpt:
        bloques.append(f"**Resumen:** {excerpt}")
        bloques.append("")

    bloques.append("### Contenido")
    bloques.append("")
    bloques.append(contenido)
    bloques.append("")
    bloques.append("---")
    bloques.append("")
    return "\n".join(bloques)


def main() -> int:
    config = cargar_config()
    base_url = config["WP_BASE_URL"]
    auth = basic_auth_header(config["WP_USER"], config["WP_APP_PASSWORD"])

    print(f"Conectando a {base_url} como {config['WP_USER']}...")

    with httpx.Client(
        timeout=TIMEOUT,
        headers={"Authorization": auth, "User-Agent": "claude-for-legal-ar/ingest"},
    ) as client:
        # Verificar auth
        ping = client.get(f"{base_url}/wp-json/wp/v2/users/me")
        if ping.status_code == 401:
            print("ERROR: credenciales rechazadas (401). Verificá WP_USER y WP_APP_PASSWORD.", file=sys.stderr)
            return 1
        ping.raise_for_status()
        usuario_info = ping.json()
        print(f"  Autenticado como: {usuario_info.get('name', '?')} (ID {usuario_info.get('id', '?')})")

        # Resolver categorías
        category_ids = resolver_categorias(client, base_url, config["WP_CATEGORY_SLUGS"])
        if category_ids:
            print(f"  Filtrando por categorías: {category_ids}")
        else:
            print("  Sin filtro de categoría — descargando todo.")

        # Fetch posts
        print("Descargando posts...")
        posts = list(fetch_posts(client, base_url, category_ids))
        print(f"  Posts recuperados: {len(posts)}")

    if not posts:
        print("Sin posts para escribir. Salida sin cambios.")
        return 0

    # Renderizar
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    encabezado = (
        "# Guías de mariovadillo.com.ar — contenido ingestado\n"
        "\n"
        "> Generado por `scripts/ingest-vadillo-wordpress.py`. **No editar a mano** — "
        "se regenera cada vez que corra el script.\n"
        "\n"
        f"- Fuente: {base_url}\n"
        f"- Posts: {len(posts)}\n"
        "- Uso: las skills del plugin `derecho-consumidor` leen este archivo como "
        "referencia de criterios, modelos y guías del autor.\n"
        "\n"
        "---\n\n"
    )

    cuerpo = "\n".join(renderizar_post(p) for p in posts)

    OUTPUT_FILE.write_text(encabezado + cuerpo, encoding="utf-8")
    print(f"OK: escrito {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
