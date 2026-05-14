# Quick Start

**5 minutos.** De cero a usando el primer plugin.

## 1. Tener Claude Code instalado

Si todavía no lo tenés en tu Mac, abrí la Terminal y corré:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Cerrá y volvé a abrir la Terminal. Después tipeá `claude` y dale enter para entrar.

## 2. Cloná o descargá este repo

```bash
cd ~
git clone https://github.com/MNVadillo/claude-for-legal-ar.git
```

(Reemplazá `MNVadillo` por tu usuario de GitHub si forkeaste a otra cuenta.)

## 3. Agregá el marketplace y el primer plugin

Adentro de Claude Code:

```
/plugin marketplace add ~/claude-for-legal-ar
/plugin install derecho-consumidor@claude-for-legal-ar
```

Cuando te pregunte si querés instalación de proyecto o de usuario, **elegí usuario** — así el plugin lee archivos desde cualquier carpeta de tu Mac, no solo el proyecto actual.

## 4. **Cerrá y volvé a abrir Claude Code**

Este paso no es opcional. Hasta que reinicies, el plugin no está activo.

## 5. Corré el cold-start

```
/derecho-consumidor:cold-start-interview
```

Tarda 10 a 15 minutos. Te va a preguntar:

- Tus áreas de práctica dentro del derecho del consumidor (bancos, telcos, servicios públicos, salud, transporte aéreo, etc.)
- Tu jurisdicción principal (provincia, fueros)
- Tu estilo de redacción doctrinal
- Documentos semilla — escritos viejos tuyos, intimaciones modelo, dictámenes

Cuanto más material le des, más afinada queda la salida de cada skill. Hay opción `--quick-start` si querés tenerlo operativo en 2 minutos y refinar después.

## 6. Conectá las fuentes legales

Para que las citas a SAIJ, Infoleg y boletines oficiales sean reales (no inventadas por el modelo):

```bash
# SAIJ — MCP de terceros (Hernán C.C., open source)
pip install saij-mcp --break-system-packages

# ar-legal-sources — MCP propio de este repo (Infoleg + BORA + BO Mendoza)
cd ~/claude-for-legal-ar/mcp-servers/ar-legal-sources
pip install -e . --break-system-packages
```

Después agregalos a tu config de Claude Code:

```
claude mcp add saij saij-mcp
claude mcp add ar-legal-sources ar-legal-sources
```

## 7. Probalo

Tirale un caso real:

```
Revisame este contrato de plan de ahorro: tiene cláusula de actualización
por valor móvil del modelo y un cargo de "gastos administrativos" del 8%
sobre el valor de cada cuota. ¿Hay abusividad?
```

El plugin debería identificar las cláusulas problemáticas, citar arts. 988 CCyCN y 37 LDC, y referenciar (si están conectadas) jurisprudencia comparable.

## Si algo falla

- **"Command not found"** → te olvidaste de reiniciar Claude Code (paso 4).
- **"Run setup first"** → corré el `cold-start-interview` antes que cualquier otra skill.
- **Citas marcadas `[verificar]`** → faltó conectar SAIJ o ar-legal-sources (paso 6). Sin fuentes conectadas, las citas vienen del modelo y hay que verificarlas a mano.
- **"No puedo leer este archivo"** → instalaste en alcance de proyecto, no de usuario. Reinstalá desde tu home: `/plugin uninstall derecho-consumidor`, después `/plugin install derecho-consumidor@claude-for-legal-ar` desde `~`.

## Cargar tu propio contenido

Si querés que el plugin tenga tus guías y tus artículos publicados como referencias:

```bash
cd ~/claude-for-legal-ar
# Configurar credenciales WordPress en un .env (no se commitea)
cp scripts/.env.example scripts/.env
# Editar scripts/.env con tus datos

# Ingestar guías de tu sitio
python scripts/ingest-vadillo-wordpress.py

# Ingestar tus artículos publicados en MDZ
python scripts/ingest-mdz-articles.py
```

Ambos scripts depositan el contenido en `derecho-consumidor/references/` como markdown indexable. Las skills lo levantan automáticamente.
