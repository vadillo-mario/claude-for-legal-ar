"""Servidor MCP para fuentes legales argentinas.

Expone herramientas para:
- Buscar normativa nacional en Infoleg
- Recuperar el texto de una norma específica
- Buscar publicaciones recientes en el Boletín Oficial de la Nación (BORA)
- Buscar publicaciones recientes en el Boletín Oficial de Mendoza
- Listar y consultar organismos: SCJM, CIJur, CSJN, ATM, EPRE, Irrigación, ARCA

Notas de implementación
-----------------------
Este v0.1.0 hace scraping ligero contra los sitios públicos. Para producción se
recomienda:
1. Implementar cache local (SQLite) para reducir presión sobre los servidores
   públicos.
2. Manejar rate limiting con backoff exponencial.
3. Agregar tests contra fixtures HTML versionados.
4. Considerar usar API JSON cuando esté disponible (BORA tiene endpoints JSON
   en algunas vistas; Infoleg tiene búsqueda HTML).
"""

import asyncio
import logging
import sys
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from . import infoleg, bora, bo_mendoza, organismos

logger = logging.getLogger("ar-legal-sources")

server = Server("ar-legal-sources")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Listar herramientas disponibles."""
    return [
        Tool(
            name="infoleg_buscar",
            description=(
                "Busca normativa nacional argentina en Infoleg por palabra clave, "
                "número de norma, o combinación. Retorna lista de coincidencias con "
                "número, tipo (ley/decreto/resolución), título, fecha de sanción y URL."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "consulta": {
                        "type": "string",
                        "description": (
                            "Texto libre a buscar (ej: 'defensa del consumidor', "
                            "'24240', 'planes de ahorro'). Mínimo 3 caracteres."
                        ),
                    },
                    "tipo_norma": {
                        "type": "string",
                        "enum": ["ley", "decreto", "resolucion", "todos"],
                        "default": "todos",
                        "description": "Filtrar por tipo de norma.",
                    },
                    "limite": {
                        "type": "integer",
                        "default": 10,
                        "description": "Cantidad máxima de resultados (1-50).",
                    },
                },
                "required": ["consulta"],
            },
        ),
        Tool(
            name="infoleg_obtener_norma",
            description=(
                "Recupera el texto completo y los metadatos de una norma nacional "
                "específica desde Infoleg. Requiere el ID interno de Infoleg "
                "(obtenible vía infoleg_buscar)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "id_infoleg": {
                        "type": "string",
                        "description": "ID interno de Infoleg (ej: '638').",
                    },
                },
                "required": ["id_infoleg"],
            },
        ),
        Tool(
            name="bora_publicaciones_recientes",
            description=(
                "Consulta publicaciones del Boletín Oficial de la República Argentina "
                "(BORA) en una fecha o rango de fechas. Útil para detectar decretos "
                "y resoluciones recientes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "fecha": {
                        "type": "string",
                        "description": (
                            "Fecha en formato YYYY-MM-DD. Si se omite, usa hoy."
                        ),
                    },
                    "seccion": {
                        "type": "string",
                        "enum": ["primera", "segunda", "tercera", "todas"],
                        "default": "primera",
                        "description": (
                            "Sección del Boletín. 'primera' contiene leyes, decretos "
                            "y resoluciones del Estado nacional."
                        ),
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="bo_mendoza_publicaciones_recientes",
            description=(
                "Consulta publicaciones del Boletín Oficial de la Provincia de "
                "Mendoza en una fecha o rango. Útil para detectar decretos y "
                "resoluciones provinciales."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "fecha": {
                        "type": "string",
                        "description": (
                            "Fecha en formato YYYY-MM-DD. Si se omite, usa hoy."
                        ),
                    },
                    "palabra_clave": {
                        "type": "string",
                        "description": (
                            "Opcional. Filtra resultados por palabra clave (ej: "
                            "'EPRE', 'ATM', 'Irrigación')."
                        ),
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="listar_organismos_ar",
            description=(
                "Lista los organismos administrativos y judiciales argentinos "
                "que este servidor puede consultar: SCJM (Suprema Corte Mza), "
                "CIJur (Centro de Información Jurídica Mza), CSJN, ATM, EPRE, "
                "DGI Irrigación, ARCA (ex AFIP). Devuelve para cada uno: alias, "
                "nombre, URL, descripción y nivel de cobertura."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="consultar_organismo_ar",
            description=(
                "Consulta un organismo argentino específico. Si se pasa "
                "'consulta', busca por texto cuando el organismo lo permite. "
                "Si no, devuelve novedades de la portada. Útil para jurisprudencia "
                "provincial (SCJM, CIJur), resoluciones administrativas (ATM, EPRE, "
                "Irrigación, ARCA), o cuando una norma no está en Infoleg/BORA. "
                "Llamar primero a listar_organismos_ar para ver alias disponibles."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "alias": {
                        "type": "string",
                        "enum": ["scjm", "cijur", "csjn", "atm", "epre", "irrigacion", "arca"],
                        "description": "Alias del organismo (ver listar_organismos_ar).",
                    },
                    "consulta": {
                        "type": "string",
                        "description": (
                            "Texto a buscar (opcional). Si se omite, devuelve "
                            "las novedades de la portada del organismo."
                        ),
                    },
                    "limite": {
                        "type": "integer",
                        "default": 10,
                        "description": "Cantidad máxima de resultados (1-50).",
                    },
                },
                "required": ["alias"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Despacho de llamadas a herramientas."""
    try:
        if name == "infoleg_buscar":
            resultado = await infoleg.buscar(
                consulta=arguments["consulta"],
                tipo_norma=arguments.get("tipo_norma", "todos"),
                limite=arguments.get("limite", 10),
            )
        elif name == "infoleg_obtener_norma":
            resultado = await infoleg.obtener_norma(
                id_infoleg=arguments["id_infoleg"],
            )
        elif name == "bora_publicaciones_recientes":
            resultado = await bora.publicaciones_recientes(
                fecha=arguments.get("fecha"),
                seccion=arguments.get("seccion", "primera"),
            )
        elif name == "bo_mendoza_publicaciones_recientes":
            resultado = await bo_mendoza.publicaciones_recientes(
                fecha=arguments.get("fecha"),
                palabra_clave=arguments.get("palabra_clave"),
            )
        elif name == "listar_organismos_ar":
            resultado = await organismos.listar_organismos()
        elif name == "consultar_organismo_ar":
            resultado = await organismos.consultar_organismo(
                alias=arguments["alias"],
                consulta=arguments.get("consulta"),
                limite=arguments.get("limite", 10),
            )
        else:
            return [TextContent(type="text", text=f"Herramienta desconocida: {name}")]

        return [TextContent(type="text", text=resultado)]

    except httpx.HTTPError as e:
        logger.error(f"Error HTTP en {name}: {e}")
        return [TextContent(
            type="text",
            text=(
                f"Error de conectividad al consultar la fuente. "
                f"El sitio puede estar caído o lento. Detalle: {e}"
            ),
        )]
    except Exception as e:
        logger.exception(f"Error en {name}")
        return [TextContent(
            type="text",
            text=f"Error procesando la solicitud: {e}",
        )]


async def main_async() -> None:
    """Entry point asíncrono."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Iniciando ar-legal-sources MCP server...")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Entry point sincrónico (usado por el script de consola)."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("ar-legal-sources terminado por usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()
