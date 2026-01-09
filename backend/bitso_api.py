"""
🌐 ENDPOINTS API PARA BITSO - Webhooks y pagos
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Dict, Optional
from pydantic import BaseModel
import json
import logging

from core.payment.bitso_processor import bitso_processor

router = APIRouter(prefix="/api/bitso", tags=["bitso"])

# Modelos
class PaymentRequest(BaseModel):
    amount: float
    currency: str = "MXN"
    description: Optional[str] = None
    bot_id: Optional[str] = None
    node_name: Optional[str] = None

class WithdrawalRequest(BaseModel):
    amount: float
    currency: str = "MXN"
    destination: str  # CLABE o dirección crypto
    method: str = "spie"  # spie, crypto

# Endpoints
@router.post("/create-payment")
async def create_payment(request: PaymentRequest):
    """Crea enlace de pago con Bitso"""
    try:
        if request.bot_id and request.node_name:
            # Pago para crecimiento
            result = bitso_processor.create_growth_payment(
                bot_id=request.bot_id,
                node_name=request.node_name,
                amount=request.amount,
                currency=request.currency
            )
        else:
            # Pago general
            result = bitso_processor.create_payment_link(
                amount=request.amount,
                currency=request.currency,
                description=request.description or "Donación NeuraForge AI"
            )
        
        if result.get("success"):
            return {
                "success": True,
                "payment_data": result,
                "message": "Enlace de pago creado"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Error desconocido"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando pago: {str(e)}")

@router.post("/create-withdrawal")
async def create_withdrawal(request: WithdrawalRequest):
    """Crea retiro a cuenta bancaria o crypto"""
    try:
        result = bitso_processor.create_withdrawal(
            amount=request.amount,
            currency=request.currency,
            destination=request.destination,
            method=request.method
        )
        
        if result.get("success"):
            return {
                "success": True,
                "withdrawal_data": result,
                "message": "Retiro programado"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando retiro: {str(e)}")

@router.get("/account-info")
async def get_account_info():
    """Obtiene información de cuenta Bitso"""
    try:
        result = bitso_processor.get_account_info()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo info: {str(e)}")

@router.get("/payment-status/{payment_id}")
async def get_payment_status(payment_id: str):
    """Verifica estado de un pago"""
    try:
        result = bitso_processor.check_payment_status(payment_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando pago: {str(e)}")

# Webhooks
@router.post("/webhook")
async def handle_bitso_webhook(
    request: Request,
    x_bitso_signature: Optional[str] = Header(None)
):
    """Webhook para recibir notificaciones de Bitso"""
    
    try:
        # Leer payload
        payload_bytes = await request.body()
        payload_str = payload_bytes.decode('utf-8')
        payload = json.loads(payload_str)
        
        # Verificar firma
        if x_bitso_signature:
            if not bitso_processor.verify_webhook_signature(payload_str, x_bitso_signature):
                logging.warning("⚠️ Firma de webhook inválida")
                raise HTTPException(status_code=401, detail="Firma inválida")
        
        # Procesar webhook
        result = bitso_processor.process_webhook(payload)
        
        if result.get("success"):
            return {"success": True, "processed": True}
        else:
            logging.error(f"Error procesando webhook: {result.get('error')}")
            return {"success": False, "error": result.get("error")}
            
    except Exception as e:
        logging.error(f"Error en webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/crypto")
async def handle_crypto_webhook(
    request: Request,
    x_bitso_signature: Optional[str] = Header(None)
):
    """Webhook específico para pagos crypto"""
    
    try:
        payload_bytes = await request.body()
        payload_str = payload_bytes.decode('utf-8')
        payload = json.loads(payload_str)
        
        # Aquí procesarías específicamente pagos crypto
        # Por ahora usamos el mismo procesador
        result = bitso_processor.process_webhook(payload)
        
        return {"success": True, "crypto_processed": True, "result": result}
        
    except Exception as e:
        logging.error(f"Error en webhook crypto: {e}")
        return {"success": False, "error": str(e)}
