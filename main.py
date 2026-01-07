import sqlite3
import asyncio
import logging
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import TelegramError
import uvicorn

# --- CONFIGURACIÓN ---
TOKEN_TELEGRAM = "TU_TOKEN_AQUÍ" # <--- Pon tu Token real de BotFather
ADMIN_PASSWORD = "neuraforge_admin_2026"
DB_NAME = "neuraforge.db"

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NeuraForge")

# --- BASE DE DATOS ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     telegram_id TEXT UNIQUE, 
                     username TEXT, 
                     bot_type TEXT DEFAULT 'PROSPECTO',
                     is_active INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# --- LÓGICA DEL BOT (Registro de Clientes) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = get_db_connection()
    try:
        conn.execute('''INSERT OR IGNORE INTO users (telegram_id, username) 
                        VALUES (?, ?)''', (user.id, user.username))
        conn.commit()
    finally:
        conn.close()

    await update.message.reply_text(
        f"👋 ¡Hola {user.first_name}! Bienvenido a NeuraForge AI.\n"
        "Estamos listos para automatizar tu negocio. Pronto un asesor te contactará."
    )

# --- SERVIDOR WEB (Panel de Control) ---
app = FastAPI(title="NeuraForge Admin")

@app.get("/admin/{password}", response_class=HTMLResponse)
async def admin_dashboard(password: str):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Acceso Denegado")
    
    conn = get_db_connection()
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()

    return f"""
    <html>
    <head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-black text-white p-10">
        <h1 class="text-2xl text-blue-500 font-bold">NEURAFORGE AI - PANEL PRO</h1>
        <p class="mt-4">Usuarios en Base de Datos: <span class="text-green-400">{total_users}</span></p>
        <div class="mt-10 p-6 bg-gray-900 rounded-xl">
            <h2 class="text-xl mb-4 text-blue-300">Enviar Mensaje Masivo</h2>
            <form action="/broadcast/{password}" method="post">
                <textarea name="mensaje" class="w-full p-4 bg-black border border-gray-700 rounded text-white" rows="5"></textarea>
                <button type="submit" class="mt-4 bg-blue-600 px-6 py-2 rounded">DESPEGAR</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/broadcast/{password}")
async def broadcast_real(password: str, mensaje: str = Form(...)):
    if password != ADMIN_PASSWORD: raise HTTPException(status_code=403)
    
    bot_sender = Bot(token=TOKEN_TELEGRAM)
    conn = get_db_connection()
    users = conn.execute('SELECT telegram_id FROM users WHERE is_active = 1').fetchall()
    conn.close()

    sent, errors = 0, 0
    for user in users:
        try:
            await bot_sender.send_message(chat_id=user['telegram_id'], text=mensaje)
            sent += 1
            await asyncio.sleep(0.05)
        except: errors += 1

    return HTMLResponse(f"<h1>Enviados: {sent} | Errores: {errors}</h1><a href='/admin/{password}'>Volver</a>")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Iniciar el bot en segundo plano
    # (Para producción real, se recomienda usar procesos separados, pero esto funciona para demos)
    uvicorn.run(app, host="0.0.0.0", port=8000)

