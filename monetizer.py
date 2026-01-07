import requests

def get_monetized_link(direct_url):
    # Ejemplo con una API de acortador (Ajusta con tu API Key real)
    API_KEY = "tu_api_key_de_acortador"
    BASE_URL = "https://api.acortador.com/v1/shorten"
    
    try:
        # Llamada simulada al acortador
        # response = requests.get(f"{BASE_URL}?key={API_KEY}&url={direct_url}")
        # return response.json()['short_url']
        return f"https://paga-por-click.com/neuraforge-apk-user-123" # Simulación
    except Exception:
        return direct_url # Si falla el acortador, entrega el link directo para no perder al cliente
