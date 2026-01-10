#!/data/data/com.termux/files/usr/bin/bash

echo "⚡ Iniciando Entorno NeuraForge AI..."

# 1. Asegurar que el procesador no se duerma
termux-wake-lock
echo "✅ Wake-lock activado (Procesador despierto)"

# 2. Verificar Red con Cloudflare WARP
if ping -c 1 1.1.1.1 &> /dev/null; then
    echo "🌐 Conexión Segura detectada."
else
    echo "⚠️ Advertencia: No hay conexión a internet o WARP está apagado."
fi

# 3. Lanzar el servidor en segundo plano
echo "🚀 Arrancando Servidor y Bot..."
python main.py
