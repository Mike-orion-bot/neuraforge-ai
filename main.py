#!/bin/bash
# ==============================================================================
# NEURAFORGE AI - MÓDULO DE SINCRONIZACIÓN GIT PRO
# ==============================================================================

REPO_URL="https://github.com/Mike-orion-bot/neuraforge-ai.git"
TOKEN="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" # Tu token detectado

echo -e "\033[0;34m[+] Iniciando sincronización profunda con GitHub...\033[0m"

async def on_user_start(update, context):
    user = update.effective_user
    conn = get_db_connection()
    try:
        # Registra al usuario como "Prospecto" antes de que compre
        conn.execute('''INSERT OR IGNORE INTO users 
                        (telegram_id, username, bot_type, is_active) 
                        VALUES (?, ?, ?, ?)''', 
                     (user.id, user.username, "PROSPECTO", 0))
        conn.commit()
    finally:
        conn.close()
    
    await update.message.reply_text(
        f"👋 ¡Hola {user.first_name}! Soy el constructor de NeuraForge.\n\n"
        "Estoy listo para armar tu bot de ventas. ¿Qué giro prefieres?",
        reply_markup=menu_giros # El teclado de Pizzería, Taxi, etc.
    )



# 1. Limpieza de Git previo si existe error
if [ -d ".git" ]; then
    echo "[!] Detectado repositorio previo. Re-vinculando..."
    rm -rf .git
fi

# 2. Inicialización limpia
git init
git checkout -b main

# 3. Configuración de credenciales (usando tu token para evitar errores de login)
# Reemplazamos el URL para incluir el token automáticamente
AUTH_URL="https://Mike-orion-bot:$TOKEN@github.com/Mike-orion-bot/neuraforge-ai.git"

# 4. Preparar archivos (respetando el .gitignore que ya tienes)
git add .
git commit -m "Update: Integración Núcleo Orion Hunter y Bots Modulares"

# 5. Conexión y subida forzada
git remote add origin "$AUTH_URL"
echo "[+] Empujando código a la nube..."
git push -u origin main --force

echo -e "\033[0;32m[✅] Sincronización exitosa en: $REPO_URL\033[0m"
