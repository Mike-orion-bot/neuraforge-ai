#!/bin/bash
# Script de inicio NeuraForge AI v2.5

echo "🚀 Iniciando motores de NeuraForge AI..."

# 1. Instalar dependencias (por si acaso)
pip install -r requirements.txt

# 2. Configurar la clave maestra si no existe
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY="NF_$(openssl rand -hex 16)"
    echo "🔑 Nueva Secret Key generada para esta sesión."
fi

# 3. Lanzar el servidor con Uvicorn
# Puerto 8000, 4 trabajadores para manejar múltiples donaciones al mismo tiempo
echo "🌐 Panel administrativo disponible en puerto 8000"
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4


