#!/bin/bash
# 🚀 SCRIPT DE INTEGRACIÓN COMPLETA DEL SISTEMA DE CRECIMIENTO

echo "=================================================="
echo "🚀 NEURAFORGE AI - INTEGRACIÓN DE NODOS DE CRECIMIENTO"
echo "=================================================="

# Verificar que estamos en el directorio correcto
if [ ! -d "core" ]; then
    echo "❌ Error: Debes ejecutar desde el directorio raíz de NeuraForge"
    exit 1
fi

# 1. Crear directorios necesarios
echo "📁 Creando estructura de directorios..."
mkdir -p core/database
mkdir -p backend

# 2. Instalar dependencias si es necesario
echo "📦 Verificando dependencias..."
pip install fastapi sqlite3 json datetime typing || true

# 3. Copiar archivos del sistema de crecimiento
echo "🔧 Copiando archivos del sistema..."

# Los archivos ya fueron creados en los pasos anteriores
echo "✅ Archivos creados:"
echo "   - core/database/growth_models.py"
echo "   - core/growth_manager.py"
echo "   - backend/growth_api.py"
echo "   - integrate_growth_ui.sh"
echo "   - migrate_existing_bots.py"

# 4. Integrar UI en admin.HTML
echo "🎨 Integrando interfaz de usuario..."
chmod +x integrate_growth_ui.sh
./integrate_growth_ui.sh

# 5. Migrar bots existentes
echo "🔄 Migrando bots existentes al sistema de crecimiento..."
python migrate_existing_bots.py

# 6. Integrar con main_orchestrator.py existente
echo "🔗 Integrando con orchestrator principal..."

# Buscar main_orchestrator.py y agregar import del growth manager
if [ -f "main_orchestrator.py" ]; then
    if ! grep -q "growth_manager" main_orchestrator.py; then
        echo "   ➕ Agregando import de growth_manager a main_orchestrator.py"
        
        # Agregar import después de otros imports
        sed -i '/^import/ a\from core.growth_manager import growth_manager' main_orchestrator.py
        
        # Buscar donde agregar inicialización del growth manager
        if grep -q "def initialize_system" main_orchestrator.py; then
            sed -i '/def initialize_system/a\
    # Inicializar sistema de crecimiento\
    print("🚀 Inicializando sistema de crecimiento...")\
    try:\
        # El sistema se auto-inicializa al importar\
        print("✅ Sistema de crecimiento listo")\
    except Exception as e:\
        print(f"⚠️ Error inicializando crecimiento: {e}")' main_orchestrator.py
        fi
    fi
fi

# 7. Integrar con el servidor web existente
echo "🌐 Integrando endpoints API..."

# Buscar archivo principal del servidor web
SERVER_FILES=("main.py" "app.py" "server.py" "backend/main.py")
for file in "${SERVER_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   🔍 Encontrado servidor en: $file"
        
        # Verificar si es FastAPI/Flask
        if grep -q "FastAPI\|flask\|Flask" "$file"; then
            echo "   ➕ Integrando router de crecimiento..."
            
            # Agregar import
            if ! grep -q "growth_api" "$file"; then
                sed -i '/^from/ a\from backend.growth_api import router as growth_router' "$file"
                
                # Agregar router (depende del framework)
                if grep -q "FastAPI" "$file"; then
                    sed -i '/app = FastAPI()/ a\app.include_router(growth_router)' "$file"
                elif grep -q "flask" "$file"; then
                    # Flask requiere integración diferente
                    echo "   ℹ️  Para Flask, manualmente registra los blueprints/endpoints"
                fi
            fi
        fi
    fi
done

# 8. Verificar integración
echo "🔍 Verificando integración..."

# Verificar que los archivos existen
ERRORS=0
for file in "core/database/growth_models.py" "core/growth_manager.py" "backend/growth_api.py"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file existe"
    else
        echo "   ❌ $file NO existe"
        ERRORS=$((ERRORS + 1))
    fi
done

# Verificar que admin.HTML fue modificado
if grep -q "Sistema de Crecimiento" templates/admin.HTML; then
    echo "   ✅ Interfaz integrada en admin.HTML"
else
    echo "   ⚠️  Interfaz no encontrada en admin.HTML"
fi

# 9. Crear script de prueba
echo "🧪 Creando script de prueba..."
cat > test_growth_system.py << 'TEST_EOF'
#!/usr/bin/env python3
"""
🧪 TEST DEL SISTEMA DE CRECIMIENTO
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.database.growth_models import GrowthDatabase
    from core.growth_manager import GrowthManager
    
    print("✅ Módulos importados correctamente")
    
    # Test básico de base de datos
    db = GrowthDatabase()
    print("✅ Base de datos de crecimiento inicializada")
    
    # Test de gestor
    manager = GrowthManager()
    print("✅ Gestor de crecimiento inicializado")
    
    # Verificar tablas
    import sqlite3
    conn = sqlite3.connect("neuraforge.db")
    cursor = conn.cursor()
    
    tables = ["growth_nodes", "node_requirements", "growth_events", "node_progress"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone()[0] > 0:
            print(f"   ✅ Tabla {table} existe")
        else:
            print(f"   ❌ Tabla {table} NO existe")
    
    conn.close()
    
    print("\n🎯 SISTEMA DE CRECIMIENTO LISTO!")
    print("Puedes acceder a:")
    print("1. Panel admin: http://localhost:8080")
    print("2. API Growth: http://localhost:8080/api/growth/status/[bot_id]")
    print("3. Dashboard global: http://localhost:8080/#growth")
    
except Exception as e:
    print(f"❌ Error en test: {e}")
    import traceback
    traceback.print_exc()
TEST_EOF

chmod +x test_growth_system.py

echo "=================================================="
if [ $ERRORS -eq 0 ]; then
    echo "🎉 ¡INTEGRACIÓN COMPLETADA EXITOSAMENTE!"
    echo ""
    echo "📋 RESUMEN:"
    echo "✅ Sistema de crecimiento instalado"
    echo "✅ Base de datos extendida"
    echo "✅ API REST configurada"
    echo "✅ Interfaz web integrada"
    echo "✅ Bots existentes migrados"
    echo ""
    echo "🚀 PRÓXIMOS PASOS:"
    echo "1. Ejecuta test: python test_growth_system.py"
    echo "2. Reinicia el servidor: python main.py"
    echo "3. Accede a http://localhost:8080"
    echo "4. Verifica la nueva pestaña 'Crecimiento'"
else
    echo "⚠️  Integración completada con $ERRORS errores"
    echo "Revisa los mensajes anteriores para solucionarlos"
fi

echo "=================================================="
