# backend/integration.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
from datetime import datetime

app = FastAPI()

@app.post("/api/check-module-access")
async def check_module_access(license_key: str, module_name: str):
    """Verifica si un módulo está activo para una licencia"""
    conn = sqlite3.connect("neuraforge.db")
    cursor = conn.cursor()
    
    # Verificar licencia
    cursor.execute('''
        SELECT status, expiration_date FROM licenses 
        WHERE license_key = ? AND status = 'active'
    ''', (license_key,))
    
    license_data = cursor.fetchone()
    if not license_data:
        return {"access": False, "reason": "Licencia inválida o expirada"}
    
    # Verificar módulo
    cursor.execute('''
        SELECT price, donation_required FROM modules 
        WHERE name = ? AND bot_type = 'sat'
    ''', (module_name,))
    
    module_data = cursor.fetchone()
    if not module_data:
        return {"access": False, "reason": "Módulo no encontrado"}
    
    price, donation_required = module_data
    
    # Verificar si el módulo requiere donación
    if donation_required:
        cursor.execute('''
            SELECT 1 FROM donations 
            WHERE license_key = ? AND module_name = ? AND status = 'completed'
        ''', (license_key, module_name))
        
        donation = cursor.fetchone()
        if not donation:
            return {
                "access": False,
                "reason": "Donación requerida",
                "price": price,
                "donation_url": f"/donate/{license_key}/{module_name}"
            }
    
    conn.close()
    return {"access": True, "module": module_name}

@app.post("/api/process-donation")
async def process_donation(license_key: str, module_name: str, amount: float, method: str):
    """Procesa una donación y activa un módulo"""
    # 1. Registrar donación
    conn = sqlite3.connect("neuraforge.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO donations (license_key, module_name, amount, method, status)
        VALUES (?, ?, ?, ?, 'completed')
    ''', (license_key, module_name, amount, method))
    
    # 2. Activar módulo
    cursor.execute('''
        INSERT OR REPLACE INTO active_modules (license_key, module_name, activated_at)
        VALUES (?, ?, ?)
    ''', (license_key, module_name, datetime.now()))
    
    conn.commit()
    conn.close()
    
    # 3. Enviar notificación al bot
    await notify_bot(license_key, module_name)
    
    return {
        "success": True,
        "message": f"Módulo {module_name} activado",
        "donation_amount": amount,
        "activation_time": datetime.now().isoformat()
    }

async def notify_bot(license_key: str, module_name: str):
    """Notifica al bot sobre nuevo módulo activado"""
    # Implementar notificación via webhook o Telegram
    pass
