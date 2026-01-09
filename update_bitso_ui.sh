#!/bin/bash
# 💰 ACTUALIZAR ADMIN.HTML CON INTEGRACIÓN BITSO

ADMIN_HTML="templates/admin.HTML"

echo "🔧 Actualizando admin.HTML con Bitso Payments..."

# Backup
cp "$ADMIN_HTML" "$ADMIN_HTML.backup.bitso.$(date +%Y%m%d_%H%M%S)"

# Agregar nuevo modal para Bitso
sed -i '/<!-- Modal: Donation -->/i\
        <!-- Modal: Bitso Payment -->\
        <div id="bitsoPaymentModal" class="modal">\
            <div class="modal-content">\
                <div class="modal-header">\
                    <h3 class="modal-title"><i class="fas fa-coins"></i> Pago con Bitso</h3>\
                    <span class="close-modal" onclick="closeModal(\x27bitsoPaymentModal\x27)">&times;</span>\
                </div>\
                \
                <div class="form-group">\
                    <label class="form-label">Monto a pagar</label>\
                    <input type="number" class="form-input" id="bitsoAmount" placeholder="Ej: 500" min="10" max="100000">\
                </div>\
                \
                <div class="form-group">\
                    <label class="form-label">Moneda</label>\
                    <select class="form-input" id="bitsoCurrency">\
                        <option value="MXN">Pesos Mexicanos (MXN)</option>\
                        <option value="BTC">Bitcoin (BTC)</option>\
                        <option value="ETH">Ethereum (ETH)</option>\
                        <option value="USDT">USDT (TRC-20)</option>\
                    </select>\
                </div>\
                \
                <div class="form-group" id="bitsoMethodGroup">\
                    <label class="form-label">Método de pago</label>\
                    <select class="form-input" id="bitsoMethod">\
                        <option value="spei">Transferencia SPEI</option>\
                        <option value="pse">PSE (Colombia)</option>\
                        <option value="crypto">Criptomoneda</option>\
                    </select>\
                </div>\
                \
                <div class="qr-container" id="bitsoQrContainer" style="display: none;">\
                    <div class="qr-title">Escanea para pagar</div>\
                    <div class="qr-code" id="bitsoQrCode">\
                        <!-- QR generado dinámicamente -->\
                    </div>\
                </div>\
                \
                <div id="bitsoInstructions" style="margin: 20px 0; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px; display: none;">\
                    <h4><i class="fas fa-info-circle"></i> Instrucciones</h4>\
                    <div id="bitsoInstructionsContent"></div>\
                </div>\
                \
                <button class="btn btn-success" style="width: 100%;" onclick="createBitsoPayment()">\
                    <i class="fas fa-bolt"></i> Generar Enlace de Pago\
                </button>\
                \
                <div id="bitsoPaymentResult" style="margin-top: 20px; display: none;">\
                    <!-- Resultado del pago -->\
                </div>\
            </div>\
        </div>' "$ADMIN_HTML"

# Agregar funciones JavaScript
sed -i '/function showDonationModalForGrowth(amount) {/a\
        // Mostrar modal de Bitso para pagos grandes\
        function showBitsoPaymentModal(amount, currency, purpose) {\
            document.getElementById("bitsoPaymentModal").style.display = "block";\
            \
            if (amount) {\
                document.getElementById("bitsoAmount").value = amount;\
            }\
            \
            if (currency) {\
                document.getElementById("bitsoCurrency").value = currency;\
            }\
            \
            currentPaymentPurpose = purpose || "general";\
        }' "$ADMIN_HTML"

# Agregar después de la función processDonation
sed -i '/function processDonation() {/a\
        // Crear pago con Bitso\
        async function createBitsoPayment() {\
            const amount = document.getElementById("bitsoAmount").value;\
            const currency = document.getElementById("bitsoCurrency").value;\
            const method = document.getElementById("bitsoMethod").value;\
            \
            if (!amount || amount < 10) {\
                alert("Monto mínimo: $10 MXN o equivalente");\
                return;\
            }\
            \
            // Datos adicionales para crecimiento\
            const purpose = currentPaymentPurpose;\
            let botId = null;\
            let nodeName = null;\
            \
            if (purpose.startsWith("growth_")) {\
                botId = currentBotId;\
                nodeName = purpose.replace("growth_", "");\
            }\
            \
            try {\
                const response = await fetch("/api/bitso/create-payment", {\
                    method: "POST",\
                    headers: {"Content-Type": "application/json"},\
                    body: JSON.stringify({\
                        amount: parseFloat(amount),\
                        currency: currency,\
                        bot_id: botId,\
                        node_name: nodeName,\
                        description: `Pago NeuraForge AI - ${purpose}`\
                    })\
                });\
                \
                if (!response.ok) throw new Error("Error creando pago");\
                \
                const result = await response.json();\
                \
                if (result.success) {\
                    showBitsoPaymentResult(result.payment_data);\
                } else {\
                    alert(`Error: ${result.detail || "Error desconocido"}`);\
                }\
                \
            } catch (error) {\
                console.error("Error:", error);\
                alert("Error de conexión al servidor");\
            }\
        }\
        \
        // Mostrar resultado del pago Bitso\
        function showBitsoPaymentResult(paymentData) {\
            const resultDiv = document.getElementById("bitsoPaymentResult");\
            const qrContainer = document.getElementById("bitsoQrContainer");\
            const instructionsDiv = document.getElementById("bitsoInstructions");\
            \
            // Mostrar QR si existe\
            if (paymentData.qr_code_url) {\
                qrContainer.style.display = "block";\
                document.getElementById("bitsoQrCode").innerHTML = \
                    `<img src="${paymentData.qr_code_url}" alt="QR Code" style="width:100%; border-radius:5px;">`;\
            }\
            \
            // Mostrar instrucciones\
            if (paymentData.instructions) {\
                instructionsDiv.style.display = "block";\
                \
                if (typeof paymentData.instructions === "string") {\
                    document.getElementById("bitsoInstructionsContent").innerHTML = \
                        `<p>${paymentData.instructions}</p>`;\
                } else if (typeof paymentData.instructions === "object") {\
                    let html = "";\
                    for (const [key, value] of Object.entries(paymentData.instructions)) {\
                        html += `<p><strong>${key}:</strong> ${value}</p>`;\
                    }\
                    document.getElementById("bitsoInstructionsContent").innerHTML = html;\
                }\
            }\
            \
            // Mostrar enlaces\
            let resultHtml = `<div style="text-align:center;">\
                <h4 style="color:var(--success);"><i class="fas fa-check-circle"></i> Pago creado exitosamente</h4>\
                <p>ID: <code>${paymentData.payment_id}</code></p>`;\
            \
            if (paymentData.payment_url) {\
                resultHtml += `<a href="${paymentData.payment_url}" target="_blank" class="btn btn-primary" style="margin:10px;">\
                    <i class="fas fa-external-link-alt"></i> Ir a Pagar\
                </a>`;\
            }\
            \
            if (paymentData.spei_reference) {\
                resultHtml += `<div style="margin-top:15px;">\
                    <p><strong>Referencia SPEI:</strong></p>\
                    <input type="text" value="${paymentData.spei_reference}" readonly style="width:100%; padding:10px; text-align:center; font-family:monospace; background:#111; color:var(--highlight); border:1px solid var(--highlight); border-radius:5px;">\
                </div>`;\
            }\
            \
            if (paymentData.crypto_address) {\
                resultHtml += `<div style="margin-top:15px;">\
                    <p><strong>Dirección ${paymentData.currency}:</strong></p>\
                    <input type="text" value="${paymentData.crypto_address}" readonly style="width:100%; padding:10px; text-align:center; font-family:monospace; background:#111; color:var(--highlight); border:1px solid var(--highlight); border-radius:5px; word-break:break-all;">\
                </div>`;\
            }\
            \
            resultHtml += `<p style="margin-top:15px; font-size:12px; opacity:0.8;">\
                <i class="fas fa-clock"></i> Expira: ${new Date(paymentData.expires_at).toLocaleString()}\
            </p></div>`;\
            \
            resultDiv.innerHTML = resultHtml;\
            resultDiv.style.display = "block";\
            \
            // Actualizar UI si es para crecimiento\
            if (currentPaymentPurpose.startsWith("growth_") && currentBotId) {\
                setTimeout(() => loadGrowthData(currentBotId), 3000);\
            }\
        }' "$ADMIN_HTML"

# Actualizar función de donación para incluir Bitso en montos grandes
sed -i '/function processDonation() {/i\
        // Variable global para propósito de pago\
        let currentPaymentPurpose = "general";' "$ADMIN_HTML"

sed -i '/function processDonation() {/,/^        }/ {
    /alert.*Donación.*procesada/ i\
            // Para montos grandes, sugerir Bitso\
            if (amount >= 1000) {\
                if (confirm("¿Deseas usar Bitso para este pago grande?\\n\\nOfrece: SPEI, Crypto, tasas más bajas.")) {\
                    showBitsoPaymentModal(amount, "MXN", "donation");\
                    return;\
                }\
            }
}' "$ADMIN_HTML"

# Actualizar función de upgrade para usar Bitso
sed -i '/function upgradeToNode(nodeName) {/,/^        }/ {
    /const confirmUpgrade = confirm/ a\
            // Determinar costo del nodo\
            const nodeCost = getNodeCost(nodeName);\
            if (nodeCost >= 500) {\
                if (confirm(`Recomendamos usar Bitso para pagos mayores a $500 MXN.\\n\\n¿Deseas continuar con Bitso?`)) {\
                    showBitsoPaymentModal(nodeCost, "MXN", `growth_${nodeName}`);\
                    return;\
                }\
            }
}' "$ADMIN_HTML"

# Agregar función para obtener costo del nodo
sed -i '/function getNodeIcon(nodeName) {/i\
        // Obtener costo aproximado del nodo\
        function getNodeCost(nodeName) {\
            const costs = {\
                "nivel_2": 500,\
                "nivel_3": 1500\
            };\
            return costs[nodeName] || 0;\
        }' "$ADMIN_HTML"

echo "✅ Interfaz Bitso actualizada en admin.HTML"
echo "📋 Backup: $ADMIN_HTML.backup.bitso.*"
