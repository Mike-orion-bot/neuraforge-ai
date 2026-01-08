import qrcode
import requests
from io import BytesIO
import base64

class PaymentProcessor:
    def __init__(self):
        # Tu dirección de Bitso o Wallet para recibir
        self.my_wallet = "TU_DIRECCION_BITCOIN_AQUÍ" 

    def get_crypto_amount(self, amount_mxn):
        """Convierte Pesos a Satoshis en tiempo real"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=mxn"
            price = requests.get(url).json()['bitcoin']['mxn']
            return round(amount_mxn / price, 8)
        except:
            return 0.00001 # Valor de respaldo si falla la API

    def generate_qr_base64(self, amount_mxn, reference):
        """Crea un QR que las Apps de Crypto entienden (Protocolo bitcoin:)"""
        btc_amount = self.get_crypto_amount(amount_mxn)
        
        # Formato estándar: bitcoin:DIRECCION?amount=0.0001&label=NeuraForge
        pay_uri = f"bitcoin:{self.my_wallet}?amount={btc_amount}&label=NeuraForge_Ref_{reference}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(pay_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        
        # Convertimos a Base64 para que se pueda ver en tu HTML sin guardar archivos
        return base64.b64encode(buffered.getvalue()).decode()
