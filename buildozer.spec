[app]
# (str) Título de tu aplicación
title = Chatbot Advance by NeuraforgeAI

# (str) Nombre del paquete (identificador único)
package.name = nfa_advance

# (str) Dominio de la organización
package.domain = ai.neuraforge

# (str) Versión
version = 1.0.0

# (list) Extensiones de archivos a incluir
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Permisos de Android (Vital para marketing y notificaciones)
android.permissions = INTERNET, ACCESS_NETWORK_STATE, RECEIVE_BOOT_COMPLETED, VIBRATE

# (list) Requerimientos (Copia los de tu requirements.txt)
requirements = python3, kivy, requests, certifi, firebase-admin

# (str) Icono de la App (Si tienes uno en tu carpeta static)
# icon.filename = %(source.dir)s/static/logo.png

# (str) Orientación
orientation = portrait
