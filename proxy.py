import requests
import random
from itertools import cycle

class MultiPlatformOrchestrator:
    def __init__(self, proxy_list: list):
        # Lista de proxies (pueden ser gratuitos o premium)
        self.proxy_pool = cycle(proxy_list)
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X)..."
        ]

    def get_headers(self):
        return {"User-Agent": random.choice(self.user_agents)}

    def request_with_rotation(self, url, method="GET", data=None):
        """Ejecuta una petición rotando IP y User-Agent para evitar rastreo."""
        proxy = next(self.proxy_pool)
        proxies = {"http": proxy, "https": proxy}
        
        try:
            response = requests.request(
                method, url, 
                proxies=proxies, 
                headers=self.get_headers(), 
                data=data, 
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"🔄 Proxy {proxy} falló, reintentando con el siguiente...")
            return self.request_with_rotation(url, method, data)
