"""
TOKEN $NFG - Token de utilidad del ecosistema
Simulación de ERC-20/BRC-20
"""

from decimal import Decimal
from datetime import datetime
import hashlib
import json

class NeuraForgeToken:
    def __init__(self, name: str = "NeuraForge", symbol: str = "NFG"):
        self.name = name
        self.symbol = symbol
        self.total_supply = Decimal("1000000.00")  # 1 millón tokens
        self.decimals = 18
        self.holders = {}
        self.transactions = []
        
        # Distribución inicial
        self.initial_distribution = {
            "community_fund": Decimal("400000.00"),  # 40%
            "team": Decimal("200000.00"),           # 20%
            "ecosystem_growth": Decimal("200000.00"), # 20%
            "rewards_pool": Decimal("100000.00"),   # 10%
            "airdrop": Decimal("100000.00")         # 10%
        }
    
    async def initialize(self):
        """Inicializa token con distribución inicial"""
        # Asignar distribución inicial
        for holder, amount in self.initial_distribution.items():
            self.holders[holder] = {
                "address": self.generate_address(holder),
                "balance": amount,
                "locked": Decimal("0.00") if holder != "team" else amount * Decimal("0.80")  # Team vesting
            }
        
        # Crear transacción genesis
        genesis_tx = {
            "tx_hash": self.generate_tx_hash("genesis"),
            "from": "0x0000000000000000000000000000000000000000",
            "to": "distribution",
            "amount": float(self.total_supply),
            "timestamp": datetime.now().isoformat(),
            "block": 0
        }
        
        self.transactions.append(genesis_tx)
        await self.save_state()
        
        return True
    
    async def transfer(self, from_addr: str, to_addr: str, amount: Decimal) -> bool:
        """Transfiere tokens entre direcciones"""
        # Validar fondos
        if self.holders.get(from_addr, {}).get("balance", 0) < amount:
            return False
        
        # Ejecutar transferencia
        self.holders[from_addr]["balance"] -= amount
        
        if to_addr not in self.holders:
            self.holders[to_addr] = {
                "address": to_addr,
                "balance": Decimal("0.00"),
                "locked": Decimal("0.00")
            }
        
        self.holders[to_addr]["balance"] += amount
        
        # Registrar transacción
        tx = {
            "tx_hash": self.generate_tx_hash(from_addr + to_addr + str(amount)),
            "from": from_addr,
            "to": to_addr,
            "amount": float(amount),
            "timestamp": datetime.now().isoformat(),
            "block": len(self.transactions)
        }
        
        self.transactions.append(tx)
        await self.save_state()
        
        return True
    
    async def mint(self, to_addr: str, amount: Decimal) -> bool:
        """Mint nuevos tokens (solo contrato de community_fund)"""
        # En producción, esto tendría controles de permisos
        if to_addr not in self.holders:
            self.holders[to_addr] = {
                "address": to_addr,
                "balance": Decimal("0.00"),
                "locked": Decimal("0.00")
            }
        
        self.holders[to_addr]["balance"] += amount
        self.total_supply += amount
        
        # Registrar mint
        tx = {
            "tx_hash": self.generate_tx_hash("mint" + to_addr + str(amount)),
            "from": "0x0000000000000000000000000000000000000000",
            "to": to_addr,
            "amount": float(amount),
            "timestamp": datetime.now().isoformat(),
            "block": len(self.transactions),
            "type": "mint"
        }
        
        self.transactions.append(tx)
        await self.save_state()
        
        return True
    
    async def burn(self, from_addr: str, amount: Decimal) -> bool:
        """Quema tokens"""
        if self.holders.get(from_addr, {}).get("balance", 0) < amount:
            return False
        
        self.holders[from_addr]["balance"] -= amount
        self.total_supply -= amount
        
        # Registrar burn
        tx = {
            "tx_hash": self.generate_tx_hash("burn" + from_addr + str(amount)),
            "from": from_addr,
            "to": "0x0000000000000000000000000000000000000000",
            "amount": float(amount),
            "timestamp": datetime.now().isoformat(),
            "block": len(self.transactions),
            "type": "burn"
        }
        
        self.transactions.append(tx)
        await self.save_state()
        
        return True
    
    async def stake(self, holder: str, amount: Decimal) -> bool:
        """Stakea tokens para obtener voting power"""
        if self.holders.get(holder, {}).get("balance", 0) < amount:
            return False
        
        # Mover de balance a staked
        self.holders[holder]["balance"] -= amount
        
        if "staked" not in self.holders[holder]:
            self.holders[holder]["staked"] = Decimal("0.00")
        
        self.holders[holder]["staked"] += amount
        
        await self.save_state()
        return True
    
    def get_balance(self, address: str) -> Decimal:
        """Obtiene balance de dirección"""
        holder = self.holders.get(address, {})
        return holder.get("balance", Decimal("0.00"))
    
    def get_staking_power(self, address: str) -> Decimal:
        """Obtiene poder de staking (para votación)"""
        holder = self.holders.get(address, {})
        balance = holder.get("balance", Decimal("0.00"))
        staked = holder.get("staked", Decimal("0.00"))
        
        # Staked tokens cuentan doble para votación
        return balance + (staked * Decimal("2"))
    
    def generate_address(self, name: str) -> str:
        """Genera dirección simulado"""
        hash_input = name + datetime.now().isoformat()
        return "0x" + hashlib.sha256(hash_input.encode()).hexdigest()[:40]
    
    def generate_tx_hash(self, input_str: str) -> str:
        """Genera hash de transacción"""
        return "0x" + hashlib.sha256(input_str.encode()).hexdigest()[:64]
    
    async def save_state(self):
        """Guarda estado del token"""
        state = {
            "name": self.name,
            "symbol": self.symbol,
            "total_supply": float(self.total_supply),
            "holders": {
                addr: {
                    "balance": float(data["balance"]),
                    "locked": float(data.get("locked", 0)),
                    "staked": float(data.get("staked", 0))
                }
                for addr, data in self.holders.items()
            },
            "transactions": self.transactions[-100:]  # Últimas 100 transacciones
        }
        
        with open("data/token_state.json", "w") as f:
            json.dump(state, f, indent=2)
