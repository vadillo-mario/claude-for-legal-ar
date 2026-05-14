# ar-legal-sources — MCP Server

Servidor MCP (Model Context Protocol) que expone fuentes legales argentinas al cliente Claude (Claude Code, Claude Cowork, Claude Desktop).

## Herramientas expuestas

| Tool | Qué hace |
|---|---|
| `infoleg_buscar` | Busca normativa nacional en Infoleg por palabra clave, número, o tipo |
| `infoleg_obtener_norma` | Recupera el texto completo y los metadatos de una norma específica |
| `bora_publicaciones_recientes` | Lista publicaciones del Boletín Oficial Nación por fecha |
| `bo_mendoza_publicaciones_recientes` | Lista publicaciones del Boletín Oficial de Mendoza por fecha |
| `listar_organismos_ar` | Lista organismos disponibles (SCJM, CIJur, CSJN, ATM, EPRE, Irrigación, ARCA) |
| `consultar_organismo_ar` | Consulta un organismo específico: búsqueda por texto o novedades de portada |

## Instalación

Requiere Python 3.10+.

```bash
cd mcp-servers/ar-legal-sources
pip install -e . --break-system-packages
```

(El flag `--break-system-packages` es necesario en macOS reciente con Python instalado vía Homebrew o el sistema; alternativamente usá un virtualenv o `uv`.)

## Registro en Claude Code

```bash
claude mcp add ar-legal-sources ar-legal-sources
```

## Uso típico desde Claude Code

Una vez registrado, el cliente Claude puede invocar las herramientas naturalmente:

> "Buscame en Infoleg la Ley de Defensa del Consumidor"
> → llama a `infoleg_buscar(consulta="defensa del consumidor", tipo_norma="ley")`

> "Decretos del Boletín Oficial del 14 de mayo de 2026"
> → llama a `bora_publicaciones_recientes(fecha="2026-05-14")`

> "¿Salió algo de EPRE en el BO Mendoza la semana pasada?"
> → llama a `bo_mendoza_publicaciones_recientes(fecha=..., palabra_clave="EPRE")`

## Estado del v0.1.0

Lo que funciona:

- Las cuatro herramientas están implementadas y ejecutan HTTP real contra los sitios públicos.
- Parsing HTML con heurísticas robustas pero adaptables si los sitios cambian.
- Manejo de errores básico (404, timeouts).

Lo que falta para producción:

- Cache local (SQLite) para evitar martillar las fuentes.
- Tests contra fixtures HTML versionados.
- Rate limiting con backoff exponencial.
- Soporte para texto actualizado de Infoleg cuando la norma tiene anexo `texact.htm`.
- Soporte para PDF en BO Mendoza (algunas ediciones son sólo PDF).
- Recuperación de detalle individual de items del BORA y BO Mza (hoy solo lista la portada).

## Cobertura por fuente

| Fuente | Cobertura v0.1 | Tool MCP |
|---|---|---|
| Infoleg | Búsqueda + recuperación de norma | `infoleg_buscar`, `infoleg_obtener_norma` |
| BORA | Portada por fecha y sección | `bora_publicaciones_recientes` |
| BO Mendoza | Portada por fecha + filtro por palabra | `bo_mendoza_publicaciones_recientes` |
| SCJM | Búsqueda + listado de resultados | `consultar_organismo_ar` alias `scjm` |
| CIJur | Búsqueda + listado básico | `consultar_organismo_ar` alias `cijur` |
| CSJN | URL del buscador (recomendado complementar con SAIJ) | `consultar_organismo_ar` alias `csjn` |
| ATM | Novedades de portada | `consultar_organismo_ar` alias `atm` |
| EPRE | Novedades de portada | `consultar_organismo_ar` alias `epre` |
| DGI Irrigación | Novedades de portada | `consultar_organismo_ar` alias `irrigacion` |
| ARCA | Búsqueda en normativa + novedades | `consultar_organismo_ar` alias `arca` |
| SAIJ | (Usar MCP de terceros) | `saij-mcp` (paquete pip de hernan-cc) |

Para **SAIJ** (jurisprudencia con sumarios, tesauro, doctrina) usar el MCP de terceros [hernan-cc/saij-mcp](https://glama.ai/mcp/servers/@hernan-cc/saij-mcp), que envuelve la API JSON pública de SAIJ y está más maduro que cualquier scraping. Instalación: `pip install saij-mcp`.

## Contribuir

Pull requests bienvenidos. Tests con `pytest`. Estructura preferida: agregar un módulo nuevo (`atm.py`, `epre.py`, etc.) por cada fuente que se quiera cubrir, y exponer su herramienta en `server.py`.

## Licencia

Apache 2.0 — ver el LICENSE de la raíz del repo.
