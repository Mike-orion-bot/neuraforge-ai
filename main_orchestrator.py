#!/usr/bin/env python3
"""
ORCHESTRATOR PRINCIPAL - NeuraForge AI
Coordina todos los módulos y servicios
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/neuraforge.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class NeuraForgeOrchestrator:
    def __init__(self):
        self.modules = {}
        self.version = "3.1.0"
        
    async def start_all(self):
        """Inicia todos los módulos"""
        logger.info(f"🚀 Iniciando NeuraForge AI v{self.version}")
        
        try:
            # Importar módulos dinámicamente
            from core.station import StationManager
            from core.bot_builder import BotFactory
            from core.security.id_system import SecureIDSystem
            from core.payment.crypto_gateway import CryptoPaymentGateway
            
            # Inicializar módulos
            self.modules['station'] = StationManager()
            self.modules['factory'] = BotFactory()
            self.modules['security'] = SecureIDSystem()
            self.modules['payment'] = CryptoPaymentGateway()
            
            # Iniciar servicios
            await self.modules['station'].initialize()
            await self.modules['factory'].start_bot_factory()
            
            logger.info("✅ Todos los módulos iniciados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando módulos: {e}")
            return False
    
    async def run(self):
        """Ejecuta el orchestrator principal"""
        if not await self.start_all():
            logger.error("No se pudieron iniciar los módulos")
            return
        
        # Mantener el sistema corriendo
        try:
            logger.info("✅ Sistema operativo. Presiona Ctrl+C para detener.")
            
            # Tarea infinita para mantener activo
            while True:
                await asyncio.sleep(3600)  # Esperar 1 hora
                
        except KeyboardInterrupt:
            logger.info("🛑 Sistema detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error crítico: {e}")

# Punto de entrada
if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    if not Path("core").exists():
        print("❌ Error: Ejecuta desde el directorio neuraforge_ai")
        sys.exit(1)
    
    # Crear logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Iniciar
    orchestrator = NeuraForgeOrchestrator()
    
    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        print("\n👋 Hasta pronto!")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
