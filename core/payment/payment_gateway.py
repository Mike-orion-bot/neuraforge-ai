#!/usr/bin/env python3
"""
PAYMENT GATEWAY UNIFICADO - Soporta múltiples procesadores
"""

from enum import Enum
from typing import Dict, Optional
from decimal import Decimal

class PaymentProvider(Enum):
    BINANCE = "binance"
    BITSO = "bitso"
    MERCADOPAGO = "mercadopago"
    PAYPAL = "paypal"
    STRIPE = "stripe"

class UnifiedPaymentGateway:
    """Gateway unificado para todos los métodos de pago"""
    
    def __init__(self, provider: PaymentProvider = PaymentProvider.BINANCE):
        self.provider = provider
        self.processor = self._get_processor()
    
    def _get_processor(self):
        """Obtiene el procesador según provider"""
        if self.provider == PaymentProvider.BINANCE:
            from .binance_processor import BinanceProcessor
            return BinanceProcessor()
        elif self.provider == PaymentProvider.BITSO:
            from .bitso_processor import BitsoProcessor
            return BitsoProcessor()
        # Agregar más providers aquí
        
    def create_payment(self, amount: Decimal, currency: str, 
                      metadata: Dict = None) -> Dict:
        """Crea un pago"""
        return self.processor.create_payment(amount, currency, metadata)
    
    def process_payout(self, to_address: str, amount: Decimal, 
                      currency: str = "USDT") -> Dict:
        """Procesa un pago saliente"""
        return self.processor.create_payout(to_address, amount, currency)
    
    def get_balance(self, currency: str = None) -> Dict:
        """Obtiene balance"""
        return self.processor.get_balances()
