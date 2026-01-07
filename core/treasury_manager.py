# core/treasury_manager.py
import ccxt # Librería para conectar con Exchanges

class TreasuryManager:
    def __init__(self, api_key, secret):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
        })

    def convert_to_crypto(self, amount_fiat):
        """Convierte las ventas de Google Pay/Stripe a Cripto"""
        # Compra USDT para estabilidad o BTC para largo plazo
        order = self.exchange.create_market_buy_order('BTC/USDT', amount_fiat)
        return order

    def withdraw_for_life_expenses(self, amount_usdt, destination_wallet):
        """Envía fondos a tu billetera personal para tus gastos diarios"""
        # Esto es lo que te permite 'vivir bien' y recuperar tu situación
        self.exchange.withdraw('USDT', amount_usdt, destination_wallet)
