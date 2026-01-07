# core/factory.py
import importlib

class BotFactory:
    @staticmethod
    def create_bot(bot_type, extra_modules=[]):
        # 1. Cargar el núcleo (Taxi, SAT o Pizza)
        core_module = importlib.import_module(f"templates.{bot_type}_core")
        bot_instance = core_module.get_instance()
        
        # 2. Inyectar módulos adicionales dinámicamente
        for mod_name in extra_modules:
            addon = importlib.import_module(f"modules.{mod_name}")
            bot_instance.add_extension(addon.extension)
            
        return bot_instance
