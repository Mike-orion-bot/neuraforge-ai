#!/bin/bash
# sync_neuraforge_fixed.sh - Script corregido para sincronización

set -e

echo "🚀 NEURAFORGE AI - GIT SYNC PROFESIONAL"
echo "======================================="

# Configuración con TUS DATOS
PROJECT_DIR="$HOME/neuraforge_ai"
GITHUB_USER="Mike-orion-bot"
GITHUB_REPO="neuraforge-ai"
GITHUB_TOKEN="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"
GITHUB_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
BRANCH="main"

# Configuración Hotmart
HOTMART_CLIENT_ID="c9ae9a82-e436-4f28-80a8-5e195f0f7815"
HOTMART_CLIENT_SECRET="d6516d77-dad6-4695-98ee-617059331004"

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

# ================= 1. CONFIGURAR GIT =================
configure_git() {
    log "Configurando Git con tus credenciales..."
    
    cd "$PROJECT_DIR"
    
    # Corregir configuración previa
    git config --local --unset credential.helper 2>/dev/null || true
    
    # Configurar usuario
    git config user.email "zevachmk@gmail.com"
    git config user.name "Mike Orion Bot"
    
    # Configurar remote con token
    if git remote | grep -q origin; then
        git remote set-url origin "$GITHUB_URL"
    else
        git remote add origin "$GITHUB_URL"
    fi
    
    success "Git configurado con token"
}

# ================= 2. CREAR ARCHIVOS DE CONFIGURACIÓN =================
create_config_files() {
    log "Creando archivos de configuración..."
    
    # 2.1 Crear .env con Hotmart
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# ================= HOTMART API =================
HOTMART_CLIENT_ID=$HOTMART_CLIENT_ID
HOTMART_CLIENT_SECRET=$HOTMART_CLIENT_SECRET
HOTMART_BASIC_AUTH=YzlhZTlhODItZTQzNi00ZjI4LTgwYTgtNWUxOTVmMGY3ODE1OmQ2NTE2ZDc3LWRhZDYtNDY5NS05OGVlLTYxNzA1OTMzMTAwNA==

# ================= TELEGRAM (CONFIGURAR DESPUÉS) =================
# MULTIBOT_TELEGRAM_TOKEN=tu_token_multibot_aqui
# AFFILIATE_TELEGRAM_TOKEN=tu_token_afiliados_aqui

# ================= DATABASE =================
DATABASE_URL=sqlite:///neuraforge.db

# ================= APP =================
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=false
ENVIRONMENT=production
EOF
        success ".env creado (¡NO SUBIR A GITHUB!)"
    fi
    
    # 2.2 Crear .env.example para GitHub
    cat > .env.example << 'EOF'
# ================= HOTMART API =================
HOTMART_CLIENT_ID=tu_client_id_aqui
HOTMART_CLIENT_SECRET=tu_client_secret_aqui

# ================= TELEGRAM =================
MULTIBOT_TELEGRAM_TOKEN=tu_token_multibot_aqui
AFFILIATE_TELEGRAM_TOKEN=tu_token_afiliados_aqui

# ================= DATABASE =================
DATABASE_URL=sqlite:///neuraforge.db

# ================= APP =================
SECRET_KEY=genera_con_openssl_rand_hex_32
DEBUG=false
ENVIRONMENT=production
EOF
    
    # 2.3 Actualizar config.json
    if [ -f "config.json" ]; then
        cat > config.json << EOF
{
  "project_name": "NeuraForge AI",
  "version": "3.0.0",
  "owner": "Mike Orion Bot",
  "email": "zevachmk@gmail.com",
  "github": "https://github.com/Mike-orion-bot/neuraforge-ai",
  "ecosystem": {
    "revenue_sharing": true,
    "auto_funding": true,
    "community_voting": true,
    "hotmart_integrated": true
  },
  "apis": {
    "hotmart": {
      "client_id": "$HOTMART_CLIENT_ID",
      "configured": true
    },
    "telegram": {
      "multibot": false,
      "affiliate_bot": false
    },
    "bitso": {
      "configured": false
    }
  },
  "sync": {
    "last_sync": "$(date '+%Y-%m-%d %H:%M:%S')",
    "auto_sync": true,
    "frequency": "6h"
  }
}
EOF
        success "config.json actualizado"
    fi
}

# ================= 3. CREAR .GITIGNORE MEJORADO =================
create_gitignore() {
    log "Creando .gitignore mejorado..."
    
    cat > .gitignore << 'EOF'
# ================= SECRETS & CREDENTIALS =================
.env
.env.local
.secret
*.key
*.pem
*.crt
credentials.json
service-account.json

# ================= DATABASES =================
*.db
*.sqlite
*.sqlite3
*.db-journal
neuraforge.db
neuraforge_hive.db
data/*.db
!data/.gitkeep

# ================= LOGS =================
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# ================= BACKUPS =================
backups/
*.backup.*
*.bak

# ================= PYTHON =================
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

# ================= CACHE & TEMP =================
.cache/
.nox/
.coverage
.coverage.*
*,cover
.hypothesis/
.pytest_cache/
.mypy_cache/
.tox/
tmp/
temp/
*.tmp
*.temp

# ================= IDE =================
.vscode/
.idea/
*.swp
*.swo
*~

# ================= OS =================
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# ================= BUILD & DIST =================
dist/
build/
*.egg-info/
*.egg
*.whl
*.pyz
*.pyo
*.pyd

# ================= APK & BINARIES =================
*.apk
*.exe
*.dll
*.so
*.dylib
bin/

# ================= RAILWAY =================
.railway/
railway.toml

# ================= DOCKER =================
docker-compose.override.yml

# ================= PERSONAL =================
personal/
private/
secret/
keys/

# ================= STATIC ASSETS =================
static/apk/*.apk
static/uploads/
static/temp/

# ================= TEMPLATES CACHE =================
templates/__pycache__/
templates/*.pyc

# ================= SPECIFIC FILES =================
config.local.json
settings.local.py
admin.HTML.backup.*
EOF
    
    success ".gitignore creado"
}

# ================= 4. SINCRONIZAR CON GITHUB =================
sync_with_github() {
    log "Sincronizando con GitHub..."
    
    cd "$PROJECT_DIR"
    
    # 4.1 Agregar archivos importantes
    git add \
        bots/ \
        core/ \
        hotmart/ \
        templates/ \
        main_ecosystem.py \
        main_orchestrator.py \
        main.py \
        requirements.txt \
        railway.json \
        docker-compose.yml \
        config.json \
        .env.example \
        .gitignore \
        README.md 2>/dev/null || true
    
    # 4.2 Commit
    if git status --porcelain | grep -q "."; then
        git commit -m "Sync: $(date '+%Y-%m-%d %H:%M:%S') - Hotmart configurado"
        success "Commit creado"
    else
        warning "No hay cambios para commitear"
        return 0
    fi
    
    # 4.3 Pull antes de push
    log "Actualizando desde GitHub..."
    git pull origin "$BRANCH" --rebase --autostash || {
        warning "Posible conflicto, haciendo merge..."
        git pull origin "$BRANCH" --no-rebase
    }
    
    # 4.4 Push con token
    log "Subiendo a GitHub con token..."
    if git push origin "$BRANCH"; then
        success "✅ ¡Push exitoso a GitHub!"
        echo ""
        echo "🌐 Repositorio: https://github.com/$GITHUB_USER/$GITHUB_REPO"
        echo "🔗 URL con token: $GITHUB_URL"
    else
        error "Error en push"
        echo "Intentando con fuerza..."
        git push origin "$BRANCH" --force
    fi
}

# ================= 5. CONFIGURAR HOTMART =================
setup_hotmart() {
    log "Configurando Hotmart..."
    
    cd "$PROJECT_DIR"
    
    # Crear directorio hotmart si no existe
    mkdir -p hotmart
    
    # Crear archivo de configuración Hotmart
    cat > hotmart/config.py << EOF
#!/usr/bin/env python3
"""
CONFIGURACIÓN HOTMART - NeuraForge AI
"""

import os
import base64
from typing import Dict, Optional

class HotmartConfig:
    # Credenciales desde variables de entorno
    CLIENT_ID = os.getenv("HOTMART_CLIENT_ID", "$HOTMART_CLIENT_ID")
    CLIENT_SECRET = os.getenv("HOTMART_CLIENT_SECRET", "$HOTMART_CLIENT_SECRET")
    
    # URLs de API
    BASE_URL = "https://api.hotmart.com"
    AUTH_URL = f"{BASE_URL}/oauth/token"
    SALES_URL = f"{BASE_URL}/sales/rest/v2/historical"
    PRODUCTS_URL = f"{BASE_URL}/product/rest/v2"
    
    @classmethod
    def get_basic_auth(cls) -> str:
        """Genera Basic Auth header"""
        credentials = f"{cls.CLIENT_ID}:{cls.CLIENT_SECRET}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    @classmethod
    def get_headers(cls, access_token: Optional[str] = None) -> Dict:
        """Genera headers para requests"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        else:
            headers["Authorization"] = cls.get_basic_auth()
        
        return headers
    
    @classmethod
    def validate_config(cls) -> bool:
        """Valida que la configuración sea correcta"""
        if not cls.CLIENT_ID or cls.CLIENT_ID == "tu_client_id_aqui":
            print("❌ HOTMART_CLIENT_ID no configurado")
            return False
        
        if not cls.CLIENT_SECRET or cls.CLIENT_SECRET == "tu_client_secret_aqui":
            print("❌ HOTMART_CLIENT_SECRET no configurado")
            return False
        
        print("✅ Configuración Hotmart válida")
        print(f"   Client ID: {cls.CLIENT_ID[:10]}...")
        print(f"   Client Secret: {cls.CLIENT_SECRET[:10]}...")
        return True

if __name__ == "__main__":
    config = HotmartConfig()
    config.validate_config()
EOF
    
    # Crear script de prueba Hotmart
    cat > hotmart/test_connection.py << 'EOF'
#!/usr/bin/env python3
"""
PRUEBA DE CONEXIÓN HOTMART
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hotmart.config import HotmartConfig
import requests
import json

def test_hotmart_connection():
    """Prueba la conexión con Hotmart API"""
    print("🧪 Probando conexión con Hotmart...")
    
    # 1. Validar configuración
    if not HotmartConfig.validate_config():
        return False
    
    try:
        # 2. Obtener access token
        print("🔑 Obteniendo access token...")
        response = requests.post(
            HotmartConfig.AUTH_URL,
            headers=HotmartConfig.get_headers(),
            data={"grant_type": "client_credentials"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                print(f"✅ Token obtenido: {access_token[:50]}...")
                
                # 3. Probar endpoint de productos
                print("📦 Probando API de productos...")
                products_response = requests.get(
                    HotmartConfig.PRODUCTS_URL,
                    headers=HotmartConfig.get_headers(access_token)
                )
                
                if products_response.status_code == 200:
                    products = products_response.json()
                    print(f"✅ Conexión exitosa! Productos disponibles: {len(products.get('items', []))}")
                    return True
                else:
                    print(f"❌ Error productos: {products_response.status_code}")
                    return False
            else:
                print("❌ No se pudo obtener token")
                return False
        else:
            print(f"❌ Error auth: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    if test_hotmart_connection():
        print("\n🎉 ¡Hotmart configurado correctamente!")
        print("📊 Ahora puedes usar:")
        print("   • hotmart_integration.py - Para gestión de productos")
        print("   • affiliate_bot/ - Para bot de afiliados")
    else:
        print("\n⚠️  Revisa tu configuración en .env")
        print("💡 Asegúrate de que HOTMART_CLIENT_ID y HOTMART_CLIENT_SECRET sean correctos")
EOF
    
    chmod +x hotmart/test_connection.py
    success "Configuración Hotmart creada"
}

# ================= 6. CREAR README ACTUALIZADO =================
create_readme() {
    log "Creando README.md actualizado..."
    
    cat > README.md << 'EOF'
# 🚀 NeuraForge AI - Sistema Autosustentable

<div align="center">

![NeuraForge AI](https://img.shields.io/badge/NeuraForge-AI%20Ecosystem-blue)
![Version](https://img.shields.io/badge/Version-3.0-green)
![Hotmart](https://img.shields.io/badge/Hotmart-Integrated-orange)
![License](https://img.shields.io/badge/License-MIT-brightgreen)

**IAs → Ganancias → Financiamiento → Más IAs**

</div>

## 📋 Configuración Rápida

### 1. Credenciales Configuradas
- **GitHub**: `Mike-orion-bot/neuraforge-ai`
- **Hotmart**: Client ID y Secret ya configurados
- **Email**: zevachmk@gmail.com

### 2. Estructura del Proyecto
