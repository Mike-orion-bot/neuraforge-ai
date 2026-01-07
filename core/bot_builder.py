import sqlite3
import json

def save_bot_configuration(telegram_id, business_type, modules_list):
    """Guarda la configuración personalizada del usuario en la DB"""
    conn = sqlite3.connect("neuraforge.db")
    cursor = conn.cursor()
    
    # Convertimos la lista de módulos a JSON para guardarla
    modules_json = json.dumps(modules_list)
    
    cursor.execute('''
        UPDATE users 
        SET metadata = ?, plan = ?
        WHERE telegram_id = ?
    ''', (modules_json, business_type, telegram_id))
    
    conn.commit()
    conn.close()
    return True
