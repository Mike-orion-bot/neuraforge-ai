# core/security/predictive_firewall.py
import os
import time

class PredictiveFirewall:
    def __init__(self):
        self.blacklist = set()
        self.failed_attempts = {} # {ip: count}

    def analyze_traffic(self, ip_address, request_pattern):
        """
        Analiza si el comportamiento de una IP es humano o un bot de ataque.
        """
        # Si la IP hace más de 10 peticiones por segundo, es sospechosa
        if self._is_brute_force(ip_address):
            self.block_ip(ip_address)
            return False
        return True

    def _is_brute_force(self, ip):
        self.failed_attempts[ip] = self.failed_attempts.get(ip, 0) + 1
        return self.failed_attempts[ip] > 20 # Umbral predictivo

    def block_ip(self, ip):
        print(f"🚫 Firewall: Bloqueando IP maliciosa {ip}")
        self.blacklist.add(ip)
        # Comando para el sistema operativo (si estuviéramos en Linux real)
        # os.system(f"iptables -A INPUT -s {ip} -j DROP")

