#!/bin/bash
echo "🔍 VERIFICACIÓN DEL SISTEMA - $(date)"

echo ""
echo "=== PROCESOS ACTIVOS ==="
if pgrep -f "python3 sistema_monitoreo.py" > /dev/null; then
    echo "✅ sistema_monitoreo.py - ACTIVO (PID: $(pgrep -f 'python3 sistema_monitoreo.py'))"
else
    echo "❌ sistema_monitoreo.py - INACTIVO"
fi

if pgrep -f "webhook.*9000" > /dev/null; then
    echo "✅ webhook - ACTIVO (PID: $(pgrep -f 'webhook.*9000'))"
else
    echo "❌ webhook - INACTIVO"
fi

echo ""
echo "=== PUERTOS ==="
for port in 5000 9000; do
    if netstat -tulpn 2>/dev/null | grep ":$port" > /dev/null; then
        echo "✅ Puerto $port - EN USO"
    else
        echo "❌ Puerto $port - LIBRE"
    fi
done

echo ""
echo "=== LOGS RECIENTES ==="
if [ -f monitoreo.log ]; then
    echo "📄 monitoreo.log (últimas 3 líneas):"
    tail -3 monitoreo.log
else
    echo "📄 monitoreo.log - NO EXISTE"
fi

if [ -f webhook.log ]; then
    echo "📄 webhook.log (últimas 3 líneas):"
    tail -3 webhook.log
else
    echo "📄 webhook.log - NO EXISTE"
fi

echo ""
echo "=== ARCHIVOS NECESARIOS ==="
[ -f sistema_monitoreo.py ] && echo "✅ sistema_monitoreo.py" || echo "❌ sistema_monitoreo.py"
[ -f config/hooks.json ] && echo "✅ config/hooks.json" || echo "❌ config/hooks.json"
[ -f scripts/mercado_pago.sh ] && echo "✅ scripts/mercado_pago.sh" || echo "❌ scripts/mercado_pago.sh"

echo ""
echo "=== ACCESO WEB ==="
echo "🌐 Dashboard: http://localhost:5000"
echo "📊 Status API: http://localhost:5000/status"
echo "🔗 Webhook: http://localhost:9000/hooks/mercado-pago"
