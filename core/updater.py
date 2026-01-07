# core/updater.py
import os
import subprocess

async def check_for_updates():
    """La entidad revisa si hay mejoras en el servidor central (GitHub)"""
    try:
        # Ejecuta un 'git pull' de forma silenciosa
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        if "Already up to date" not in result.stdout:
            print("🚀 Mejora detectada. Reiniciando núcleo evolutivo...")
            os.system("python main.py") # El bot se reinicia solo con el nuevo código
    except Exception as e:
        print(f"⚠️ Error en auto-actualización: {e}")
