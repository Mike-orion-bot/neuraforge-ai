import asyncio
import aiohttp
from datetime import datetime

class PaymentMonitor:
    def __init__(self, wallet_address):
        self.wallet = wallet_address
        self.api_url = f"https://blockchain.info/rawaddr/{wallet_address}"

    async def check_payment(self, expected_satoshis):
        """Vigila la billetera hasta encontrar el pago"""
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(self.api_url) as response:
                    data = await response.json()
                    # Revisamos la última transacción
                    last_tx = data['txs'][0] if data['txs'] else None
                    
                    if last_tx:
                        # Verificamos si el monto coincide (con un margen de error pequeño)
                        for out in last_tx['out']:
                            if out['addr'] == self.wallet and out['value'] >= expected_satoshis:
                                return True, last_tx['hash']
                
                # Esperamos 30 segundos antes de volver a revisar (para no saturar la API)
                await asyncio.sleep(30)

# Ejemplo de uso:
# monitor = PaymentMonitor("TU_DIRECCION_WALLET")
# await monitor.check_payment(2500) # 2500 Satoshis aprox $20 MXN
