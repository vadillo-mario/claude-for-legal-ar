# derecho-consumidor

Plugin para Claude Code orientado a la práctica de defensa del consumidor en Argentina, con foco en LDC 24.240, CCyCN arts. 1092-1122 y 988, normativa BCRA, y regulación sectorial (ENRE, ENARGAS, ANAC, ENACOM, SSN, SSS).

## Skills disponibles (v0.1.0)

| Comando | Qué hace |
|---|---|
| `/derecho-consumidor:cold-start-interview` | Setup inicial — aprende tus áreas, jurisdicción, estilo doctrinal y carga documentos semilla |
| `/derecho-consumidor:revision-clausulas-abusivas` | Revisa un contrato de adhesión (planes de ahorro, créditos, seguros, prestación) contra LDC art. 37 y CCyCN art. 988. Marca cláusulas abusivas y propone redacción de impugnación |
| `/derecho-consumidor:intimacion-servicio-publico` | Redacta carta documento o nota administrativa de intimación a empresa de servicio público (Ecogas, EDEMSA, AYSAM, telcos, ENACOM) por facturación irregular, cortes, reemplazo de medidor, cargos abusivos |
| `/derecho-consumidor:escrito-dano-punitivo` | Borrador de escrito invocando daño punitivo (LDC art. 52 bis) con encuadre fáctico, jurídico y cuantificación |

## Skills en desarrollo (próximas versiones)

- `denuncia-coprec` — denuncia COPREC con encuadre Ley 26.993
- `analisis-tasa-usuraria` — análisis de tasa contractual contra promedio BCRA, doctrina de la usura (CCyCN art. 771)
- `reclamo-prepaga` — autorizaciones denegadas, copagos abusivos, PMO
- `reclamo-aerolinea` — cancelaciones, demoras, overbooking (Convenio Montreal + Cód. Aeronáutico + Res. ANAC 1532/98)
- `respuesta-whatsapp-consulta` — respuesta breve y numerada a consulta de ciudadano

## Fuentes que consulta

El plugin escala su rigor según las fuentes conectadas:

- **Sin fuentes externas** → cita de memoria del modelo, marca `[verificar]` en cada cita. Útil para borradores, no para presentar.
- **Con SAIJ (`saij-mcp`)** → jurisprudencia federal y provincial, doctrina, legislación nacional verificada contra base oficial.
- **Con `ar-legal-sources`** → texto vigente de leyes nacionales (Infoleg), boletines oficiales recientes (BORA, BO Mendoza).
- **Con WordPress de mariovadillo.com.ar y artículos MDZ ingestados** → reutilización de criterios doctrinales y modelos propios.

## Setup

```bash
# Desde Claude Code, después de agregar el marketplace:
/plugin install derecho-consumidor@claude-for-legal-ar

# Reiniciar Claude Code, después:
/derecho-consumidor:cold-start-interview
```

Ver [QUICKSTART.md](../QUICKSTART.md) raíz para más detalle.

## Lo que el plugin NO hace

- **No firma escritos.** El abogado revisa, ajusta y firma. Cada salida es borrador.
- **No reemplaza la consulta personal.** Para casos complejos o de alto impacto, la matrícula es del abogado, no del modelo.
- **No accede a expedientes** del Poder Judicial sin conector específico configurado (no hay aún MCP para SCJM en este repo).
- **No genera escritos de fueros que requieran firma digital** sin un paso humano explícito de validación.

## Advertencia de uso responsable

Las salidas son borradores doctrinarios. La responsabilidad profesional sobre lo que se presenta en sede administrativa o judicial es indelegable. Plazos procesales y administrativos: siempre verificarlos contra el expediente y el código de procedimientos aplicable.
