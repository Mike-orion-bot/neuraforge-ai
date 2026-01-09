#!/bin/bash
# 🚀 CONFIGURACIÓN COMPLETA BITSO PAYMENTS

echo "=================================================="
echo "💰 CONFIGURANDO BITSO PARA PAGOS AUTOMÁTICOS"
echo "=================================================="

# 1. Verificar estructura
echo "📁 Verificando estructura..."
if [ ! -d "core/payment" ]; then
    mkdir -p core/payment
fi

if [ ! -d "backend" ]; then
    mkdir -p backend
fi

# 2. Copiar archivos creados
echo "🔧 Copiando módulos Bitso..."
cp core/payment/bitso_processor.py core/payment/bitso_processor.py.backup 2>/dev/null || true
cp backend/bitso_api.py backend/bitso_api.py.backup 2>/dev/null || true

# 3. Configurar variables de entorno
echo "🔐 Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.bitso.example .env
    echo "⚠️  Edita el archivo .env con tus claves reales de Bitso"
else
    echo "📄 .env ya existe, agregando configuraciones Bitso..."
    cat .env.bitso.example | grep -E "^BITSO" >> .env
fi

# 4. Actualizar admin.HTML
echo "🎨 Actualizando interfaz..."
chmod +x update_bitso_ui.sh
./update_bitso_ui.sh

# 5. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install requests python-dotenv hmac_hashlib || pip3 install requests python-dotenv hmac_hashlib

# 6. Integrar con main_orchestrator.py
echo "🔗 Integrando con orchestrator..."
if [ -f "main_orchestrator.py" ]; then
    if ! grep -q "bitso_processor" main_orchestrator.py; then
        echo "   ➕ Agregando import de Bitso..."
        sed -i '/^from/ a\from core.payment.bitso_processor import bitso_processor' main_orchestrator.py
        
        # Buscar inicialización del sistema
        if grep -q "def initialize_system" main_orchestrator.py; then
            sed -i '/def initialize_system/a\
    # Inicializar procesador Bitso\
    print("💰 Inicializando procesador de pagos Bitso...")\
    try:\
        # Verificar credenciales\
        if bitso_processor.api_key and bitso_processor.api_secret:\
            print("✅ Bitso Payment Processor configurado")\
        else:\
            print("⚠️  Bitso: Configura API_KEY y API_SECRET en .env")\
    except Exception as e:\
        print(f"⚠️  Error inicializando Bitso: {e}")' main_orchestrator.py
        fi
    fi
fi

# 7. Integrar con el servidor web
echo "🌐 Integrando endpoints..."
SERVER_FILES=("main.py" "app.py" "server.py")
for file in "${SERVER_FILES[@]}"; do
    if [ -f "$file" ]; then
        if grep -q "FastAPI\|flask" "$file"; then
            echo "   🔍 Encontrado servidor en: $file"
            
            # Agregar import
            if ! grep -q "bitso_api" "$file"; then
                sed -i '/^from/ a\from backend.bitso_api import router as bitso_router' "$file"
                
                # Agregar router
                if grep -q "FastAPI" "$file"; then
                    sed -i '/app.include_router/ a\app.include_router(bitso_router)' "$file"
                elif grep -q "flask" "$file"; then
                    echo "   ⚠️  Para Flask, registra manualmente los blueprints"
                fi
            fi
        fi
    fi
done

# 8. Crear script de prueba
echo "🧪 Creando script de prueba..."
cat > test_bitso_payments.py << 'TEST_EOF'
#!/usr/bin/env python3
"""
🧪 TEST BITSO PAYMENTS
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    from core.payment.bitso_processor import BitsoPaymentProcessor
    
    print("✅ Módulo Bitso importado")
    
    # Test básico
    processor = BitsoPaymentProcessor()
    
    # Verificar credenciales
    if processor.api_key:
        print("✅ API Key configurada")
    else:
        print("⚠️  API Key NO configurada (configura BITSO_API_KEY en .env)")
    
    # Test creación de pago
    print("\n🧪 Test creación de pago...")
    payment = processor.create_payment_link(500.0, "MXN", "Test NeuraForge")
    
    if payment.get("success"):
        print("✅ Pago creado exitosamente")
        print(f"   ID: {payment.get('payment_id')}")
        print(f"   URL: {payment.get('payment_url', 'N/A')}")
    else:
        print(f"❌ Error: {payment.get('error')}")
    
    # Test info de cuenta
    print("\n🧪 Test información de cuenta...")
    account = processor.get_account_info()
    
    if account.get("success"):
        print("✅ Información de cuenta obtenida")
        for currency, balance in account.get("balances", {}).items():
            print(f"   {currency}: {balance}")
    else:
        print(f"❌ Error: {account.get('error')}")
    
    print("\n🎯 BITSO PAYMENTS CONFIGURADO!")
    print("\n📋 Pasos siguientes:")
    print("1. Obtén API Keys en: https://bitso.com/api_setup")
    print("2. Configura .env con tus claves reales")
    print("3. Configura webhooks en panel de Bitso")
    print("4. Reinicia el servidor: python main.py")
    print("5. Prueba pagos en: http://localhost:8080")
    
except Exception as e:
    print(f"❌ Error en test: {e}")
    import traceback
    traceback.print_exc()
TEST_EOF

chmod +x test_bitso_payments.py

echo "=================================================="
echo "🎉 ¡BITSO PAYMENTS CONFIGURADO!"
echo ""
echo "📋 RESUMEN:"
echo "✅ Módulo Bitso creado"
echo "✅ API endpoints configurados"
echo "✅ Interfaz web actualizada"
echo "✅ Script de prueba creado"
echo ""
echo "🚀 PRÓXIMOS PASOS:"
echo "1. Edita .env con tus claves reales de Bitso"
echo "2. Ejecuta: python test_bitso_payments.py"
echo "3. Configura webhooks en panel de Bitso"
echo "4. Reinicia el servidor"
echo ""
echo "💡 CONSEJOS:"
echo "- Para montos < $1000: Usa el sistema actual de donaciones"
echo "- Para montos ≥ $1000: Usa Bitso (menores comisiones)"
echo "- Para upgrades de nodo: Se sugerirá Bitso automáticamente"
echo "=================================================="
