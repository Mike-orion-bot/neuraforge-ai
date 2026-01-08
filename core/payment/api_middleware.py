# core/security/api_middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
from typing import Dict

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de seguridad para todas las APIs"""
    
    def __init__(self, app, firewall: PredictiveFirewall):
        super().__init__(app)
        self.firewall = firewall
        self.rate_limit = {}  # {ip: {count: int, reset_time: float}}
    
    async def dispatch(self, request: Request, call_next):
        # Obtener IP del cliente
        ip = request.client.host if request.client else "127.0.0.1"
        
        # Verificar firewall
        if not self.firewall.analyze_traffic(
            ip_address=ip,
            request_pattern=str(request.url),
            user_agent=request.headers.get("user-agent", "")
        ):
            raise HTTPException(status_code=403, detail="Acceso bloqueado por firewall")
        
        # Verificar rate limiting
        if not self._check_rate_limit(ip):
            raise HTTPException(status_code=429, detail="Demasiadas solicitudes")
        
        # Añadir headers de seguridad
        response = await call_next(request)
        
        # Headers de seguridad HTTP
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Registrar la solicitud
        self._log_request(request, response, ip)
        
        return response
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Implementa rate limiting por IP"""
        current_time = time.time()
        
        if ip not in self.rate_limit:
            self.rate_limit[ip] = {
                'count': 1,
                'reset_time': current_time + 60  # Reset cada minuto
            }
            return True
        
        # Verificar si necesita reset
        if current_time > self.rate_limit[ip]['reset_time']:
            self.rate_limit[ip] = {
                'count': 1,
                'reset_time': current_time + 60
            }
            return True
        
        # Incrementar contador
        self.rate_limit[ip]['count'] += 1
        
        # Permitir máximo 100 solicitudes por minuto
        return self.rate_limit[ip]['count'] <= 100
    
    def _log_request(self, request: Request, response, ip: str):
        """Registra solicitud para auditoría"""
        log_entry = {
            'timestamp': time.time(),
            'ip': ip,
            'method': request.method,
            'url': str(request.url),
            'status': response.status_code,
            'user_agent': request.headers.get("user-agent", ""),
            'referer': request.headers.get("referer", "")
        }
        
        # Guardar en archivo de log (en producción usaría un servicio de logging)
        with open("security_audit.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
