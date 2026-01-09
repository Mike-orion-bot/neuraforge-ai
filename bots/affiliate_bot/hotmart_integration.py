"""
INTEGRACIÓN HOTMART API
"""
import aiohttp
import json
import hashlib
import hmac
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HotmartManager:
    def __init__(self):
        self.base_url = "https://api.hotmart.com"
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.session = None
        
    async def connect(self):
        """Conecta a la API de Hotmart"""
        from core.config import settings
        
        self.client_id = settings.HOTMART_CLIENT_ID
        self.client_secret = settings.HOTMART_CLIENT_SECRET
        
        if not self.client_id or not self.client_secret:
            logger.error("Credenciales Hotmart no configuradas")
            return False
        
        try:
            # Obtener access token
            self.access_token = await self.get_access_token()
            
            # Crear sesión
            self.session = aiohttp.ClientSession()
            
            logger.info("✅ Conectado a Hotmart API")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando a Hotmart: {e}")
            return False
    
    async def get_access_token(self):
        """Obtiene token de acceso OAuth"""
        auth_url = f"{self.base_url}/oauth/token"
        
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            data = {'grant_type': 'client_credentials'}
            
            async with session.post(auth_url, auth=auth, data=data) as response:
                result = await response.json()
                return result.get('access_token')
    
    async def get_products(self):
        """Obtiene productos de Hotmart"""
        url = f"{self.base_url}/product/rest/v2"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                products = await response.json()
                return products.get('items', [])
            else:
                logger.error(f"Error obteniendo productos: {response.status}")
                return []
    
    async def get_sales(self, start_date: str = None, end_date: str = None):
        """Obtiene ventas de Hotmart"""
        url = f"{self.base_url}/sales/rest/v2/historical"
        
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                sales = await response.json()
                return sales.get('items', [])
            else:
                logger.error(f"Error obteniendo ventas: {response.status}")
                return []
    
    async def get_affiliates(self, product_id: str = None):
        """Obtiene afiliados"""
        url = f"{self.base_url}/affiliate/rest/v2"
        
        params = {}
        if product_id:
            params['product_id'] = product_id
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                affiliates = await response.json()
                return affiliates.get('items', [])
            else:
                logger.error(f"Error obteniendo afiliados: {response.status}")
                return []
    
    async def create_affiliate_link(self, product_id: str, affiliate_id: str):
        """Crea link de afiliado"""
        url = f"{self.base_url}/affiliate/rest/v2/link"
        
        data = {
            'product_id': product_id,
            'affiliate_id': affiliate_id,
            'source': 'neuraforge_bot'
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with self.session.post(url, headers=headers, json=data) as response:
            if response.status == 201:
                result = await response.json()
                return result
            else:
                logger.error(f"Error creando link: {response.status}")
                return None
    
    async def verify_webhook_signature(self, signature: str, payload: bytes, secret: str):
        """Verifica firma de webhook Hotmart"""
        computed_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, computed_signature)
    
    async def is_connected(self):
        """Verifica si está conectado"""
        return self.access_token is not None and self.session is not None
