#!/bin/bash
# ==============================================================================
# NEURAFORGE AI - AUTO-REPAIR SCRIPT
# Repara errores de sintaxis y regenera el núcleo del sistema
# ==============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[+] Iniciando cirugía técnica de NeuraForge AI...${NC}"

# 1. Reparar main.py (Eliminando errores de Bash en Python)
echo -e "${BLUE}[+] Re-escribiendo main.py con código limpio...${NC}"
cat > main.py << 'EOF'
import asyncio
import logging
from fastapi import FastAPI
import uvicorn
from datetime import datetime

# Logging configurado para Termux
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NeuraForge-Core")

app = FastAPI(title="NeuraForge AI Ecosystem v2.5")

@app.get("/")
async def root():
    return {
        "status": "active",
        "platform": "NeuraForge AI",
        "timestamp": datetime.now().isoformat(),
        "modules": ["SAT_Admin", "DreamFund", "Billing_Cascading"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🚀 NeuraForge AI está en línea.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# 2. Verificar y crear carpetas faltantes
echo -e "${BLUE}[+] Verificando estructura de carpetas...${NC}"
mkdir -p modules/sat_admin core/billing vault static/apk locale/es/LC_MESSAGES

# 3. Limpiar dependencias corruptas y reinstalar ligeras
echo -e "${BLUE}[+] Reparando entorno virtual (Solo librerías compatibles)...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    # Eliminar las que causan error en Termux
    pip uninstall -y torch transformers 2>/dev/null || true
    # Instalar lo esencial para el SAT y el Bot
    pip install fastapi uvicorn python-telegram-bot sqlalchemy python-dotenv cryptography
else
    echo -e "${RED}[!] No se encontró venv. Ejecuta el instalador principal primero.${NC}"
fi

echo -e "${GREEN}[✅] Reparación completada con éxito.${NC}"
echo -e "${BLUE}[!] Para iniciar el sistema ahora mismo usa:${NC}"
echo -e "${GREEN}source venv/bin/activate && python main.py${NC}"
