#!/data/data/com.termux/files/usr/bin/bash
# NEURAFORGE AI - PRODUCTION LAUNCHER

cd ~/neuraforge_ai

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════╗"
echo "║      🚀 NEURAFORGE AI - PRODUCTION MODE         ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# Función para verificar dependencias
check_requirements() {
    echo -e "${YELLOW}[1/5] Verificando dependencias...${NC}"
    
    # Python
    if ! command -v python3 &> /dev/null; then
        echo "Instalando Python..."
        pkg install python -y
    fi
    
    # Pip packages
    if [ -f "requirements.txt" ]; then
        echo "Instalando paquetes Python..."
        pip install -r requirements.txt --upgrade
    else
        # Paquetes básicos
        pip install flask requests sqlalchemy python-dotenv --upgrade
    fi
    
    echo -e "${GREEN}✅ Dependencias verificadas${NC}"
}

# Función para preparar entorno
prepare_environment() {
    echo -e "${YELLOW}[2/5] Preparando entorno...${NC}"
    
    # Crear directorios necesarios
    mkdir -p logs backups data
    
    # Verificar archivos de configuración
    if [ ! -f "config.json" ]; then
        echo "Creando config.json por defecto..."
        cat > config.json << EOF
{
    "environment": "production",
    "debug": false,
    "database_path": "neuraforge.db",
    "port": 5000,
    "api_keys": {
        "bitso": "your_bitso_api_key",
        "binance": "your_binance_api_key"
    },
    "security": {
        "encryption_key": "change_this_in_production",
        "jwt_secret": "another_secret_key"
    }
}
EOF
        echo -e "${YELLOW}⚠️  Config.json creado - REVISA LAS LLAVES${NC}"
    fi
    
    # Verificar base de datos
    if [ ! -f "neuraforge.db" ]; then
        echo -e "${YELLOW}⚠️  Base de datos no encontrada, se creará al iniciar${NC}"
    fi
    
    # Permisos
    chmod +x *.sh 2>/dev/null
    chmod +x *.py 2>/dev/null
    
    echo -e "${GREEN}✅ Entorno preparado${NC}"
}

# Función para detener servicios previos
stop_previous() {
    echo -e "${YELLOW}[3/5] Deteniendo servicios previos...${NC}"
    
    # Buscar y matar procesos NeuraForge
    pkill -f "python.*(main|neuraforge|ecosystem|orchestrator)" 2>/dev/null
    
    # Limpiar PID files
    rm -f .*.pid 2>/dev/null
    
    sleep 2
    echo -e "${GREEN}✅ Servicios previos detenidos${NC}"
}

# Función para iniciar ecosistema
start_ecosystem() {
    echo -e "${YELLOW}[4/5] Iniciando ecosistema...${NC}"
    
    echo "Selecciona modo de inicio:"
    echo "  1) 🌐 Modo Web (Flask/Dashboard)"
    echo "  2) 🤖 Modo Bots (Procesos en background)"
    echo "  3) 🔄 Modo Mixto (Web + Bots)"
    echo "  4) 🛠️  Modo Desarrollo (con logs detallados)"
    
    read -p "Opción [1-4]: " mode
    
    case $mode in
        1)
            echo "Iniciando servidor web..."
            nohup python3 main_ecosystem.py > logs/web_$(date +%Y%m%d_%H%M%S).log 2>&1 &
            WEB_PID=$!
            echo $WEB_PID > .web.pid
            ;;
        2)
            echo "Iniciando bots en background..."
            nohup python3 main_orchestrator.py > logs/bots_$(date +%Y%m%d_%H%M%S).log 2>&1 &
            BOTS_PID=$!
            echo $BOTS_PID > .bots.pid
            ;;
        3)
            echo "Iniciando modo mixto..."
            nohup python3 main_ecosystem.py > logs/full_$(date +%Y%m%d_%H%M%S).log 2>&1 &
            echo $! > .ecosystem.pid
            sleep 5
            nohup python3 main_orchestrator.py >> logs/full_$(date +%Y%m%d_%H%M%S).log 2>&1 &
            echo $! > .orchestrator.pid
            ;;
        4)
            echo "Iniciando modo desarrollo..."
            python3 main.py
            exit 0
            ;;
        *)
            echo "Opción inválida, iniciando modo web por defecto..."
            nohup python3 main_ecosystem.py > logs/default_$(date +%Y%m%d_%H%M%S).log 2>&1 &
            echo $! > .default.pid
            ;;
    esac
    
    echo -e "${GREEN}✅ Ecosistema iniciado${NC}"
}

# Función para monitorear estado
monitor_status() {
    echo -e "${YELLOW}[5/5] Monitoreando estado...${NC}"
    
    echo ""
    echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}🚀 NEURAFORGE AI - EN PRODUCCIÓN${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
    
    # Mostrar PIDs
    echo "📊 Procesos activos:"
    for pid_file in .*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat $pid_file)
            if ps -p $pid > /dev/null 2>&1; then
                service=$(echo $pid_file | sed 's/^\.//;s/\.pid$//')
                echo "  ✅ $service (PID: $pid) - ACTIVO"
            else
                echo "  ❌ $service (PID: $pid) - INACTIVO"
                rm $pid_file
            fi
        fi
    done
    
    # Verificar puertos
    echo -e "\n🔌 Puertos en uso:"
    netstat -tulpn 2>/dev/null | grep -E ":5000|:8000" || echo "  No se detectaron puertos web activos"
    
    # URLs disponibles
    echo -e "\n🌐 URLs disponibles:"
    echo "  • Dashboard:    http://localhost:5000"
    echo "  • API Status:   http://localhost:5000/status"
    echo "  • Admin Panel:  http://localhost:5000/admin"
    
    # Comandos útiles
    echo -e "\n🛠️  Comandos útiles:"
    echo "  • Ver logs:      tail -f logs/*.log"
    echo "  • Detener:       pkill -f python"
    echo "  • Reiniciar:     ./start_production.sh"
    echo "  • Sincronizar:   ./sync_neuraforge_fixed.sh"
    
    echo -e "\n📈 Sistema listo para producción!"
}

# Función principal
main() {
    check_requirements
    prepare_environment
    stop_previous
    start_ecosystem
    sleep 3
    monitor_status
}

# Ejecutar
main
