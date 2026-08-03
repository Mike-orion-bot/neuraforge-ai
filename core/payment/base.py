"""
🔧 Base class para procesadores de pago
Interfaz común para todos los gateways
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BasePaymentProcessor(ABC):
    """Clase base para todos los procesadores de pago"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"payment.{name}")
    
    @abstractmethod
    async def create_payment_link(self, amount: float, currency: str, 
                                 description: str = "", 
                                 customer_email: str = None) -> Dict:
        """Crea un enlace de pago"""
        pass
    
    @abstractmethod
    async def verify_payment(self, payment_id: str) -> Dict:
        """Verifica estado de un pago"""
        pass
    
    @abstractmethod
    async def create_withdrawal(self, amount: float, currency: str, 
                               destination: str) -> Dict:
        """Crea un retiro"""
        pass
    
    def generate_reference(self, bot_id: str = "", prefix: str = "NF") -> str:
        """Genera referencia única"""
        import hashlib
        import time
        
        seed = f"{bot_id}:{time.time()}"
        reference = hashlib.md5(seed.encode()).hexdigest()[:8].upper()
        return f"{prefix}{int(time.time())}{reference}"
    
    def log_payment(self, level: str, message: str, **kwargs):
        """Registra evento de pago"""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_info}" if extra_info else message
        
        if level == "info":
            self.logger.info(full_message)
        elif level == "error":
            self.logger.error(full_message)
        elif level == "warning":
            self.logger.warning(full_message)
        else:
            self.logger.debug(full_message)
