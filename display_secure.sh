#!/bin/bash
# deploy_secure.sh

echo "🔐 Despliegue seguro de NeuraForge AI"

# 1. Verificar variables de entorno críticas
required_vars=("SECRET_KEY" "TELEGRAM_TOKEN" "DATABASE_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variable crítica $var no configurada"
        exit 1
    fi
done

# 2. Generar claves de encriptación si no existen
if [ ! -f ".encryption_keys" ]; then
    openssl rand -hex 32 > .encryption_keys
    echo "✅ Claves de encriptación generadas"
fi

# 3. Instalar dependencias de seguridad
pip install cryptography argon2-cffi bcrypt

# 4. Configurar firewall del sistema
if command -v ufw &> /dev/null; then
    sudo ufw allow 8000/tcp
    sudo ufw allow 443/tcp
    sudo ufw enable
    echo "✅ Firewall del sistema configurado"
fi

# 5. Desplegar con Railway
railway up --service neuraforge-secure

# 6. Configurar Cloudflare WAF
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/firewall/rules" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
        "action": "block",
        "description": "NeuraForge Security Rules",
        "filter": {
            "expression": "(http.request.uri.path contains \"/admin\" and not ip.src in {$trusted_ips}) or cf.threat_score > 10"
        }
     }'

echo "🚀 Despliegue seguro completado"
