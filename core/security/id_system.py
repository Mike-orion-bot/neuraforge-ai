# core/security/id_system.py
import hashlib
import hmac
import secrets
import string
from datetime import datetime
from typing import Dict, Optional
import json

class SecureIDSystem:
    """Sistema de generación y validación de IDs ofuscados"""
    
    def __init__(self, master_key: str = None):
        self.master_key = master_key or secrets.token_hex(32)
        self.rotation_interval = 86400  # Rotar cada 24 horas
        self.last_rotation = datetime.now().timestamp()
        
    def generate_license_key(self, bot_type: str, owner_id: str) -> Dict:
        """Genera licencia ofuscada con múltiples capas"""
        
        # Capa 1: Datos base
        timestamp = int(datetime.now().timestamp())
        random_salt = secrets.token_hex(8)
        
        # Capa 2: Hash de validación
        base_data = f"{bot_type}:{owner_id}:{timestamp}:{random_salt}"
        validation_hash = self._generate_hmac(base_data)
        
        # Capa 3: ID legible ofuscado
        license_id = self._obfuscate_id(base_data)
        
        # Capa 4: Firma digital
        signature = self._generate_signature(license_id)
        
        # Capa 5: Checksum
        checksum = self._generate_checksum(f"{license_id}:{signature}")
        
        return {
            'license_id': license_id,
            'validation_hash': validation_hash,
            'signature': signature,
            'checksum': checksum,
            'timestamp': timestamp,
            'format': "NF-V2",  # Versión del formato
            'encoded': self._encode_license(license_id, signature, checksum)
        }
    
    def _obfuscate_id(self, data: str) -> str:
        """Ofusca ID usando múltiples transformaciones"""
        # Paso 1: Hash SHA3
        hash1 = hashlib.sha3_256(data.encode()).hexdigest()
        
        # Paso 2: Mezclar con sal
        mixed = ""
        for i in range(0, len(hash1), 2):
            mixed += hash1[i] + secrets.choice(string.ascii_uppercase)
        
        # Paso 3: Formato específico
        parts = [
            "NF",
            mixed[:4].upper(),
            mixed[4:8].upper(),
            mixed[8:12].upper(),
            mixed[12:16].upper()
        ]
        
        return "-".join(parts)
    
    def _generate_hmac(self, data: str) -> str:
        """Genera HMAC para validación"""
        return hmac.new(
            self.master_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()[:12]
    
    def _generate_signature(self, license_id: str) -> str:
        """Firma digital del ID"""
        timestamp = int(datetime.now().timestamp())
        data = f"{license_id}:{timestamp}:{self.master_key[:16]}"
        return hashlib.blake2s(data.encode()).hexdigest()[:8]
    
    def _generate_checksum(self, data: str) -> str:
        """Genera checksum para verificar integridad"""
        # Algoritmo de Luhn modificado para IDs
        def luhn_checksum(s):
            digits = [int(ch) for ch in s if ch.isdigit()]
            doubled = [(2 * d if i % 2 == 0 else d) for i, d in enumerate(digits)]
            total = sum(d // 10 + d % 10 for d in doubled)
            return (10 - total % 10) % 10
        
        numeric_part = ''.join(filter(str.isdigit, data))
        return str(luhn_checksum(numeric_part))
    
    def _encode_license(self, license_id: str, signature: str, checksum: str) -> str:
        """Codifica la licencia para almacenamiento seguro"""
        data = {
            'l': license_id,
            's': signature,
            'c': checksum,
            'v': '2'
        }
        
        # Codificación Base64 URL-safe
        import base64
        json_str = json.dumps(data)
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        
        return encoded
    
    def validate_license(self, encoded_license: str) -> Dict:
        """Valida una licencia codificada"""
        try:
            import base64
            import json
            
            # Decodificar
            decoded = base64.urlsafe_b64decode(encoded_license.encode()).decode()
            data = json.loads(decoded)
            
            # Verificar formato
            if data.get('v') != '2':
                return {'valid': False, 'error': 'Versión inválida'}
            
            # Verificar checksum
            expected_checksum = self._generate_checksum(f"{data['l']}:{data['s']}")
            if data['c'] != expected_checksum:
                return {'valid': False, 'error': 'Checksum inválido'}
            
            # Verificar firma (simplificado)
            expected_signature = self._generate_signature(data['l'])
            if data['s'] != expected_signature:
                return {'valid': False, 'error': 'Firma inválida'}
            
            return {
                'valid': True,
                'license_id': data['l'],
                'signature': data['s'],
                'format': 'NF-V2'
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def rotate_master_key(self):
        """Rota la clave maestra periódicamente"""
        current_time = datetime.now().timestamp()
        if current_time - self.last_rotation > self.rotation_interval:
            self.master_key = secrets.token_hex(32)
            self.last_rotation = current_time
            print("🔑 Clave maestra rotada")
