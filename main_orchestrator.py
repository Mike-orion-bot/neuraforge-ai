# main_orchestrator.py
import asyncio
from modules.security.home_defender import HomeDefender
from modules.intelligence.osinbravo import OsinbravoNAI
from modules.marketing.growth_orchestrator import GrowthOrchestrator

async def start_neuraforge_entity():
    print("🦅 Iniciando Ojo de Águila...")
    eagle = OsinbravoNAI()
    
    print("🛡️ Activando Escudo Home Defender...")
    shield = HomeDefender()
    
    print("🎯 Lanzando Orquestador de Marketing...")
    # Aquí es donde el bot empieza a buscar clientes para ti
    marketing = GrowthOrchestrator(osint_tool=eagle)
    
    # Ejecución paralela de todos los servicios
    await asyncio.gather(
        marketing.watch_and_act(target_niche="emprendedores"),
        shield.monitor_running_processes()
    )

if __name__ == "__main__":
    try:
        asyncio.run(start_neuraforge_entity())
    except KeyboardInterrupt:
        print("🚨 Entidad en modo hibernación...")

