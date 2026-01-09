"""
💰 BITSO PAYMENT PROCESSOR - Integración oficial Bitso API
Para recibir pagos automáticos en MXN y criptomonedas
"""

import os
import json
import hmac
import hashlib
import base64
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Configuración
BITSO_API_URL = "https://api.bitso.com"
BITSO_API_VERSION = "v3"

class BitsoPaymentProcessor:
    """Procesador de pagos con Bitso API oficial"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or os.getenv("BITSO_API_KEY")
        self.api_secret = api_secret or os.getenv("BITSO_API_SECRET")
        self.session = requests.Session()
        self.setup_webhooks()
        
        # Parámetros de comisión
        self.fees = {
            'MXN': {'deposit': 0.0, 'withdrawal': 5.0},  # 0% depósito, $5 retiro
            'BTC': {'deposit': 0.0, 'withdrawal': 0.0005},
            'ETH': {'deposit': 0.0, 'withdrawal': 0.01},
            'USDT': {'deposit': 0.0, 'withdrawal': 1.0}
        }
        
        logging.info("✅ Bitso Payment Processor inicializado")
    
    def generate_signature(self, method: str, path: str, json_payload: str = "") -> Dict:
        """Genera firma para autenticación Bitso API"""
        nonce = str(int(time.time() * 1000))
        message = nonce + method.upper() + "/" + BITSO_API_VERSION + path + json_payload
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "Authorization": f"Bitso {self.api_key}:{nonce}:{signature}",
            "Content-Type": "application/json"
        }
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Realiza petición a Bitso API"""
        path = f"/{BITSO_API_VERSION}/{endpoint}"
        json_payload = json.dumps(data) if data else ""
        
        headers = self.generate_signature(method, path, json_payload)
        url = BITSO_API_URL + path
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                response = self.session.put(url, headers=headers, json=data)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error en petición Bitso: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== PAY-INS (DEPÓSITOS) ====================
    
    def create_payment_link(self, amount: float, currency: str = "MXN", 
                           description: str = "", customer_email: str = None) -> Dict:
        """Crea enlace de pago para que clientes te depositen"""
        
        # Para MXN - PSE o Transferencia SPEI
        if currency == "MXN":
            return self.create_mxn_payment(amount, description, customer_email)
        
        # Para criptomonedas
        elif currency in ["BTC", "ETH", "USDT"]:
            return self.create_crypto_payment(amount, currency, description, customer_email)
        
        else:
            return {"success": False, "error": f"Moneda no soportada: {currency}"}
    
    def create_mxn_payment(self, amount: float, description: str, customer_email: str = None) -> Dict:
        """Crea enlace de pago en MXN vía SPEI/PSE"""
        
        # Obtener datos de cuenta Bitso
        account_info = self.get_account_info()
        if not account_info.get('success', False):
            return account_info
        
        # Generar referencia única
        reference = f"NF{int(time.time())}{hashlib.md5(str(amount).encode()).hexdigest()[:6].upper()}"
        
        payment_data = {
            "amount": amount,
            "currency": "MXN",
            "reference": reference,
            "description": description or f"Donación NeuraForge AI #{reference}",
            "customer_email": customer_email,
            "return_url": "https://neuraforge.ai/payment/success",
            "cancel_url": "https://neuraforge.ai/payment/cancel",
            "webhook_url": os.getenv("BITSO_WEBHOOK_URL", "https://api.neuraforge.ai/webhook/bitso"),
            "metadata": {
                "product": "neuraforge_donation",
                "system": "growth_nodes",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # En producción, usarías el endpoint de Bitso para crear enlaces de pago
        # Por ahora simulamos
        return {
            "success": True,
            "payment_id": reference,
            "payment_url": f"https://bitso.com/pay/{reference}",
            "spei_reference": f"646180{reference}",
            "instructions": {
                "bank": "BBVA Bancomer",
                "account": account_info.get('account_number', 'TBD'),
                "clabe": account_info.get('clabe', 'TBD'),
                "beneficiary": "NeuraForge AI Solutions"
            },
            "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=https://bitso.com/pay/{reference}",
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
    
    def create_crypto_payment(self, amount: float, currency: str, 
                             description: str, customer_email: str = None) -> Dict:
        """Crea dirección de depósito para criptomonedas"""
        
        # Generar dirección única (en producción, usarías API de Bitso)
        address_map = {
            "BTC": "bc1qneuraforgecrypto42jklmnopqrstuvwxyz",
            "ETH": "0xNeuraForgeCrypto42ABCDEF1234567890",
            "USDT": "TNeuraForgeCrypto42ABCDEF1234567890"
        }
        
        address = address_map.get(currency)
        
        if not address:
            return {"success": False, "error": "Moneda crypto no soportada"}
        
        reference = f"CRYPTO{int(time.time())}{hashlib.md5(str(amount).encode()).hexdigest()[:8].upper()}"
        
        return {
            "success": True,
            "payment_id": reference,
            "currency": currency,
            "amount": amount,
            "crypto_address": address,
            "destination_tag": reference[-8:],  # Para USDT
            "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={currency}:{address}?amount={amount}&label=NeuraForge",
            "instructions": f"Envía {amount} {currency} a la dirección {address}",
            "estimated_time": "2-30 confirmaciones",
            "webhook_url": os.getenv("BITSO_CRYPTO_WEBHOOK_URL", "https://api.neuraforge.ai/webhook/bitso/crypto")
        }
    
    def get_account_info(self) -> Dict:
        """Obtiene información de la cuenta Bitso"""
        try:
            # En producción, usarías: response = self.make_request("GET", "account_status")
            # Por ahora simulamos
            return {
                "success": True,
                "account_number": "1234567890",
                "clabe": "012180001234567890",
                "bank": "BBVA Bancomer",
                "balances": {
                    "MXN": 25000.50,
                    "BTC": 0.05,
                    "ETH": 0.5,
                    "USDT": 1000.0
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== PAYOUTS (RETIROS) ====================
    
    def create_withdrawal(self, amount: float, currency: str, 
                         destination: str, method: str = "spie") -> Dict:
        """Crea un retiro a cuenta bancaria o dirección crypto"""
        
        withdrawal_data = {
            "amount": str(amount),
            "currency": currency,
            "method": method,
            "reference": f"PAYOUT{int(time.time())}",
            "notes": "Pago NeuraForge AI - Sistema de crecimiento"
        }
        
        if method == "spie":
            withdrawal_data["beneficiary_name"] = "Cliente NeuraForge"
            withdrawal_data["clabe"] = destination
        elif method == "crypto":
            withdrawal_data["address"] = destination
            if currency == "USDT":
                withdrawal_data["destination_tag"] = "NEURAFORGE"
        
        try:
            # En producción: response = self.make_request("POST", "withdrawals", withdrawal_data)
            # Simulamos respuesta
            return {
                "success": True,
                "withdrawal_id": f"W{int(time.time())}",
                "amount": amount,
                "currency": currency,
                "fee": self.fees.get(currency, {}).get('withdrawal', 0),
                "net_amount": amount - self.fees.get(currency, {}).get('withdrawal', 0),
                "estimated_arrival": (datetime.now() + timedelta(hours=2)).isoformat(),
                "status": "pending",
                "tracking_url": f"https://bitso.com/withdrawal/{int(time.time())}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== WEBHOOKS ====================
    
    def setup_webhooks(self):
        """Configura webhooks para recibir notificaciones de pagos"""
        self.webhook_secret = os.getenv("BITSO_WEBHOOK_SECRET", "neuraforge_secret_2024")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verifica firma de webhook de Bitso"""
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def process_webhook(self, payload: Dict) -> Dict:
        """Procesa webhook de Bitso para actualizar pagos"""
        
        event_type = payload.get("type")
        event_data = payload.get("data", {})
        
        if event_type == "payment.received":
            return self.handle_payment_received(event_data)
        elif event_type == "withdrawal.completed":
            return self.handle_withdrawal_completed(event_data)
        elif event_type == "withdrawal.failed":
            return self.handle_withdrawal_failed(event_data)
        
        return {"success": False, "error": "Evento no manejado"}
    
    def handle_payment_received(self, data: Dict) -> Dict:
        """Maneja recepción de pago"""
        payment_id = data.get("payment_id")
        amount = data.get("amount")
        currency = data.get("currency")
        customer_email = data.get("customer_email")
        
        logging.info(f"💰 Pago recibido: {amount} {currency} - ID: {payment_id}")
        
        # Actualizar base de datos
        try:
            from core.database.models import DatabaseManager
            db = DatabaseManager()
            
            # Buscar transacción por payment_id
            db.update_payment_status(payment_id, "completed", {
                "bitso_data": data,
                "completed_at": datetime.now().isoformat()
            })
            
            # Actualizar crecimiento del bot si aplica
            if data.get("metadata", {}).get("system") == "growth_nodes":
                bot_id = data.get("metadata", {}).get("bot_id")
                if bot_id:
                    from core.growth_manager import growth_manager
                    asyncio.run(growth_manager.process_donation_for_growth(
                        bot_id, amount, f"bitso_{currency}"
                    ))
            
            return {"success": True, "processed": True, "payment_id": payment_id}
            
        except Exception as e:
            logging.error(f"Error procesando pago: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_withdrawal_completed(self, data: Dict) -> Dict:
        """Maneja retiro completado"""
        withdrawal_id = data.get("withdrawal_id")
        
        logging.info(f"✅ Retiro completado: {withdrawal_id}")
        
        # Actualizar estado en base de datos
        try:
            from core.database.models import DatabaseManager
            db = DatabaseManager()
            db.update_withdrawal_status(withdrawal_id, "completed", data)
            return {"success": True}
        except:
            return {"success": False}
    
    def handle_withdrawal_failed(self, data: Dict) -> Dict:
        """Maneja retiro fallido"""
        withdrawal_id = data.get("withdrawal_id")
        reason = data.get("reason", "Unknown")
        
        logging.error(f"❌ Retiro fallido {withdrawal_id}: {reason}")
        
        try:
            from core.database.models import DatabaseManager
            db = DatabaseManager()
            db.update_withdrawal_status(withdrawal_id, "failed", data)
            return {"success": True}
        except:
            return {"success": False}
    
    # ==================== INTEGRACIÓN CON CRECIMIENTO ====================
    
    def create_growth_payment(self, bot_id: str, node_name: str, amount: float, 
                             currency: str = "MXN") -> Dict:
        """Crea pago específico para upgrade de nodo"""
        
        node_display_names = {
            "nivel_2": "⚡ Nodo Avanzado",
            "nivel_3": "👑 Nodo Maestro"
        }
        
        description = f"Upgrade a {node_display_names.get(node_name, node_name)} - Bot {bot_id}"
        
        payment_link = self.create_payment_link(
            amount=amount,
            currency=currency,
            description=description,
            customer_email=f"bot_{bot_id}@neuraforge.ai"
        )
        
        if payment_link.get("success"):
            # Registrar en base de datos
            try:
                from core.database.models import DatabaseManager
                db = DatabaseManager()
                
                payment_id = payment_link.get("payment_id")
                db.record_payment({
                    "payment_id": payment_id,
                    "bot_id": bot_id,
                    "amount": amount,
                    "currency": currency,
                    "purpose": f"growth_upgrade_{node_name}",
                    "status": "pending",
                    "payment_data": payment_link,
                    "metadata": {
                        "bot_id": bot_id,
                        "node": node_name,
                        "system": "growth_nodes"
                    }
                })
                
                payment_link["db_recorded"] = True
                
            except Exception as e:
                logging.error(f"Error registrando pago: {e}")
                payment_link["db_recorded"] = False
        
        return payment_link
    
    def check_payment_status(self, payment_id: str) -> Dict:
        """Verifica estado de un pago"""
        try:
            # En producción: response = self.make_request("GET", f"payments/{payment_id}")
            # Simulamos
            return {
                "success": True,
                "payment_id": payment_id,
                "status": "completed",  # o pending, failed, etc.
                "amount": 500.0,
                "currency": "MXN",
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# Instancia global
bitso_processor = BitsoPaymentProcessor()
