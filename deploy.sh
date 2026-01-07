#!/data/data/com.termux/files/usr/bin/bash

# --- CONFIGURACIÓN ---
NUBE_RCLONE="nube_nfa"  # El nombre que le pusiste en rclone config
FECHA=$(date '+%Y-%m-%d %H:%M:%S')

echo "🚀 Iniciando Protocolo de Despliegue NeuraForgeAI..."

# 1. Actualizar lista de requerimientos (Vital para que otros puedan instalar tu app)
echo "📦 Actualizando requirements.txt..."
pip freeze > requirements.txt

# 2. GITHUB: Subida de código
echo "🐙 Sincronizando con GitHub..."
git add .
git commit -m "Update Auto: $FECHA - Mejoras de Core y Seguridad"

if git push origin main; then
    GIT_STATUS="✅ GitHub OK"
else
    GIT_STATUS="⚠️ GitHub Error"
fi

# 3. NUBE: Respaldo cifrado/privado (Rclone)
echo "☁️  Sincronizando con Nube Privada..."
if rclone sync ~/neuraforge_ai $NUBE_RCLONE:NeuraForge_Backup; then
    CLOUD_STATUS="✅ Nube OK"
else
    CLOUD_STATUS="⚠️ Nube Error"
fi

# 4. NOTIFICACIÓN FINAL (Al celular)
# Esto te avisa a la barra de notificaciones el resultado final
termux-notification \
    --title "NeuraForgeAI: Despliegue Completado" \
    --content "$GIT_STATUS | $CLOUD_STATUS | $FECHA" \
    --priority high

echo "🏁 Proceso terminado: $GIT_STATUS | $CLOUD_STATUS"
