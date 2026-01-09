#!/bin/bash
# git_sync_pro.sh - Sincronización profesional para NeuraForge AI
# Versión: 3.0 - Optimizado para estructura existente

set -e

echo "🚀 NEURAFORGE AI - GIT SYNC PROFESIONAL"
echo "======================================="

# Configuración
PROJECT_DIR="$HOME/neuraforge_ai"
GITHUB_USER="Mike-orion-bot"
GITHUB_REPO="neuraforge-ai"
GITHUB_URL="https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
BRANCH="main"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funciones
log() { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# 1. IR AL DIRECTORIO
cd "$PROJECT_DIR"

# 2. VERIFICAR ESTRUCTURA ACTUAL
log "Analizando estructura actual..."
echo "📁 Directorios: $(find . -type d | wc -l)"
echo "📄 Archivos: $(find . -type f | wc -l)"
echo "💾 Tamaño: $(du -sh . | cut -f1)"

# 3. CREAR .GITIGNORE COMPLETO
log "Creando .gitignore optimizado..."

cat > .gitignore << 'EOF'
# ==================== PYTHON ====================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
env.bak/
venv.bak/

# ==================== ENVIRONMENT ====================
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.env.*
!.env.example
secrets/
credentials/

# ==================== DATABASE ====================
*.db
*.sqlite
*.sqlite3
*.db-journal
neuraforge.db
neuraforge_hive.db
data/*.db
data/*.sqlite

# ==================== LOGS ====================
logs/
*.log
logs/*.log
!logs/.gitkeep

# ==================== BACKUPS ====================
backups/
*.backup.*
*.bak

# ==================== CACHE & TEMP ====================
.cache/
tmp/
temp/
*.tmp
*.temp

# ==================== IDE ====================
.vscode/
.idea/
*.swp
*.swo
*~

# ==================== OS ====================
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# ==================== BUILD & DIST ====================
dist/
build/
*.egg-info/
.coverage
.tox/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/

# ==================== APK & BINARIES ====================
*.apk
*.exe
*.dll
*.so
*.dylib
bin/

# ==================== RAILWAY ====================
.railway/
railway.toml

# ==================== DOCKER ====================
docker-compose.override.yml

# ==================== PERSONAL ====================
personal/
private/
secret/
keys/
*.key
*.pem
*.crt

# ==================== REPORTS ====================
reports/*.pdf
reports/*.docx
reports/temp/

# ==================== STATIC ASSETS ====================
static/apk/*.apk
static/uploads/
static/temp/

# ==================== TEMPLATES CACHE ====================
templates/__pycache__/
templates/*.pyc

# ==================== SPECIFIC FILES ====================
# Archivos de configuración local
config.local.json
settings.local.py

# Archivos de backup
*.backup.*
admin.HTML.backup.*

# Archivos temporales de scripts
*.sh.tmp
*.py.tmp
EOF

success ".gitignore creado"

# 4. CONFIGURAR GIT
log "Configurando Git..."

# Verificar si ya es repositorio Git
if [ ! -d ".git" ]; then
    log "Inicializando repositorio Git..."
    git init
    git remote add origin "$GITHUB_URL"
    
    # Configurar usuario
    git config user.email "zevachmk@gmail.com"
    git config user.name "Mike Orion Bot"
    
    success "Repositorio Git inicializado"
else
    # Verificar conexión remota
    if ! git remote | grep -q origin; then
        git remote add origin "$GITHUB_URL"
    fi
    
    # Actualizar URL si es necesario
    CURRENT_URL=$(git remote get-url origin 2>/dev/null || echo "")
    if [[ "$CURRENT_URL" != *"${GITHUB_USER}/${GITHUB_REPO}"* ]]; then
        warning "URL remota diferente, actualizando..."
        git remote set-url origin "$GITHUB_URL"
    fi
fi

# 5. SINCRONIZAR CON GITHUB
log "Sincronizando con GitHub..."

# Verificar si hay cambios pendientes
if git status --porcelain | grep -q "."; then
    log "Cambios detectados:"
    git status --short
    
    # Agregar todos los archivos (respetando .gitignore)
    git add .
    
    # Hacer commit
    COMMIT_MSG="Sync: $(date '+%Y-%m-%d %H:%M:%S') - Sistema completo NeuraForge AI"
    git commit -m "$COMMIT_MSG"
    
    success "✅ Commit creado: $COMMIT_MSG"
else
    warning "No hay cambios para commitear"
fi

# 6. PULL ANTES DE PUSH (para evitar conflictos)
log "Actualizando desde GitHub..."
if git pull origin "$BRANCH" --rebase --autostash; then
    success "✅ Pull exitoso"
else
    warning "⚠️  Posible conflicto, intentando merge..."
    git pull origin "$BRANCH" --no-rebase || {
        error "❌ No se pudo hacer pull. Resuelve conflictos manualmente."
        echo "Sugerencia:"
        echo "  git stash"
        echo "  git pull origin $BRANCH"
        echo "  git stash pop"
        exit 1
    }
fi

# 7. PUSH A GITHUB
log "Subiendo a GitHub..."
if git push -u origin "$BRANCH"; then
    success "✅ ¡Push exitoso a GitHub!"
    echo ""
    echo "🌐 Repositorio: https://github.com/${GITHUB_USER}/${GITHUB_REPO}"
    echo "📊 GitHub: https://github.com/${GITHUB_USER}/${GITHUB_REPO}/tree/${BRANCH}"
else
    error "❌ Error en push. Posibles causas:"
    echo "   1. No tienes permisos de escritura"
    echo "   2. El repositorio no existe"
    echo "   3. Problemas de autenticación"
    echo ""
    echo "💡 Soluciones:"
    echo "   a) Crear repositorio: https://github.com/new"
    echo "   b) Usar token de acceso:"
    echo "      git remote set-url origin https://TOKEN@github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
    echo ""
    
    read -p "¿Intentar push forzado? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        git push -u origin "$BRANCH" --force
        success "✅ Push forzado exitoso"
    else
        error "Push cancelado"
    fi
fi

# 8. CREAR ARCHIVO README.md SI NO EXISTE
if [ ! -f "README.md" ]; then
    log "Creando README.md profesional..."
    
    cat > README.md << 'EOF'
# 🚀 NeuraForge AI - Ecosistema Autosustentable

<div align="center">
  
![NeuraForge Logo](https://img.shields.io/badge/NeuraForge-AI%20Ecosystem-blue)
![Version](https://img.shields.io/badge/Version-3.0-green)
![License](https://img.shields.io/badge/License-MIT-orange)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

**IAs generan ingresos → Ganancias se redistribuyen → Financian más IAs → Impacto positivo**

</div>

## 🌍 Visión
Sistema autosustentable donde las IAs generan ganancias que financian el desarrollo de más IAs, creando un ciclo virtuoso de innovación.

## 🏗️ Arquitectura
