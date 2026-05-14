# Claude for Legal — Argentina

Plugins de Claude Code y Claude Cowork para la práctica jurídica en Argentina, con foco inicial en defensa del consumidor y derecho administrativo provincial (Mendoza). Inspirado en [anthropics/claude-for-legal](https://github.com/anthropics/claude-for-legal), reescrito íntegramente para derecho argentino.

> **Estado:** v0.1.0 — primer plugin operativo (`derecho-consumidor`), segundo plugin en esqueleto (`derecho-admin-mendoza`), un MCP server inicial (`ar-legal-sources`).

## Qué hay en el repo

```
claude-for-legal-ar/
├── derecho-consumidor/          # plugin operativo — LDC 24.240, daño punitivo, COPREC
├── derecho-admin-mendoza/       # esqueleto — amparo colectivo, impugnación de actos
├── mcp-servers/
│   └── ar-legal-sources/        # MCP server: Infoleg + BORA + BO Mendoza
├── scripts/
│   ├── ingest-vadillo-wordpress.py   # bajar guías de mariovadillo.com.ar
│   └── ingest-mdz-articles.py        # bajar artículos del autor en mdzol.com
└── .claude-plugin/
    └── marketplace.json
```

## Fuentes de derecho integradas

| Fuente | Cobertura | Estado | Cómo se accede |
|---|---|---|---|
| **SAIJ** | Legislación nacional y provincial, jurisprudencia, doctrina | MCP de terceros disponible | `pip install saij-mcp` ([hernan-cc/saij-mcp](https://glama.ai/mcp/servers/@hernan-cc/saij-mcp)) |
| **Infoleg** | Legislación nacional (texto actualizado) | MCP propio | `mcp-servers/ar-legal-sources` — `infoleg_buscar`, `infoleg_obtener_norma` |
| **BORA** (Boletín Oficial Nación) | Decretos, resoluciones, leyes recién publicadas | MCP propio | `mcp-servers/ar-legal-sources` — `bora_publicaciones_recientes` |
| **BO Mendoza** | Decretos y leyes provinciales | MCP propio | `mcp-servers/ar-legal-sources` — `bo_mendoza_publicaciones_recientes` |
| **CIJur** | Doctrina y jurisprudencia Mendoza | MCP propio (búsqueda básica) | `consultar_organismo_ar` alias `cijur` |
| **SCJM** | Jurisprudencia Suprema Corte Mendoza | MCP propio (búsqueda + listado) | `consultar_organismo_ar` alias `scjm` |
| **CSJN** | Jurisprudencia CSJN | MCP propio (URL del buscador) | `consultar_organismo_ar` alias `csjn` |
| **ATM** | Resoluciones administrativas tributarias Mza. | MCP propio (portada) | `consultar_organismo_ar` alias `atm` |
| **EPRE** | Resoluciones regulador eléctrico Mza. | MCP propio (portada) | `consultar_organismo_ar` alias `epre` |
| **DGI Irrigación** | Resoluciones de Superintendencia del agua Mza. | MCP propio (portada) | `consultar_organismo_ar` alias `irrigacion` |
| **ARCA** (ex AFIP) | Resoluciones, instrucciones, dictámenes | MCP propio (búsqueda + portada) | `consultar_organismo_ar` alias `arca` |
| **Contenido propio del autor** | Guías de mariovadillo.com.ar + artículos en MDZ | Scripts de ingesta | `scripts/ingest-*.py` |

## Instalación rápida

Ver [QUICKSTART.md](./QUICKSTART.md) — 5 minutos.

```bash
# En Claude Code:
/plugin marketplace add /ruta/local/a/claude-for-legal-ar
/plugin install derecho-consumidor@claude-for-legal-ar

# Reiniciar Claude Code, después:
/derecho-consumidor:cold-start-interview
```

## Advertencia legal

Todas las salidas de estos plugins son **borradores para revisión profesional** — no son asesoramiento legal, no son dictámenes, no reemplazan al abogado. Cada skill emite drafts con citas a la fuente y plantea hipótesis; el abogado responsable verifica, completa y firma. Esto vale especialmente para los plazos procesales y administrativos, donde la responsabilidad del profesional es indelegable.

Los plugins reflejan un estilo de práctica (el del autor) y un encuadre doctrinal específicos. Adaptelos a su propia práctica corriendo el `cold-start-interview` de cada plugin.

## Licencia

Apache 2.0 — ver [LICENSE](./LICENSE). Forkeable, modificable, redistribuible.

## Contribuciones

Pull requests bienvenidos. Las guías de estilo doctrinal y redacción están en cada `CLAUDE.md` de los plugins.

---

**Autor:** Mario Vadillo · [mariovadillo.com.ar](https://mariovadillo.com.ar) · Abogado, especialista en derecho del consumidor, Mendoza, Argentina.


## Test: Validación de flujo end-to-end
Este PR valida que el flujo de integración de Claude funciona correctamente.
