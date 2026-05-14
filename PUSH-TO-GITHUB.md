# Cómo subir este repo a tu GitHub

Pasos para publicar `claude-for-legal-ar` en tu cuenta de GitHub. Asumo que tu usuario es **MNVadillo** — ajustá si es distinto.

## Opción A — Con GitHub CLI (recomendado)

Si tenés `gh` instalado en tu Mac (si no: `brew install gh`):

```bash
# 1. Descomprimir el ZIP en tu home
cd ~
unzip claude-for-legal-ar.zip
cd claude-for-legal-ar

# 2. Inicializar git
git init
git add .
git commit -m "v0.1.0: derecho-consumidor operativo + MCP ar-legal-sources + scripts de ingesta"

# 3. Login a GitHub si todavía no lo hiciste
gh auth login

# 4. Crear el repo y pushear de un solo paso
gh repo create MNVadillo/claude-for-legal-ar \
  --public \
  --description "Plugins de Claude Code para la práctica jurídica en Argentina — defensa del consumidor, derecho administrativo Mendoza, conectores a Infoleg/SAIJ/BORA/SCJM/CIJur/ATM/EPRE/Irrigación/ARCA." \
  --source=. \
  --push
```

## Opción B — Con git crudo + GitHub web

```bash
# 1. Descomprimir el ZIP en tu home
cd ~
unzip claude-for-legal-ar.zip
cd claude-for-legal-ar

# 2. Inicializar git
git init
git add .
git commit -m "v0.1.0: derecho-consumidor operativo + MCP ar-legal-sources + scripts de ingesta"
git branch -M main

# 3. Ir a https://github.com/new
#    Owner: MNVadillo
#    Repository name: claude-for-legal-ar
#    Description: (copiar de la opción A)
#    Public
#    NO marcar "Initialize this repository with README" (ya lo tenés)
#    Crear

# 4. GitHub te va a mostrar la URL — usala así:
git remote add origin https://github.com/MNVadillo/claude-for-legal-ar.git
git push -u origin main
```

## Después del push — primer uso

```bash
# Cloná en cualquier máquina donde uses Claude Code:
git clone https://github.com/MNVadillo/claude-for-legal-ar.git
cd claude-for-legal-ar

# Instalá el plugin
# (en Claude Code, no en zsh)
/plugin marketplace add ~/claude-for-legal-ar
/plugin install derecho-consumidor@claude-for-legal-ar
# Cerrar y reabrir Claude Code
/derecho-consumidor:cold-start-interview
```

## Cargar tus guías y artículos como referencia

Ya en la carpeta del repo:

```bash
# 1. Dependencias de los scripts
pip install -r scripts/requirements.txt --break-system-packages

# 2. Credenciales WordPress
cp scripts/.env.example scripts/.env
# Editá scripts/.env y completá WP_APP_PASSWORD con tu app password
# (el que ya está en memoria de Claude: "Rbfq Nwje etNy h1Im 5sjw 75LT")

# 3. Bajar tus guías de mariovadillo.com.ar
python scripts/ingest-vadillo-wordpress.py

# 4. Bajar tus columnas de mdzol.com/consumidores
python scripts/ingest-mdz-articles.py --paginas 30 --firma "Mario Vadillo"
```

Ambos generan archivos en `derecho-consumidor/references/` que NO se commitean (están en `.gitignore`), pero las skills los leen como referencia de tu estilo y criterios.

## Conectar las fuentes legales (MCPs)

```bash
# SAIJ — MCP de terceros que envuelve la API JSON oficial
pip install saij-mcp --break-system-packages

# ar-legal-sources — nuestro MCP (Infoleg, BORA, BO Mza, SCJM, CIJur, CSJN,
# ATM, EPRE, Irrigación, ARCA)
cd mcp-servers/ar-legal-sources
pip install -e . --break-system-packages
cd ../..

# Registrar en Claude Code
claude mcp add saij saij-mcp
claude mcp add ar-legal-sources ar-legal-sources
```

## Mantenimiento

- **Cuando cambien tus reglas de estilo** o agregues una nueva área de práctica: corré `/derecho-consumidor:cold-start-interview --refresh`.
- **Cuando publiques una guía nueva** o columna nueva: corré los scripts de ingesta para refrescar las referencias.
- **Cuando los sitios scrapeados cambien layout**: ajustar los selectores en `mcp-servers/ar-legal-sources/src/ar_legal_sources/`. Los archivos están comentados con notas sobre qué cambiar.

## Tag de versión

Cuando estés conforme con la v0.1.0:

```bash
git tag -a v0.1.0 -m "Primera versión pública"
git push origin v0.1.0
```

Esto crea un release en GitHub que otros pueden clonar pineado.

## Si querés mantenerlo privado primero

En la opción A, reemplazar `--public` por `--private`. Después se puede pasar a público desde Settings del repo en GitHub.
