# core/payment/crypto_gateway.py
import hashlib
import secrets
from typing import Dict, Optional
import aiohttp
import asyncio

class CryptoPaymentGateway:
    """Gateway de pagos con conversión automática a crypto"""
    
    def __init__(self):
        self.exchange_apis = {
            'bitso': 'https://api.bitso.com/v3/ticker',
            'binance': 'https://api.binance.com/api/v3/ticker/price',
            'coinbase': 'https://api.coinbase.com/v2/exchange-rates'
        }
        
    async def create_payment_request(self, amount_mxn: float, 
                                   email: str, 
                                   license_key: str) -> Dict:
        """Crea solicitud de pago con múltiples opciones"""
        
        # Generar ID de transacción único
        tx_id = self._generate_tx_id(license_key, email)
        
        # Opción 1: Google Pay (si está disponible)
        google_pay_link = await self._generate_google_pay_link(amount_mxn, tx_id)
        
        # Opción 2: Crypto directo
        crypto_options = await self._get_crypto_options(amount_mxn)
        
        # Opción 3: Transferencia bancaria tradicional
        bank_transfer = self._generate_bank_transfer(amount_mxn, tx_id)
        
        return {
            'transaction_id': tx_id,
            'amount_mxn': amount_mxn,
            'payment_options': {
                'google_pay': google_pay_link,
                'crypto': crypto_options,
                'bank_transfer': bank_transfer
            },
            'expires_in': 3600,  # 1 hora
            'verification_url': f"https://botscaza.com/verify/{tx_id}"
        }
    
    def _generate_tx_id(self, license_key: str, email: str) -> str:
        """Genera ID de transacción único"""
        seed = f"{license_key}:{email}:{secrets.token_hex(8)}"
        hash_obj = hashlib.sha3_256(seed.encode())
        tx_hash = hash_obj.hexdigest()[:16].upper()
        
        # Formato: TX-NF-XXXX-XXXX
        return f"TX-NF-{tx_hash[:4]}-{tx_hash[4:8]}"
    
    async def _generate_google_pay_link(self, amount: float, tx_id: str) -> Optional[Dict]:
        """Genera enlace de Google Pay"""
        try:
            # En producción, usar Google Pay API real
            return {
                'type': 'google_pay',
                'url': f"https://pay.google.com/gp/p/{tx_id}",
                'amount': amount,
                'currency': 'MXN',
                'qr_code': f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://pay.google.com/gp/p/{tx_id}"
            }
        except:
            return None
    
    async def _get_crypto_options(self, amount_mxn: float) -> Dict:
        """Obtiene opciones de pago en crypto"""
        crypto_rates = {}
        
        async with aiohttp.ClientSession() as session:
            for crypto in ['BTC', 'ETH', 'USDT', 'XRP']:
                try:
                    rate = await self._get_crypto_rate(crypto, session)
                    if rate:
                        crypto_amount = amount_mxn / rate
                        crypto_rates[crypto] = {
                            'amount': round(crypto_amount, 8),
                            'rate': rate,
                            'address': self._generate_crypto_address(crypto)
                        }
                except:
                    continue
        
        return crypto_rates
    
    async def _get_crypto_rate(self, crypto: str, session: aiohttp.ClientSession) -> Optional[float]:
        """Obtiene tasa de cambio actual"""
        try:
            if crypto == 'BTC':
                url = "https://api.bitso.com/v3/ticker/?book=btc_mxn"
                async with session.get(url) as response:
                    data = await response.json()
                    return float(data['payload']['last'])
            # Agregar más cryptos según necesidad
        except:
            # Fallback a tasas predefinidas
            fallback_rates = {
                'BTC': 1000000,
                'ETH': 60000,
                'USDT': 17,
                'XRP': 10
            }
            return fallback_rates.get(crypto, 17)
    
    def _generate_crypto_address(self, crypto: str) -> str:
        """Genera dirección de recepción única"""
        # En producción, generar dirección única por transacción
        base_addresses = {
            'BTC': 'bc1qneuraforgecrypto42jklmnopqrstuvwxyz',
            'ETH': '0xNeuraForgeCrypto42ABCDEF1234567890',
            'USDT': 'TNeuraForgeCrypto42ABCDEF1234567890',
            'XRP': 'rNeuraForgeCrypto42ABCDEF1234567890'
        }
        return base_addresses.get(crypto, '')
    
    def _generate_bank_transfer(self, amount: float, tx_id: str) -> Dict:
        """Genera datos para transferencia bancaria"""
        return {
            'type': 'bank_transfer',
            'bank': 'BBVA',
            'clabe': '012180001234567890',
            'account': '4152312345678901',
            'name': 'NeuraForge AI',
            'reference': tx_id,
            'amount': amount
        }
