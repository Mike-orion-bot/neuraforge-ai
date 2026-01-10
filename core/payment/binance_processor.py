#!/usr/bin/env python3
"""
BINANCE PROCESSOR - Alternativa estable a Bitso para México
"""

import os
import hmac
import hashlib
import requests
import time
from typing import Dict, Optional
from decimal import Decimal

class BinanceProcessor:
    """Procesador de pagos con Binance API"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.base_url = "https://api.binance.com"
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        
    def get_deposit_address(self, currency: str = "USDT", network: str = "BEP20") -> Dict:
        """Obtiene dirección de depósito"""
        endpoint = "/sapi/v1/capital/deposit/address"
        params = {
            "coin": currency,
            "network": network,
            "timestamp": int(time.time() * 1000)
        }
        
        response = self._signed_request("GET", endpoint, params)
        return {
            "address": response.get("address"),
            "tag": response.get("tag"),
            "currency": currency,
            "network": network,
            "platform": "Binance"
        }
    
    def create_payout(self, to_address: str, amount: Decimal, 
                     currency: str = "USDT", network: str = "BEP20") -> Dict:
        """Crea un pago/retiro"""
        endpoint = "/sapi/v1/capital/withdraw/apply"
        
        params = {
            "coin": currency,
            "address": to_address,
            "amount": str(amount),
            "network": network,
            "timestamp": int(time.time() * 1000)
        }
        
        response = self._signed_request("POST", endpoint, params)
        return {
            "id": response.get("id"),
            "status": "pending",
            "amount": amount,
            "currency": currency,
            "address": to_address
        }
    
    def get_balances(self) -> Dict:
        """Obtiene balances de cuenta"""
        endpoint = "/api/v3/account"
        params = {"timestamp": int(time.time() * 1000)}
        
        response = self._signed_request("GET", endpoint, params)
        
        balances = {}
        for balance in response.get("balances", []):
            free = Decimal(balance["free"])
            if free > 0:
                balances[balance["asset"]] = {
                    "free": free,
                    "locked": Decimal(balance["locked"]),
                    "total": free + Decimal(balance["locked"])
                }
        
        return balances
    
    def get_mxn_rate(self, crypto: str = "USDT") -> Decimal:
        """Obtiene tasa de cambio MXN a crypto"""
        # Binance no tiene par MXN directo, usar USD
        ticker = self._public_request("GET", "/api/v3/ticker/price", 
                                     {"symbol": f"{crypto}USDT"})
        
        # Convertir USDT a MXN usando tasa aproximada
        usdt_price = Decimal(ticker["price"])
        mxn_rate = usdt_price * Decimal("17.0")  # Tasa aproximada USD/MXN
        
        return mxn_rate
    
    def _signed_request(self, method: str, endpoint: str, params: Dict) -> Dict:
        """Realiza request firmado"""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        params["signature"] = signature
        
        headers = {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, params=params, headers=headers)
        
        return response.json()
    
    def _public_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Realiza request público"""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, params=params)
        return response.json()

# Cliente simplificado para usuarios
class BinanceEasyClient:
    """Cliente simplificado para usuarios finales"""
    
    @staticmethod
    def get_deposit_qr(address: str, currency: str, amount: Decimal = None) -> str:
        """Genera QR para depósito"""
        qr_data = f"{currency}:{address}"
        if amount:
            qr_data += f"?amount={amount}"
        
        # Usar API de QR codes
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_data}"
        return qr_url
    
    @staticmethod
    def validate_address(address: str, currency: str) -> bool:
        """Valida dirección de wallet"""
        # Validaciones básicas por tipo de crypto
        validators = {
            "BTC": lambda a: a.startswith("1") or a.startswith("3") or a.startswith("bc1"),
            "ETH": lambda a: a.startswith("0x") and len(a) == 42,
            "USDT": lambda a: a.startswith("0x") and len(a) == 42,  # ERC20/BEP20
            "XRP": lambda a: a.startswith("r") and len(a) == 34,
        }
        
        validator = validators.get(currency.upper())
        return validator(address) if validator else True
