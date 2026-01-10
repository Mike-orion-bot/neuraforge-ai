#!/data/data/com.termux/files/usr/bin/bash

# NEURAFORGE AI - GIT SYNC PROFESIONAL
echo "🚀 NEURAFORGE AI - GIT SYNC PROFESIONAL"
echo "======================================="

# Configuración
REPO_DIR="$HOME/neuraforge_ai"
BACKUP_DIR="$REPO_DIR/backups"
LOG_DIR="$REPO_DIR/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Crear directorios necesarios
mkdir -p "$BACKUP_DIR" "$LOG_DIR"

# Función para loggear
log() {
    echo "[$(date '+%F %T')] $1" | tee -a "$LOG_DIR/sync.log"
}

# Función para backup
backup_system() {
    log "💾 Creando backup del sistema..."
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    
    # Excluir archivos grandes y temporales
    tar --exclude='__pycache__' \
        --exclude='*.log' \
        --exclude='*.db-journal' \
        -czf "$BACKUP_FILE" \
        -C "$REPO_DIR" .
    
    if [ $? -eq 0 ]; then
        log "✅ Backup creado: $(basename $BACKUP_FILE)"
        echo "$BACKUP_FILE" > "$BACKUP_DIR/latest_backup.txt"
    else
        log "❌ Error al crear backup"
        return 1
    fi
}

# Función para verificar git
check_git() {
    if ! command -v git &> /dev/null; then
        log "❌ Git no está instalado"
        pkg install git -y
    fi
    
    # Configurar git si es necesario
    git config --global user.email "sync@neuraforge.ai"
    git config --global user.name "NeuraForge Sync"
}

# Función para sincronizar con repositorio remoto
sync_with_remote() {
    cd "$REPO_DIR"
    
    # Verificar si es un repositorio git
    if [ ! -d .git ]; then
        log "📦 Inicializando repositorio git..."
        git init
        git add .
        git commit -m "Initial commit - $TIMESTAMP"
    fi
    
    # Agregar remoto (ajusta la URL)
    if ! git remote | grep -q origin; then
        log "🔗 Agregando repositorio remoto..."
        git remote add origin https://github.com/tu_usuario/neuraforge-ai.git
    fi
    
    # Sincronizar
    log "🔄 Sincronizando con remoto..."
    git add .
    git commit -m "Auto-sync $TIMESTAMP" || true
    git pull origin main --rebase || true
    git push origin main || log "⚠️  No se pudo hacer push, puede ser solo lectura"
    
    log "✅ Sincronización completada"
}

# Función para verificar dependencias
check_dependencies() {
    log "🔍 Verificando dependencias..."
    
    # Python y pip
    if ! command -v python3 &> /dev/null; then
        log "📦 Instalando Python..."
        pkg install python -y
    fi
    
    # Instalar requirements
    if [ -f "$REPO_DIR/requirements.txt" ]; then
        log "📦 Instalando dependencias Python..."
        pip install -r "$REPO_DIR/requirements.txt" --upgrade
    fi
    
    # Verificar servicios críticos
    for service in nginx redis sqlite3; do
        if ! command -v $service &> /dev/null 2>&1; then
            log "⚠️  $service no está instalado (opcional)"
        fi
    done
}

# Función para reparar permisos
fix_permissions() {
    log "🔧 Reparando permisos..."
    
    # Dar permisos de ejecución a scripts
    find "$REPO_DIR" -name "*.sh" -type f -exec chmod +x {} \;
    chmod +x "$REPO_DIR"/*.py 2>/dev/null || true
    
    # Permisos para la base de datos
    if [ -f "$REPO_DIR/neuraforge.db" ]; then
        chmod 644 "$REPO_DIR/neuraforge.db"
    fi
    
    log "✅ Permisos reparados"
}

# Función para verificar estado del sistema
check_system_status() {
    log "📊 Verificando estado del sistema..."
    
    # Verificar procesos activos
    echo "=== PROCESOS ACTIVOS ==="
    ps aux | grep -E "python.*(main|neuraforge)" | grep -v grep || echo "No hay procesos activos"
    
    # Verificar base de datos
    echo -e "\n=== BASE DE DATOS ==="
    if [ -f "$REPO_DIR/neuraforge.db" ]; then
        size=$(du -h "$REPO_DIR/neuraforge.db" | cut -f1)
        echo "neuraforge.db: $size"
        
        # Verificar integridad
        if command -v sqlite3 &> /dev/null; then
            sqlite3 "$REPO_DIR/neuraforge.db" "PRAGMA integrity_check;" 2>/dev/null | head -5
        fi
    else
        echo "❌ Base de datos no encontrada"
    fi
    
    # Verificar logs
    echo -e "\n=== LOGS RECIENTES ==="
    if [ -d "$LOG_DIR" ]; then
        ls -la "$LOG_DIR"/*.log 2>/dev/null | head -3
    fi
    
    # Verificar espacio
    echo -e "\n=== ESPACIO DISCO ==="
    df -h | grep -E "Filesystem|/data"
}

# Función para limpiar temporales
clean_temp_files() {
    log "🧹 Limpiando archivos temporales..."
    
    # Eliminar pycache
    find "$REPO_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    
    # Eliminar logs antiguos (>7 días)
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null
    
    # Eliminar backups antiguos (>30 días)
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete 2>/dev/null
    
    log "✅ Limpieza completada"
}

# Menú principal
show_menu() {
    echo ""
    echo "🎯 MENÚ DE SINCRONIZACIÓN NEURAFORGE"
    echo "====================================="
    echo "1) 🔄 Sincronizar completo (Backup + Git + Dependencias)"
    echo "2) 💾 Solo backup"
    echo "3) 📦 Solo dependencias"
    echo "4) 🔧 Solo reparar permisos"
    echo "5) 🧹 Solo limpiar temporales"
    echo "6) 📊 Ver estado del sistema"
    echo "7) 🚀 Iniciar ecosistema de producción"
    echo "8) 🛑 Detener ecosistema"
    echo "9) 📝 Ver logs"
    echo "0) ❌ Salir"
    echo ""
    read -p "Selecciona una opción [0-9]: " option
    
    case $option in
        1)
            backup_system
            check_git
            sync_with_remote
            check_dependencies
            fix_permissions
            ;;
        2) backup_system ;;
        3) check_dependencies ;;
        4) fix_permissions ;;
        5) clean_temp_files ;;
        6) check_system_status ;;
        7) start_production_ecosystem ;;
        8) stop_ecosystem ;;
        9) view_logs ;;
        0) echo "👋 Saliendo..."; exit 0 ;;
        *) echo "❌ Opción inválida" ;;
    esac
}

# Función para iniciar ecosistema de producción
start_production_ecosystem() {
    log "🚀 INICIANDO ECOSISTEMA DE PRODUCCIÓN"
    
    # Detener procesos previos
    stop_ecosystem
    
    # Iniciar servicios principales
    cd "$REPO_DIR"
    
    echo "📦 Servicios disponibles:"
    echo "  1) main.py (Sistema principal)"
    echo "  2) main_ecosystem.py (Ecosistema completo)"
    echo "  3) main_orchestrator.py (Orquestador)"
    echo "  4) Todos en modo producción"
    
    read -p "Selecciona opción [1-4]: " service_option
    
    case $service_option in
        1)
            log "▶️ Iniciando main.py..."
            nohup python3 main.py > "$LOG_DIR/main_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
            echo $! > "$REPO_DIR/.main.pid"
            ;;
        2)
            log "▶️ Iniciando main_ecosystem.py..."
            nohup python3 main_ecosystem.py > "$LOG_DIR/ecosystem_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
            echo $! > "$REPO_DIR/.ecosystem.pid"
            ;;
        3)
            log "▶️ Iniciando main_orchestrator.py..."
            nohup python3 main_orchestrator.py > "$LOG_DIR/orchestrator_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
            echo $! > "$REPO_DIR/.orchestrator.pid"
            ;;
        4)
            log "▶️ Iniciando TODOS los servicios..."
            # Iniciar en orden
            nohup python3 main_ecosystem.py > "$LOG_DIR/full_ecosystem.log" 2>&1 &
            echo $! > "$REPO_DIR/.full.pid"
            sleep 5
            nohup python3 main_orchestrator.py >> "$LOG_DIR/full_ecosystem.log" 2>&1 &
            ;;
        *)
            echo "❌ Opción inválida, iniciando ecosistema por defecto..."
            nohup python3 main_ecosystem.py > "$LOG_DIR/default_ecosystem.log" 2>&1 &
            echo $! > "$REPO_DIR/.default.pid"
            ;;
    esac
    
    # Esperar y verificar
    sleep 3
    check_running_services
    
    log "✅ Ecosistema iniciado en producción"
    echo "📊 Para ver logs: tail -f $LOG_DIR/*.log"
    echo "🌐 URL: http://localhost:5000 (si aplica)"
}

# Función para verificar servicios corriendo
check_running_services() {
    echo "=== SERVICIOS EN EJECUCIÓN ==="
    
    for pid_file in "$REPO_DIR"/.??*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if ps -p "$pid" > /dev/null 2>&1; then
                service_name=$(basename "$pid_file" | sed 's/^\.//;s/\.pid$//')
                echo "✅ $service_name (PID: $pid)"
            else
                echo "❌ $(basename "$pid_file") - PID $pid no encontrado"
                rm "$pid_file"
            fi
        fi
    done
    
    # Verificar procesos Python
    echo -e "\n=== PROCESOS PYTHON ACTIVOS ==="
    ps aux | grep -E "python.*(main|neuraforge)" | grep -v grep | awk '{print "  " $11 " (PID:" $2 ")"}'
}

# Función para detener ecosistema
stop_ecosystem() {
    log "🛑 Deteniendo ecosistema..."
    
    # Detener por PID files
    for pid_file in "$REPO_DIR"/.??*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid"
                echo "  Detenido PID $pid ($(basename $pid_file))"
            fi
            rm "$pid_file"
        fi
    done
    
    # Detener por nombre
    pkill -f "python.*(main_ecosystem|main_orchestrator|main.py)" 2>/dev/null
    
    sleep 2
    log "✅ Ecosistema detenido"
}

# Función para ver logs
view_logs() {
    echo "=== ÚLTIMOS LOGS ==="
    
    if [ -d "$LOG_DIR" ]; then
        latest_log=$(ls -t "$LOG_DIR"/*.log 2>/dev/null | head -1)
        if [ -n "$latest_log" ]; then
            echo "📄 Mostrando: $(basename $latest_log)"
            echo "========================================"
            tail -20 "$latest_log"
        else
            echo "No hay logs disponibles"
        fi
    else
        echo "Directorio de logs no encontrado"
    fi
    
    echo ""
    read -p "¿Ver log completo? (s/n): " view_full
    if [[ "$view_full" == "s" || "$view_full" == "S" ]]; then
        cat "$latest_log"
    fi
}

# MAIN EXECUTION
main() {
    # Verificar que estamos en el directorio correcto
    if [ ! -f "$REPO_DIR/main.py" ] && [ ! -f "$REPO_DIR/main_ecosystem.py" ]; then
        echo "❌ No estás en el directorio correcto de NeuraForge AI"
        echo "💡 Ejecuta: cd ~/neuraforge_ai"
        exit 1
    fi
    
    # Mostrar banner
    echo ""
    echo "███████╗███╗   ██╗██╗   ██╗██████╗  █████╗ "
    echo "██╔════╝████╗  ██║██║   ██║██╔══██╗██╔══██╗"
    echo "█████╗  ██╔██╗ ██║██║   ██║██████╔╝███████║"
    echo "██╔══╝  ██║╚██╗██║██║   ██║██╔══██╗██╔══██║"
    echo "███████╗██║ ╚████║╚██████╔╝██║  ██║██║  ██║"
    echo "╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝"
    echo "            AI ECOSYSTEM v2.0"
    echo ""
    
    # Mostrar menú
    show_menu
    
    # Preguntar si continuar
    echo ""
    read -p "¿Continuar con otra operación? (s/n): " continue
    if [[ "$continue" == "s" || "$continue" == "S" ]]; then
        main
    else
        echo "👋 Saliendo..."
        check_running_services
    fi
}

# Ejecutar main
main
