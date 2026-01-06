import sqlite3
import asyncio
import logging
from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
from telegram import Bot
from telegram.error import TelegramError
import uvicorn

# --- CONFIGURACIÓN CRÍTICA ---
TOKEN_TELEGRAM = "TU_TOKEN_DE_TELEGRAM" # Reemplaza con el tuyo
ADMIN_PASSWORD = "neuraforge_admin_2026" # Tu clave para entrar al panel
DB_NAME = "neuraforge.db"

# Inicialización
bot = Bot(token=TOKEN_TELEGRAM)
app = FastAPI(title="NeuraForge Production Admin")
logger = logging.getLogger("NeuraForge")

# --- FUNCIONES DE BASE DE DATOS ---
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
                     is_active INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# --- INTERFAZ ADMINISTRATIVA (HTML) ---
@app.get("/admin/{password}", response_class=HTMLResponse)
async def admin_dashboard(password: str):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Acceso Denegado")
    
    conn = get_db_connection()
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NeuraForge PRO</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-black text-gray-200">
        <nav class="p-6 border-b border-gray-800 flex justify-between">
            <h1 class="text-xl font-bold text-blue-500">NEURAFORGE AI <span class="text-gray-500 text-xs">PROD v2.5</span></h1>
            <div class="text-right">
                <p class="text-xs text-gray-500">Usuarios Registrados</p>
                <p class="text-lg font-mono text-green-500">{total_users}</p>
            </div>
        </nav>
        
        <main class="p-8 max-w-4xl mx-auto">
            <div class="bg-gray-900 border border-gray-800 p-8 rounded-2xl shadow-2xl">
                <h2 class="text-2xl font-bold mb-6 italic text-blue-400">📢 Difusión del Manifiesto de Sueños</h2>
                <form action="/broadcast/{password}" method="post" class="space-y-6">
                    <div>
                        <label class="block text-sm mb-2 text-gray-400">Mensaje para la Comunidad:</label>
                        <textarea name="mensaje" required class="w-full bg-black border border-gray-700 rounded-xl p-4 text-white focus:border-blue-500 outline-none transition-all" rows="6" placeholder="Escribe aquí el anuncio importante..."></textarea>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg transition-transform transform active:scale-95">
                        DESPEGAR MENSAJE MASIVO
                    </button>
                </form>
            </div>
        </main>
    </body>
    </html>
    """

# --- LÓGICA DE ENVÍO REAL ---
@app.post("/broadcast/{password}")
async def broadcast_real(password: str, mensaje: str = Form(...)):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403)

    conn = get_db_connection()
    users = conn.execute('SELECT telegram_id FROM users WHERE is_active = 1').fetchall()
    conn.close()

    if not users:
        return HTMLResponse("<h2>No hay usuarios en la base de datos para enviar.</h2><a href='/admin/{password}'>Volver</a>")

    sent_count = 0
    error_count = 0

    # Envío asíncrono para no bloquear
    for user in users:
        try:
            await bot.send_message(chat_id=user['telegram_id'], text=mensaje, parse_mode='Markdown')
            sent_count += 1
            await asyncio.sleep(0.05) # Evitar spam-ban de Telegram
        except TelegramError as e:
            logger.error(f"Error enviando a {user['telegram_id']}: {e}")
            error_count += 1

    return HTMLResponse(f"""
        <body style="background: #000; color: #fff; font-family: sans-serif; padding: 50px; text-align: center;">
            <h1 style="color: #4ade80;">🚀 Proceso Completado</h1>
            <p>Enviados con éxito: {sent_count}</p>
            <p style="color: #f87171;">Errores/Bloqueos: {error_count}</p>
            <br>
            <a href="/admin/{password}" style="color: #3b82f6; text-decoration: none; border: 1px solid; padding: 10px 20px; border-radius: 5px;">Regresar al Panel</a>
        </body>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
