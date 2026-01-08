# core/provisioner.py
import uuid

class BusinessProvisioner:
    def create_client_environment(self, business_name, plan_type):
        client_id = str(uuid.uuid4())[:8]
        print(f"🛠️ Creando entorno para: {business_name} (ID: {client_id})")
        
        # 1. Crear esquema de base de datos aislado
        self.init_db(client_id)
        
        # 2. Asignar módulos según el plan
        modules = self.assign_modules(plan_type)
        
        # 3. Notificar al usuario vía Push
        self.send_welcome_push(client_id)
        
        return {"status": "success", "url": f"https://{business_name}.neuraforge.ai"}

    def assign_modules(self, plan):
        config = {
            "marketing": True if plan == "full" else False,
            "inventory": True if "pro" in plan else False
        }
        return config
