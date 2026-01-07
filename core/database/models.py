# Definición de la "Plantilla" y el "Número de Serie"
class BotLicense:
    def __init__(self, serial_number, owner_id, template_type):
        self.serial_number = serial_number  # Ej: NF-SAT-2026-XXXX
        self.owner_id = owner_id
        self.template_type = template_type  # SAT, Taxi, Pizza, Afiliados
        self.is_active = False
        self.modules = [] # Aquí se guardan los "Módulos Extra"

# Ejemplo de como se vería en SQLite:
# TABLE licenses:
# | Serial_ID (PK) | User_ID | Template_ID | Status | Created_At |
# | NF-SAT-101     | 558291  | SAT_PRO     | PAID   | 2026-01-06 |
