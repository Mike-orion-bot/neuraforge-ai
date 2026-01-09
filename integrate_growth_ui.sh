#!/bin/bash
# 📋 Script para integrar UI de crecimiento en admin.HTML

ADMIN_HTML_PATH="templates/admin.HTML"

echo "🔧 Integrando nodos de crecimiento en $ADMIN_HTML_PATH..."

# Backup del archivo original
cp "$ADMIN_HTML_PATH" "$ADMIN_HTML_PATH.backup.$(date +%Y%m%d_%H%M%S)"

# Buscar la sección de módulos y agregar después el sistema de crecimiento
# Agregar CSS para nodos primero
sed -i '/<style>/a\
        /* ================= NODOS DE CRECIMIENTO ================= */\
        .growth-system {\
            margin-top: 30px;\
            padding: 20px;\
            background: rgba(0, 0, 0, 0.3);\
            border-radius: 15px;\
            border: 1px solid var(--card-border);\
        }\
        \
        .growth-header {\
            display: flex;\
            justify-content: space-between;\
            align-items: center;\
            margin-bottom: 20px;\
            padding-bottom: 15px;\
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);\
        }\
        \
        .growth-title {\
            font-size: 20px;\
            font-weight: 700;\
            color: var(--highlight);\
            display: flex;\
            align-items: center;\
            gap: 10px;\
        }\
        \
        .node-progress-container {\
            display: flex;\
            justify-content: space-between;\
            align-items: center;\
            margin: 25px 0;\
            position: relative;\
        }\
        \
        .node {\
            background: rgba(26, 26, 46, 0.8);\
            border-radius: 12px;\
            padding: 20px;\
            text-align: center;\
            width: 30%;\
            position: relative;\
            z-index: 2;\
            transition: all 0.3s ease;\
            border: 2px solid transparent;\
        }\
        \
        .node.active {\
            border-color: var(--success);\
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);\
        }\
        \
        .node.locked {\
            border-color: var(--warning);\
            opacity: 0.7;\
            cursor: pointer;\
        }\
        \
        .node.unlockable {\
            border-color: var(--highlight);\
            opacity: 0.9;\
            cursor: pointer;\
            animation: pulse 2s infinite;\
        }\
        \
        .node.locked:hover, .node.unlockable:hover {\
            opacity: 1;\
            transform: translateY(-5px);\
        }\
        \
        .node-icon {\
            font-size: 32px;\
            margin-bottom: 10px;\
        }\
        \
        .node-name {\
            font-weight: 600;\
            margin-bottom: 5px;\
            font-size: 16px;\
        }\
        \
        .node-description {\
            font-size: 12px;\
            opacity: 0.8;\
            margin-bottom: 10px;\
            min-height: 40px;\
        }\
        \
        .node-requirements {\
            font-size: 11px;\
            color: var(--warning);\
            margin: 8px 0;\
            padding: 5px 10px;\
            background: rgba(255, 170, 0, 0.1);\
            border-radius: 8px;\
        }\
        \
        .node-connector {\
            height: 3px;\
            background: var(--highlight);\
            flex-grow: 1;\
            position: relative;\
            top: -20px;\
            z-index: 1;\
        }\
        \
        .node-connector.locked {\
            background: var(--warning);\
            opacity: 0.5;\
        }\
        \
        .btn-upgrade {\
            background: linear-gradient(45deg, var(--warning), #ffaa00);\
            color: black;\
            border: none;\
            padding: 8px 15px;\
            border-radius: 8px;\
            margin-top: 10px;\
            cursor: pointer;\
            font-weight: bold;\
            transition: all 0.3s ease;\
            width: 100%;\
        }\
        \
        .btn-upgrade:hover {\
            transform: scale(1.05);\
            box-shadow: 0 5px 15px rgba(255, 170, 0, 0.4);\
        }\
        \
        .btn-upgrade.disabled {\
            background: #666;\
            cursor: not-allowed;\
            opacity: 0.5;\
        }\
        \
        .growth-stats {\
            display: grid;\
            grid-template-columns: repeat(3, 1fr);\
            gap: 15px;\
            margin-top: 20px;\
        }\
        \
        .growth-stat-card {\
            background: rgba(0, 0, 0, 0.4);\
            border-radius: 10px;\
            padding: 15px;\
            text-align: center;\
        }\
        \
        .growth-stat-value {\
            font-size: 24px;\
            font-weight: bold;\
            color: var(--highlight);\
            margin-bottom: 5px;\
        }\
        \
        .growth-stat-label {\
            font-size: 12px;\
            opacity: 0.8;\
        }\
        \
        .unlocked-modules-list {\
            display: flex;\
            flex-wrap: wrap;\
            gap: 10px;\
            margin-top: 15px;\
        }\
        \
        .module-tag {\
            background: rgba(0, 255, 136, 0.2);\
            color: var(--success);\
            padding: 5px 10px;\
            border-radius: 20px;\
            font-size: 12px;\
            border: 1px solid var(--success);\
        }\
        \
        .module-tag.locked {\
            background: rgba(255, 85, 85, 0.2);\
            color: var(--danger);\
            border-color: var(--danger);\
        }\
        \
        @keyframes pulse {\
            0% { box-shadow: 0 0 0 0 rgba(0, 255, 255, 0.4); }\
            70% { box-shadow: 0 0 0 10px rgba(0, 255, 255, 0); }\
            100% { box-shadow: 0 0 0 0 rgba(0, 255, 255, 0); }\
        }\
        \
        .node-progress-bar {\
            height: 6px;\
            background: rgba(255, 255, 255, 0.1);\
            border-radius: 3px;\
            margin: 10px 0;\
            overflow: hidden;\
        }\
        \
        .node-progress-fill {\
            height: 100%;\
            background: linear-gradient(90deg, var(--highlight), var(--success));\
            border-radius: 3px;\
            transition: width 0.5s ease;\
        }' "$ADMIN_HTML_PATH"

# Buscar donde agregar la sección de crecimiento (después de la sección de módulos)
# Agregar HTML para el sistema de crecimiento
sed -i '/<!-- Activity Stream -->/i\
        <!-- Growth Nodes System -->\
        <div class="dashboard-section modules-section" id="growth-section">\
            <div class="section-header">\
                <h3 class="section-title">\
                    <i class="fas fa-sitemap"></i>\
                    Sistema de Crecimiento\
                </h3>\
                <div class="section-stats">\
                    <span class="metric-value" id="growth-score">0</span>\
                    <span class="metric-title">Puntos Crecimiento</span>\
                </div>\
            </div>\
            \
            <div class="growth-system">\
                <div class="node-progress-container" id="node-progress-container">\
                    <!-- Los nodos se cargan dinámicamente via JavaScript -->\
                    <div class="node" id="node-1">\
                        <div class="node-icon">🌱</div>\
                        <div class="node-name">Nodo Básico</div>\
                        <div class="node-description">Funcionalidades esenciales</div>\
                        <div class="node-status">\
                            <span class="module-status status-active">ACTUAL</span>\
                        </div>\
                    </div>\
                    \
                    <div class="node-connector"></div>\
                    \
                    <div class="node locked" id="node-2">\
                        <div class="node-icon">⚡</div>\
                        <div class="node-name">Nodo Avanzado</div>\
                        <div class="node-description">Más herramientas y límites</div>\
                        <div class="node-requirements">Requiere: $500 MXN o 5 ventas</div>\
                        <button class="btn-upgrade" onclick="upgradeNode(2)">Mejorar</button>\
                    </div>\
                    \
                    <div class="node-connector locked"></div>\
                    \
                    <div class="node locked" id="node-3">\
                        <div class="node-icon">👑</div>\
                        <div class="node-name">Nodo Maestro</div>\
                        <div class="node-description">Todas las funciones desbloqueadas</div>\
                        <div class="node-requirements">Requiere: $1500 MXN o 20 ventas</div>\
                        <button class="btn-upgrade" onclick="upgradeNode(3)">Mejorar</button>\
                    </div>\
                </div>\
                \
                <div class="growth-stats">\
                    <div class="growth-stat-card">\
                        <div class="growth-stat-value" id="total-sales">0</div>\
                        <div class="growth-stat-label">Ventas Totales</div>\
                    </div>\
                    <div class="growth-stat-card">\
                        <div class="growth-stat-value" id="total-donations">$0</div>\
                        <div class="growth-stat-label">Donaciones Acumuladas</div>\
                    </div>\
                    <div class="growth-stat-card">\
                        <div class="growth-stat-value" id="daily-quota">100</div>\
                        <div class="growth-stat-label">Límite Diario</div>\
                    </div>\
                </div>\
                \
                <div class="unlocked-modules">\
                    <h4 style="margin: 15px 0 10px 0; font-size: 16px;">\
                        <i class="fas fa-unlock"></i> Módulos Desbloqueados\
                    </h4>\
                    <div class="unlocked-modules-list" id="unlocked-modules-list">\
                        <!-- Módulos se cargan dinámicamente -->\
                        <span class="module-tag">Declaración Anual</span>\
                        <span class="module-tag">Consulta RFC</span>\
                    </div>\
                </div>\
            </div>\
        </div>' "$ADMIN_HTML_PATH"

# Agregar funciones JavaScript al final del archivo, antes de </script>
sed -i '/window.onload = function() {/a\
        // ============= SISTEMA DE CRECIMIENTO =============\
        let currentBotId = null;\
        let currentBotType = null;\
        let growthData = null;\
        \
        // Cargar datos de crecimiento\
        async function loadGrowthData(botId) {\
            if (!botId) return;\
            \
            currentBotId = botId;\
            \
            try {\
                const response = await fetch(`/api/growth/status/${botId}`);\
                if (!response.ok) throw new Error("Error cargando datos");\
                \
                growthData = await response.json();\
                updateGrowthUI(growthData);\
                \
                // Actualizar cada 30 segundos\
                setTimeout(() => loadGrowthData(botId), 30000);\
                \
            } catch (error) {\
                console.error("Error cargando crecimiento:", error);\
            }\
        }\
        \
        // Actualizar UI con datos de crecimiento\
        function updateGrowthUI(data) {\
            if (!data) return;\
            \
            // Actualizar puntuación\
            document.getElementById("growth-score").textContent = \
                data.current_node?.growth_score || 0;\
            \
            // Actualizar estadísticas\
            document.getElementById("total-sales").textContent = \
                data.current_node?.total_sales || 0;\
            \
            document.getElementById("total-donations").textContent = \
                `$${data.current_node?.total_donations || 0}`;\
            \
            document.getElementById("daily-quota").textContent = \
                data.current_node?.daily_quota || 100;\
            \
            // Actualizar nodos\
            updateNodesUI(data);\
            \
            // Actualizar módulos desbloqueados\
            updateUnlockedModules(data);\
        }\
        \
        // Actualizar visualización de nodos\
        function updateNodesUI(data) {\
            const nodes = data.available_nodes || [];\
            const currentNode = data.current_node?.current_node || "nivel_1";\
            \
            // Determinar índice del nodo actual\
            let currentIndex = 0;\
            nodes.forEach((node, index) => {\
                if (node.node_name === currentNode) {\
                    currentIndex = index;\
                }\
            });\
            \
            // Actualizar cada nodo en el DOM\
            nodes.forEach((node, index) => {\
                const nodeElement = document.getElementById(`node-${index + 1}`);\
                if (!nodeElement) return;\
                \
                // Reset clases\
                nodeElement.className = "node";\
                \
                // Icono y nombre\
                const icon = nodeElement.querySelector(".node-icon");\
                const name = nodeElement.querySelector(".node-name");\
                const desc = nodeElement.querySelector(".node-description");\
                const req = nodeElement.querySelector(".node-requirements");\
                const btn = nodeElement.querySelector(".btn-upgrade");\
                \
                if (icon) icon.textContent = getNodeIcon(node.node_name);\
                if (name) name.textContent = getNodeDisplayName(node.node_name);\
                \
                // Estado del nodo\
                if (node.is_current) {\
                    nodeElement.classList.add("active");\
                    if (btn) btn.style.display = "none";\
                } else if (data.can_upgrade && index === currentIndex + 1) {\
                    nodeElement.classList.add("unlockable");\
                    if (btn) {\
                        btn.style.display = "block";\
                        btn.className = "btn-upgrade";\
                        btn.onclick = () => upgradeToNode(node.node_name);\
                        btn.textContent = `Mejorar a ${getNodeDisplayName(node.node_name)}`;\
                    }\
                    \
                    // Mostrar requisitos\
                    if (req) {\
                        req.style.display = "block";\
                        req.textContent = formatRequirements(node.requirement_value);\
                    }\
                } else {\
                    nodeElement.classList.add("locked");\
                    if (btn) {\
                        btn.style.display = "block";\
                        btn.className = "btn-upgrade disabled";\
                        btn.disabled = true;\
                        btn.textContent = "Bloqueado";\
                    }\
                    \
                    // Mostrar requisitos\
                    if (req) {\
                        req.style.display = "block";\
                        req.textContent = formatRequirements(node.requirement_value);\
                    }\
                }\
                \
                // Actualizar conectores\
                updateConnectors(index, nodes.length, node.is_current || index <= currentIndex);\
            });\
        }\
        \
        // Actualizar módulos desbloqueados\
        function updateUnlockedModules(data) {\
            const modulesList = document.getElementById("unlocked-modules-list");\
            if (!modulesList) return;\
            \
            modulesList.innerHTML = "";\
            \
            const unlocked = data.current_node?.unlocked_modules || "[]";\
            try {\
                const modules = JSON.parse(unlocked);\
                \
                modules.forEach(module => {\
                    const tag = document.createElement("span");\
                    tag.className = "module-tag";\
                    tag.textContent = getModuleDisplayName(module);\
                    modulesList.appendChild(tag);\
                });\
                \
            } catch (e) {\
                console.error("Error parseando módulos:", e);\
            }\
        }\
        \
        // Solicitar upgrade de nodo\
        async function upgradeToNode(nodeName) {\
            if (!currentBotId || !nodeName) return;\
            \
            // Mostrar modal de confirmación\
            const confirmUpgrade = confirm(`¿Estás seguro de actualizar al nodo ${getNodeDisplayName(nodeName)}?\\n\\nEsto puede requerir una donación.`);\
            if (!confirmUpgrade) return;\
            \
            try {\
                const response = await fetch(`/api/growth/upgrade/${currentBotId}`, {\
                    method: "POST",\
                    headers: {\
                        "Content-Type": "application/json"\
                    },\
                    body: JSON.stringify({\
                        target_node: nodeName,\
                        confirm: true\
                    })\
                });\
                \
                if (!response.ok) {\
                    const error = await response.json();\
                    if (error.missing_requirements) {\
                        showRequirementModal(error);\
                    } else {\
                        alert(`Error: ${error.detail || "Error desconocido"}`);\
                    }\
                    return;\
                }\
                \
                const result = await response.json();\
                \
                if (result.success) {\
                    alert(`✅ ${result.message}`);\
                    // Recargar datos\
                    await loadGrowthData(currentBotId);\
                } else {\
                    alert(`Error: ${result.error}`);\
                }\
                \
            } catch (error) {\
                console.error("Error en upgrade:", error);\
                alert("Error de conexión al servidor");\
            }\
        }\
        \
        // Mostrar modal con requisitos faltantes\
        function showRequirementModal(errorData) {\
            const modal = document.createElement("div");\
            modal.className = "modal";\
            modal.innerHTML = `\
                <div class="modal-content">\
                    <div class="modal-header">\
                        <h3 class="modal-title"><i class="fas fa-exclamation-triangle"></i> Requisitos Faltantes</h3>\
                        <span class="close-modal" onclick="this.parentElement.parentElement.remove()">&times;</span>\
                    </div>\
                    <div style="padding: 20px;">\
                        <p>Necesitas cumplir los siguientes requisitos:</p>\
                        <ul style="margin: 15px 0; padding-left: 20px;">\
                            ${(errorData.missing_requirements || []).map(req => `<li>${req}</li>`).join("")}\
                        </ul>\
                        <div style="margin-top: 20px;">\
                            <button class="btn btn-primary" onclick="showDonationModalForGrowth(${errorData.requirements?.donation || 0})">\
                                <i class="fas fa-coffee"></i> Realizar Donación\
                            </button>\
                            <button class="btn" style="margin-left: 10px;" onclick="this.parentElement.parentElement.parentElement.remove()">\
                                Cancelar\
                            </button>\
                        </div>\
                    </div>\
                </div>\
            `;\
            \
            document.body.appendChild(modal);\
            modal.style.display = "block";\
        }\
        \
        // Mostrar modal de donación para crecimiento\
        function showDonationModalForGrowth(amount) {\
            // Cerrar modales anteriores\
            document.querySelectorAll(".modal").forEach(m => m.remove());\
            \
            // Usar el modal de donación existente\
            showDonationModal();\
            \
            // Establecer monto si se proporciona\
            if (amount) {\
                setTimeout(() => {\
                    const customAmount = document.getElementById("customAmount");\
                    if (customAmount) {\
                        customAmount.value = amount;\
                        currentDonationAmount = amount;\
                    }\
                    \
                    // Seleccionar opción de donación correspondiente\
                    document.querySelectorAll(".donation-option").forEach(option => {\
                        const optionAmount = parseInt(option.querySelector(".donation-amount").textContent.replace("$", "").replace(" MXN", ""));\
                        if (optionAmount === amount) {\
                            option.click();\
                        }\
                    });\
                }, 100);\
            }\
        }\
        \
        // Funciones auxiliares\
        function getNodeIcon(nodeName) {\
            const icons = {\
                "nivel_1": "🌱",\
                "nivel_2": "⚡",\
                "nivel_3": "👑"\
            };\
            return icons[nodeName] || "📊";\
        }\
        \
        function getNodeDisplayName(nodeName) {\
            const names = {\
                "nivel_1": "Nodo Básico",\
                "nivel_2": "Nodo Avanzado",\
                "nivel_3": "Nodo Maestro"\
            };\
            return names[nodeName] || nodeName;\
        }\
        \
        function getModuleDisplayName(moduleId) {\
            const names = {\
                "declaracion_anual": "Declaración Anual",\
                "consulta_rfc": "Consulta RFC",\
                "facturacion_cfdi": "Facturación CFDI",\
                "calculo_isr": "Cálculo ISR",\
                "contabilidad_basica": "Contabilidad Básica",\
                "auditoria_ia": "Auditoría IA",\
                "pedidos_basicos": "Pedidos Básicos",\
                "menu_digital": "Menú Digital"\
            };\
            return names[moduleId] || moduleId;\
        }\
        \
        function formatRequirements(reqJson) {\
            try {\
                const req = JSON.parse(reqJson);\
                const parts = [];\
                \
                if (req.donation) parts.push(`$${req.donation} MXN`);\
                if (req.sales) parts.push(`${req.sales} ventas`);\
                if (req.time_days) parts.push(`${req.time_days} días activo`);\
                \
                return "Requiere: " + parts.join(" o ");\
            } catch {\
                return "Requiere: donación";\
            }\
        }\
        \
        function updateConnectors(index, total, isUnlocked) {\
            // Esta función actualizaría los conectores entre nodos\
            // Implementación simplificada para demo\
        }\
        \
        // Integrar con el sistema existente de selección de bot\
        // Modificar la función que muestra datos del bot para cargar crecimiento\
        const originalShowBotData = window.showBotData || function() {};\
        window.showBotData = function(botId, botType) {\
            originalShowBotData(botId, botType);\
            loadGrowthData(botId);\
        };\
        \
        // Cargar crecimiento para el bot actual al iniciar\
        document.addEventListener("DOMContentLoaded", function() {\
            // Buscar bot activo en la página\
            const activeBotRow = document.querySelector(".licenses-table tr:hover, .licenses-table tr.active");\
            if (activeBotRow) {\
                const botId = activeBotRow.querySelector(".license-key")?.textContent;\
                if (botId) {\
                    setTimeout(() => loadGrowthData(botId.trim()), 1000);\
                }\
            }\
        });' "$ADMIN_HTML_PATH"

# Agregar botón de crecimiento a la navegación
sed -i '/<li class="nav-tab" onclick="switchTab(\x27security\x27)">Seguridad<\/li>/a\
                <li class="nav-tab" onclick="switchTab(\x27growth\x27)">Crecimiento</li>' "$ADMIN_HTML_PATH"

# Agregar contenido para la pestaña de crecimiento
sed -i '/<div id="dashboard-content" class="tab-content active">/a\
        <!-- Growth Tab Content -->\
        <div id="growth-content" class="tab-content">\
            <div class="dashboard-grid">\
                <div class="dashboard-section modules-section">\
                    <div class="section-header">\
                        <h3 class="section-title">\
                            <i class="fas fa-chart-line"></i>\
                            Dashboard de Crecimiento Global\
                        </h3>\
                        <div class="section-stats">\
                            <span class="metric-value" id="total-bots-growth">0</span>\
                            <span class="metric-title">Bots Activos</span>\
                        </div>\
                    </div>\
                    \
                    <div id="global-growth-stats">\
                        <!-- Cargado dinámicamente -->\
                        <p style="text-align: center; padding: 40px;">Cargando estadísticas de crecimiento...</p>\
                    </div>\
                </div>\
                \
                <div class="dashboard-section crypto-section">\
                    <div class="section-header">\
                        <h3 class="section-title">\
                            <i class="fas fa-trophy"></i>\
                            Ranking de Crecimiento\
                        </h3>\
                        <select class="form-input" style="width: auto;" id="growth-ranking-filter" onchange="loadGrowthRanking()">\
                            <option value="all">Todos los Bots</option>\
                            <option value="sat">SAT Bots</option>\
                            <option value="pizza">Pizza Bots</option>\
                            <option value="crypto">Crypto Bots</option>\
                        </select>\
                    </div>\
                    \
                    <div id="growth-ranking-table">\
                        <!-- Cargado dinámicamente -->\
                    </div>\
                </div>\
            </div>\
        </div>' "$ADMIN_HTML_PATH"

# Agregar función de switchTab para crecimiento
sed -i '/function switchTab(tabName) {/a\
            // Manejar pestaña de crecimiento\
            if (tabName === "growth") {\
                loadGlobalGrowthStats();\
                loadGrowthRanking();\
            }' "$ADMIN_HTML_PATH"

# Agregar funciones para la pestaña de crecimiento
sed -i '/\/\/ ============= SISTEMA DE CRECIMIENTO =============/i\
        // ============= PESTAÑA DE CRECIMIENTO GLOBAL =============\
        async function loadGlobalGrowthStats() {\
            try {\
                const response = await fetch("/api/growth/summary");\
                if (!response.ok) throw new Error("Error cargando estadísticas");\
                \
                const data = await response.json();\
                \
                document.getElementById("total-bots-growth").textContent = data.total_bots || 0;\
                \
                const statsHtml = `\
                    <div class="metrics-grid">\
                        <div class="metric-card">\
                            <div class="metric-title">Puntuación Promedio</div>\
                            <div class="metric-value">${data.stats?.average_growth_score?.toFixed(1) || 0}</div>\
                        </div>\
                        <div class="metric-card">\
                            <div class="metric-title">Ventas Totales</div>\
                            <div class="metric-value">${data.stats?.total_sales?.toLocaleString() || 0}</div>\
                        </div>\
                        <div class="metric-card">\
                            <div class="metric-title">Donaciones Totales</div>\
                            <div class="metric-value">$${data.stats?.total_donations?.toFixed(2) || 0}</div>\
                        </div>\
                        <div class="metric-card">\
                            <div class="metric-title">Listos para Upgrade</div>\
                            <div class="metric-value">${data.stats?.ready_for_upgrade || 0}</div>\
                            <div class="metric-change">${data.stats?.upgrade_rate || 0}% del total</div>\
                        </div>\
                    </div>\
                    \
                    <h4 style="margin: 25px 0 15px 0;">Distribución por Nodo</h4>\
                    <div class="node-distribution">\
                        ${Object.entries(data.stats?.node_distribution || {}).map(([node, count]) => `\
                            <div style="margin-bottom: 10px;">\
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">\
                                    <span>${getNodeDisplayName(node)}</span>\
                                    <span>${count} bots (${((count / data.total_bots) * 100).toFixed(1)}%)</span>\
                                </div>\
                                <div class="node-progress-bar">\
                                    <div class="node-progress-fill" style="width: ${((count / data.total_bots) * 100)}%"></div>\
                                </div>\
                            </div>\
                        `).join("")}\
                    </div>\
                `;\
                \
                document.getElementById("global-growth-stats").innerHTML = statsHtml;\
                \
            } catch (error) {\
                console.error("Error cargando estadísticas globales:", error);\
                document.getElementById("global-growth-stats").innerHTML = \
                    `<p style="color: var(--danger); text-align: center;">Error cargando estadísticas</p>`;\
            }\
        }\
        \
        async function loadGrowthRanking() {\
            const filter = document.getElementById("growth-ranking-filter")?.value || "all";\
            \
            try {\
                const url = filter === "all" ? "/api/growth/summary" : `/api/growth/summary?bot_type=${filter}`;\
                const response = await fetch(url);\
                if (!response.ok) throw new Error("Error cargando ranking");\
                \
                const data = await response.json();\
                \
                const rankingHtml = `\
                    <table class="licenses-table">\
                        <thead>\
                            <tr>\
                                <th>#</th>\
                                <th>Bot ID</th>\
                                <th>Tipo</th>\
                                <th>Nodo Actual</th>\
                                <th>Puntuación</th>\
                                <th>Ventas</th>\
                                <th>Estado</th>\
                            </tr>\
                        </thead>\
                        <tbody>\
                            ${data.summary?.map((bot, index) => `\
                                <tr onclick="showBotGrowthDetail('\${bot.bot_id}')" style="cursor: pointer;">\
                                    <td>${index + 1}</td>\
                                    <td><span class="license-key">${bot.bot_id.substring(0, 12)}...</span></td>\
                                    <td>${bot.bot_type}</td>\
                                    <td>${getNodeDisplayName(bot.current_node)}</td>\
                                    <td><strong>${bot.growth_score}</strong></td>\
                                    <td>${bot.total_sales}</td>\
                                    <td>\
                                        ${bot.can_upgrade ? \
                                            `<span class="license-status status-valid">Listo para upgrade</span>` : \
                                            `<span class="license-status status-pending">En progreso</span>`\
                                        }\
                                    </td>\
                                </tr>\
                            `).join("") || "<tr><td colspan=\'7\' style=\'text-align: center;\'>No hay datos</td></tr>"}\
                        </tbody>\
                    </table>\
                `;\
                \
                document.getElementById("growth-ranking-table").innerHTML = rankingHtml;\
                \
            } catch (error) {\
                console.error("Error cargando ranking:", error);\
                document.getElementById("growth-ranking-table").innerHTML = \
                    `<p style="color: var(--danger); text-align: center;">Error cargando ranking</p>`;\
            }\
        }\
        \
        function showBotGrowthDetail(botId) {\
            // Cambiar a dashboard y cargar datos del bot específico\
            switchTab("dashboard");\
            \
            // Simular clic en el bot para cargar sus datos\
            setTimeout(() => {\
                const botRow = document.querySelector(`.license-key:contains("${botId.substring(0, 8)}")`)?.closest("tr");\
                if (botRow) {\
                    botRow.click();\
                    loadGrowthData(botId);\
                }\
            }, 500);\
        }' "$ADMIN_HTML_PATH"

echo "✅ 4. Interfaz de crecimiento integrada en admin.HTML"
echo "📋 Backup creado: $ADMIN_HTML_PATH.backup.*"
