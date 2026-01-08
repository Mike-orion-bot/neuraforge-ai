#!/bin/bash
# sync_neuraforge.sh - Sincronización automática con Git + Railway
# Ubicación: ~/neuraforge_ai/sync_neuraforge.sh

set -e  # Detener en errores

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración
PROJECT_DIR="$HOME/neuraforge_ai"
GIT_USER="Mike-orion-bot"
GIT_REPO="neuraforge-ai"
GIT_BRANCH="main"
RAILWAY_PROJECT_ID="d25a4126-83ea-4c45-847a-50d8f77f0acb"  # Tu ID de Railway

log() { echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# Función para actualizar Railway CLI
update_railway_cli() {
    log "Actualizando Railway CLI..."
    if npm list -g @railway/cli | grep -q '@railway/cli'; then
        npm update -g @railway/cli
        success "Railway CLI actualizado"
    else
        npm install -g @railway/cli
        success "Railway CLI instalado"
    fi
}

# Función para configurar Git remoto correctamente
setup_git_remote() {
    log "Configurando Git remote..."
    
    cd "$PROJECT_DIR"
    
    # Verificar si es un repositorio Git
    if [ ! -d ".git" ]; then
        git init
        success "Repositorio Git inicializado"
    fi
    
    # Configurar usuario
    git config user.email "zevachmk@gmail.com"
    git config user.name "Mike Orion Bot"
    
    # Configurar remote correcto
    if git remote | grep -q "origin"; then
        git remote remove origin
    fi
    
    git remote add origin "https://github.com/$GIT_USER/$GIT_REPO.git"
    
    # Verificar conexión
    if git ls-remote --exit-code origin > /dev/null 2>&1; then
        success "Conexión Git establecida con https://github.com/$GIT_USER/$GIT_REPO"
    else
        error "No se puede conectar al repositorio. ¿Existe?"
        echo "Puedes crearlo en: https://github.com/new"
        echo "Nombre: $GIT_REPO"
        echo "Luego ejecuta: git push -u origin main"
        return 1
    fi
}

# Función para sincronizar con GitHub
sync_with_github() {
    log "Sincronizando con GitHub..."
    
    cd "$PROJECT_DIR"
    
    # Crear .gitignore si no existe
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# Database
*.db
*.sqlite3

# Secrets
.env
.secret
*.key
*.pem

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temporary
tmp/
temp/

# APK builds
dist/
build/
*.apk
EOF
        success ".gitignore creado"
    fi
    
    # Agregar todos los archivos
    git add .
    
    # Verificar si hay cambios
    if git diff --cached --quiet; then
        warning "No hay cambios para commitear"
        return 0
    fi
    
    # Hacer commit
    git commit -m "Sync automático: $(date '+%Y-%m-%d %H:%M:%S')" || {
        warning "Commit vacío o error, continuando..."
        return 0
    }
    
    # Pull antes de push para evitar conflictos
    git pull origin "$GIT_BRANCH" --rebase --autostash || {
        warning "Posible conflicto, intentando merge..."
        git pull origin "$GIT_BRANCH" --no-rebase
    }
    
    # Push a GitHub
    if git push -u origin "$GIT_BRANCH"; then
        success "✅ Push exitoso a GitHub"
        return 0
    else
        error "Error en push. Intentando forzar..."
        
        read -p "¿Forzar push? (s/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            git push -u origin "$GIT_BRANCH" --force
            success "Push forzado exitoso"
        else
            error "Push cancelado"
            return 1
        fi
    fi
}

# Función para configurar Railway
setup_railway() {
    log "Configurando Railway..."
    
    # Actualizar CLI primero
    update_railway_cli
    
    # Login a Railway
    if ! railway whoami 2>/dev/null; then
        warning "Sesión no iniciada. Iniciando sesión en Railway..."
        railway login
        
        if [ $? -ne 0 ]; then
            error "Error al iniciar sesión en Railway"
            echo "Intenta manualmente: railway login"
            return 1
        fi
    fi
    
    # Enlazar proyecto
    cd "$PROJECT_DIR"
    
    if [ ! -f ".railway/config.json" ]; then
        log "Enlazando proyecto con Railway..."
        railway link "$RAILWAY_PROJECT_ID"
        
        if [ $? -ne 0 ]; then
            warning "Creando nuevo proyecto en Railway..."
            railway init
        fi
    fi
    
    # Configurar variables de entorno si no existen
    log "Configurando variables de entorno..."
    
    # Lista de variables requeridas
    declare -A required_vars=(
        ["TELEGRAM_TOKEN"]="Tu token de Telegram (de @BotFather)"
        ["SECRET_KEY"]="$(openssl rand -hex 32)"
        ["ADMIN_PASSWORD"]="neuraforge_admin_$(date +%Y)"
        ["DATABASE_URL"]="sqlite:///neuraforge.db"
    )
    
    for var in "${!required_vars[@]}"; do
        if ! railway variables list 2>/dev/null | grep -q "$var"; then
            log "Configurando $var..."
            
            # Usar nueva sintaxis de Railway CLI
            railway variables set "$var=${required_vars[$var]}" 2>/dev/null || \
            railway variables add "$var" "${required_vars[$var]}" 2>/dev/null || \
            echo "Warning: No se pudo configurar $var manualmente"
        fi
    done
    
    success "Railway configurado"
}

# Función para desplegar en Railway
deploy_to_railway() {
    log "Desplegando en Railway..."
    
    cd "$PROJECT_DIR"
    
    # Crear railway.json si no existe
    if [ ! -f "railway.json" ]; then
        cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python main_orchestrator.py",
    "restartPolicyType": "ON_FAILURE",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100
  }
}
EOF
        success "railway.json creado"
    fi
    
    # Crear requirements.txt actualizado
    log "Actualizando requirements.txt..."
    cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-telegram-bot==20.7
python-dotenv==1.0.0
cryptography==41.0.7
sqlalchemy==2.0.23
aiohttp==3.9.1
jinja2==3.1.2
qrcode[pil]==7.4.2
boto3==1.34.0
aiosqlite==0.19.0
pandas==2.1.4
pytest==7.4.3
EOF
    
    # Desplegar
    log "Iniciando deploy..."
    railway up --detach
    
    if [ $? -eq 0 ]; then
        success "✅ Deploy iniciado en Railway"
        echo ""
        echo "🌐 URL de producción: https://neuraforge-ai.up.railway.app"
        echo "📊 Dashboard: https://railway.app/project/$RAILWAY_PROJECT_ID"
        echo ""
        echo "Puedes ver los logs con: railway logs"
    else
        error "Error en deploy"
        return 1
    fi
}

# Función para verificar estado
check_status() {
    log "Verificando estado del sistema..."
    
    echo ""
    echo "📊 ESTADO ACTUAL:"
    echo "=================="
    
    # Git
    cd "$PROJECT_DIR"
    echo -n "Git: "
    if git status > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        echo "  Branch: $(git branch --show-current)"
        echo "  Cambios: $(git status --porcelain | wc -l) archivos modificados"
    else
        echo -e "${RED}No inicializado${NC}"
    fi
    
    # Railway
    echo -n "Railway: "
    if railway whoami > /dev/null 2>&1; then
        echo -e "${GREEN}Conectado${NC}"
    else
        echo -e "${RED}No conectado${NC}"
    fi
    
    # Python
    echo -n "Python: "
    if python3 --version > /dev/null 2>&1; then
        echo -e "${GREEN}$(python3 --version)${NC}"
    else
        echo -e "${RED}No encontrado${NC}"
    fi
    
    echo ""
}

# Función para crear estructura de directorios
create_directory_structure() {
    log "Creando estructura de directorios..."
    
    mkdir -p "$PROJECT_DIR"/{core/security,core/payment,modules,sat_admin,static,templates,logs}
    
    # Mover archivos HTML a templates si es necesario
    if [ -f "admin.HTML" ]; then
        mv admin.HTML templates/
    fi
    
    if [ -f "user_panel.HTML" ]; then
        mv user_panel.HTML templates/
    fi
    
    success "Estructura creada"
}

# Función principal
main() {
    echo ""
    echo "🚀 NEURAFORGE AI - SISTEMA DE SINCRONIZACIÓN"
    echo "=========================================="
    echo ""
    
    cd "$PROJECT_DIR"
    
    # Mostrar menú
    PS3="Selecciona una opción: "
    options=(
        "1. Sincronización completa (Git + Railway)"
        "2. Solo sincronizar con GitHub"
        "3. Solo desplegar en Railway"
        "4. Configurar Railway por primera vez"
        "5. Verificar estado"
        "6. Crear estructura de directorios"
        "7. Salir"
    )
    
    select opt in "${options[@]}"; do
        case $REPLY in
            1)
                check_status
                create_directory_structure
                setup_git_remote
                sync_with_github
                setup_railway
                deploy_to_railway
                break
                ;;
            2)
                check_status
                setup_git_remote
                sync_with_github
                break
                ;;
            3)
                check_status
                setup_railway
                deploy_to_railway
                break
                ;;
            4)
                update_railway_cli
                railway login
                railway init
                break
                ;;
            5)
                check_status
                break
                ;;
            6)
                create_directory_structure
                break
                ;;
            7)
                echo "¡Hasta luego!"
                exit 0
                ;;
            *)
                echo "Opción inválida"
                ;;
        esac
    done
    
    echo ""
    success "Proceso completado"
    echo ""
    echo "📌 Próximos pasos:"
    echo "   1. Verifica que tu bot de Telegram esté funcionando"
    echo "   2. Accede al panel: https://neuraforge-ai.up.railway.app/admin"
    echo "   3. Monitorea los logs: railway logs"
    echo ""
}

# Ejecutar
main "$@"
