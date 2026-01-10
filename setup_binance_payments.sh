#!/bin/bash
# setup_binance_payments.sh

echo "💰 CONFIGURANDO BINANCE PARA NEURAFORGE"
echo "======================================="

cd ~/neuraforge_ai

# Crear archivo de configuración
cat > .env.binance << EOF
# BINANCE API CONFIGURATION
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_API_SECRET=tu_api_secret_aqui
BINANCE_DEFAULT_CURRENCY=USDT
BINANCE_DEFAULT_NETWORK=BEP20
EOF

# Agregar al .env principal
if [ -f ".env" ]; then
    cat .env.binance >> .env
    echo "✅ Binance configurado en .env"
else
    cp .env.binance .env
    echo "✅ .env creado con configuración Binance"
fi

# Crear módulo Binance
mkdir -p core/payment

cat > core/payment/binance_processor.py << 'EOF'
# [Pega el código de BinanceProcessor aquí]
EOF

# Actualizar requirements.txt
echo "binance==1.0.16" >> requirements.txt

echo ""
echo "🎉 CONFIGURACIÓN BINANCE COMPLETADA"
echo ""
echo "📋 PASOS FINALES:"
echo "1. Ve a https://www.binance.com"
echo "2. Crea cuenta (si no tienes)"
echo "3. Ve a API Management y crea nueva API"
echo "4. Copia API Key y Secret en .env"
echo "5. Ejecuta: pip install binance"
echo ""
echo "🚀 Comandos de prueba:"
echo "   python -c \"from core.payment.binance_processor import BinanceProcessor; bp = BinanceProcessor(); print(bp.get_balances())\""
