"""
📈 MODELOS DE CRECIMIENTO DE NODOS - Integración completa
Conecta con el sistema existente sin romper nada
"""

import sqlite3
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
import hashlib

class GrowthDatabase:
    """Gestor de base de datos para nodos de crecimiento"""
    
    def __init__(self, db_path: str = "neuraforge.db"):
        self.db_path = db_path
        self.init_growth_tables()
    
    def init_growth_tables(self):
        """Inicializa tablas de crecimiento (no afecta tablas existentes)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de nodos de crecimiento (conexión con bots existentes)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS growth_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id VARCHAR(50) NOT NULL,
            bot_type VARCHAR(20) NOT NULL,
            current_node VARCHAR(50) DEFAULT 'nivel_1',
            unlocked_modules TEXT DEFAULT '[]',
            daily_quota INTEGER DEFAULT 100,
            commission_rate DECIMAL(5,2) DEFAULT 10.00,
            total_sales INTEGER DEFAULT 0,
            total_donations DECIMAL(10,2) DEFAULT 0.00,
            growth_score INTEGER DEFAULT 0,
            last_upgrade TIMESTAMP,
            next_upgrade_available TIMESTAMP,
            requirements_met BOOLEAN DEFAULT 0,
            
            -- Relación con tabla bots existente
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE,
            UNIQUE(bot_id)
        )
        ''')
        
        # Tabla de requisitos por nodo
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS node_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_type VARCHAR(20) NOT NULL,
            node_name VARCHAR(50) NOT NULL,
            requirement_type VARCHAR(20) NOT NULL, -- 'donation', 'sales', 'time', 'hybrid'
            requirement_value TEXT NOT NULL, -- JSON con valores
            unlocked_modules TEXT NOT NULL, -- JSON array
            daily_quota INTEGER,
            commission_bonus DECIMAL(5,2),
            special_perks TEXT, -- JSON con beneficios especiales
            display_order INTEGER DEFAULT 0,
            
            UNIQUE(bot_type, node_name)
        )
        ''')
        
        # Tabla de eventos de crecimiento
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS growth_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id VARCHAR(50) NOT NULL,
            event_type VARCHAR(30) NOT NULL, -- 'node_upgrade', 'module_unlock', 'requirement_met'
            from_node VARCHAR(50),
            to_node VARCHAR(50),
            trigger_type VARCHAR(20), -- 'donation', 'sale', 'manual', 'time'
            trigger_value DECIMAL(10,2),
            event_data TEXT, -- JSON con datos adicionales
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
        )
        ''')
        
        # Tabla de progreso hacia siguiente nodo
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS node_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id VARCHAR(50) NOT NULL,
            target_node VARCHAR(50) NOT NULL,
            requirement_type VARCHAR(20) NOT NULL,
            current_value DECIMAL(10,2) DEFAULT 0,
            target_value DECIMAL(10,2) NOT NULL,
            progress_percentage DECIMAL(5,2) DEFAULT 0,
            estimated_completion TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE,
            UNIQUE(bot_id, target_node, requirement_type)
        )
        ''')
        
        # Índices para optimización
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_growth_bot_id ON growth_nodes(bot_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_bot_id ON growth_events(bot_id, created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_progress_bot ON node_progress(bot_id, progress_percentage)')
        
        conn.commit()
        
        # Insertar datos por defecto si no existen
        self.insert_default_nodes(cursor)
        
        conn.close()
        
        print("✅ Tablas de crecimiento inicializadas correctamente")
    
    def insert_default_nodes(self, cursor):
        """Inserta la configuración por defecto de nodos"""
        
        # Verificar si ya existen datos
        cursor.execute("SELECT COUNT(*) FROM node_requirements")
        if cursor.fetchone()[0] > 0:
            return
        
        default_nodes = [
            # SAT BOT
            ('sat', 'nivel_1', 'none', '{}', '["declaracion_anual", "consulta_rfc"]', 100, 10.0, '{"icon": "🌱", "color": "#4CAF50"}', 1),
            ('sat', 'nivel_2', 'hybrid', '{"donation": 500, "sales": 5, "time_days": 7}', '["facturacion_cfdi", "calculo_isr", "contabilidad_basica"]', 500, 20.0, '{"icon": "⚡", "color": "#2196F3", "api_access": true}', 2),
            ('sat', 'nivel_3', 'hybrid', '{"donation": 1500, "sales": 20, "time_days": 30}', '["auditoria_ia", "reportes_avanzados", "api_completa", "soporte_prioritario"]', 9999, 30.0, '{"icon": "👑", "color": "#FFC107", "dashboard": true, "priority": true}', 3),
            
            # PIZZA BOT
            ('pizza', 'nivel_1', 'none', '{}', '["pedidos_basicos", "menu_digital"]', 50, 10.0, '{"icon": "🍕", "color": "#F44336"}', 1),
            ('pizza', 'nivel_2', 'hybrid', '{"donation": 300, "sales": 10, "time_days": 5}', '["inventario_automatico", "reparto_tracking", "marketing_basico"]', 200, 20.0, '{"icon": "🚀", "color": "#9C27B0", "analytics": true}', 2),
            ('pizza', 'nivel_3', 'hybrid', '{"donation": 1000, "sales": 50, "time_days": 20}', '["ia_recomendaciones", "reportes_avanzados", "multi_sucursal", "soporte_24/7"]', 1000, 30.0, '{"icon": "🏆", "color": "#FF9800", "enterprise": true}', 3),
            
            # CRYPTO BOT
            ('crypto', 'nivel_1', 'none', '{}', '["monitoreo_basico", "alertas_simples"]', 100, 10.0, '{"icon": "💰", "color": "#8BC34A"}', 1),
            ('crypto', 'nivel_2', 'hybrid', '{"donation": 400, "sales": 8, "time_days": 10}', '["trading_semiauto", "analisis_tecnico", "portafolio_manager"]', 500, 25.0, '{"icon": "📈", "color": "#3F51B5", "api": true}', 2),
            ('crypto', 'nivel_3', 'hybrid', '{"donation": 1200, "sales": 25, "time_days": 25}', '["trading_algoritmico", "ia_predictiva", "arbitraje", "soporte_vip"]', 9999, 40.0, '{"icon": "🤖", "color": "#E91E63", "vip": true}', 3),
        ]
        
        cursor.executemany('''
            INSERT INTO node_requirements 
            (bot_type, node_name, requirement_type, requirement_value, unlocked_modules, daily_quota, commission_bonus, special_perks, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_nodes)
        
        print("✅ Nodos por defecto insertados")
    
    def get_bot_growth_status(self, bot_id: str) -> Dict:
        """Obtiene estado completo de crecimiento de un bot"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Datos del nodo actual
        cursor.execute('''
            SELECT gn.*, nr.requirement_type, nr.requirement_value, nr.special_perks
            FROM growth_nodes gn
            LEFT JOIN node_requirements nr ON gn.bot_type = nr.bot_type AND gn.current_node = nr.node_name
            WHERE gn.bot_id = ?
        ''', (bot_id,))
        
        growth_data = cursor.fetchone()
        
        if not growth_data:
            return {"error": "Bot no encontrado en sistema de crecimiento"}
        
        # Progreso hacia siguiente nodo
        cursor.execute('''
            SELECT * FROM node_progress 
            WHERE bot_id = ? 
            ORDER BY target_node, requirement_type
        ''', (bot_id,))
        
        progress_data = [dict(row) for row in cursor.fetchall()]
        
        # Eventos recientes
        cursor.execute('''
            SELECT * FROM growth_events 
            WHERE bot_id = ? 
            ORDER BY created_at DESC 
            LIMIT 10
        ''', (bot_id,))
        
        recent_events = [dict(row) for row in cursor.fetchall()]
        
        # Nodos disponibles para upgrade
        cursor.execute('''
            SELECT nr.*, 
                   CASE WHEN gn.current_node = nr.node_name THEN 1 ELSE 0 END as is_current,
                   CASE WHEN gn.current_node < nr.node_name THEN 1 ELSE 0 END as is_upgradeable
            FROM node_requirements nr
            LEFT JOIN growth_nodes gn ON nr.bot_type = gn.bot_type AND gn.bot_id = ?
            WHERE nr.bot_type = (SELECT bot_type FROM growth_nodes WHERE bot_id = ?)
            ORDER BY nr.display_order
        ''', (bot_id, bot_id))
        
        available_nodes = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "bot_id": bot_id,
            "current_node": dict(growth_data),
            "progress": progress_data,
            "recent_events": recent_events,
            "available_nodes": available_nodes,
            "can_upgrade": self.check_upgrade_eligibility(bot_id)
        }
    
    def check_upgrade_eligibility(self, bot_id: str) -> bool:
        """Verifica si el bot puede actualizar de nodo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gn.current_node, gn.total_sales, gn.total_donations, gn.bot_type,
                   nr.requirement_type, nr.requirement_value
            FROM growth_nodes gn
            JOIN node_requirements nr ON gn.bot_type = nr.bot_type AND nr.node_name = (
                SELECT MIN(node_name) 
                FROM node_requirements 
                WHERE bot_type = gn.bot_type AND node_name > gn.current_node
            )
            WHERE gn.bot_id = ?
        ''', (bot_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return False
        
        current_node, total_sales, total_donations, bot_type, req_type, req_value = result
        
        try:
            req_data = json.loads(req_value)
            
            if req_type == 'donation':
                return total_donations >= float(req_data.get('donation', 0))
            elif req_type == 'sales':
                return total_sales >= int(req_data.get('sales', 0))
            elif req_type == 'hybrid':
                donation_ok = total_donations >= float(req_data.get('donation', 0))
                sales_ok = total_sales >= int(req_data.get('sales', 0))
                return donation_ok and sales_ok
            elif req_type == 'none':
                return True
                
        except json.JSONDecodeError:
            return False
        
        return False
    
    def upgrade_bot_node(self, bot_id: str, target_node: str, upgrade_data: Dict = None) -> Dict:
        """Actualiza el bot a un nuevo nodo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Obtener datos actuales
            cursor.execute('SELECT current_node, bot_type FROM growth_nodes WHERE bot_id = ?', (bot_id,))
            result = cursor.fetchone()
            
            if not result:
                return {"success": False, "error": "Bot no encontrado"}
            
            current_node, bot_type = result
            
            # Verificar si ya está en ese nodo
            if current_node == target_node:
                return {"success": False, "error": "El bot ya está en este nodo"}
            
            # Verificar requisitos
            cursor.execute('''
                SELECT requirement_type, requirement_value, unlocked_modules, daily_quota, commission_bonus
                FROM node_requirements
                WHERE bot_type = ? AND node_name = ?
            ''', (bot_type, target_node))
            
            node_info = cursor.fetchone()
            
            if not node_info:
                return {"success": False, "error": "Nodo destino no válido"}
            
            req_type, req_value, unlocked_modules, daily_quota, commission_bonus = node_info
            
            # Actualizar nodo
            cursor.execute('''
                UPDATE growth_nodes 
                SET current_node = ?, 
                    unlocked_modules = ?,
                    daily_quota = ?,
                    commission_rate = ?,
                    last_upgrade = CURRENT_TIMESTAMP,
                    next_upgrade_available = datetime(CURRENT_TIMESTAMP, '+7 days')
                WHERE bot_id = ?
            ''', (target_node, unlocked_modules, daily_quota, commission_bonus, bot_id))
            
            # Registrar evento
            cursor.execute('''
                INSERT INTO growth_events 
                (bot_id, event_type, from_node, to_node, trigger_type, trigger_value, event_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                bot_id, 
                'node_upgrade', 
                current_node, 
                target_node,
                upgrade_data.get('trigger_type', 'manual') if upgrade_data else 'manual',
                upgrade_data.get('trigger_value', 0) if upgrade_data else 0,
                json.dumps(upgrade_data) if upgrade_data else '{}'
            ))
            
            # Actualizar progresos
            cursor.execute('DELETE FROM node_progress WHERE bot_id = ? AND target_node = ?', (bot_id, target_node))
            
            conn.commit()
            
            # Obtener datos actualizados
            updated_data = self.get_bot_growth_status(bot_id)
            
            return {
                "success": True,
                "message": f"✅ Bot actualizado de {current_node} a {target_node}",
                "new_node": target_node,
                "unlocked_modules": json.loads(unlocked_modules),
                "perks": json.loads(node_info[5]) if len(node_info) > 5 else {},
                "updated_data": updated_data
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        
        finally:
            conn.close()
    
    def update_progress(self, bot_id: str, metric_type: str, value: float):
        """Actualiza el progreso del bot hacia el siguiente nodo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Obtener siguiente nodo
            cursor.execute('''
                SELECT gn.current_node, gn.bot_type
                FROM growth_nodes gn
                WHERE gn.bot_id = ?
            ''', (bot_id,))
            
            result = cursor.fetchone()
            
            if not result:
                return
            
            current_node, bot_type = result
            
            cursor.execute('''
                SELECT node_name, requirement_value
                FROM node_requirements
                WHERE bot_type = ? AND node_name > ?
                ORDER BY display_order
                LIMIT 1
            ''', (bot_type, current_node))
            
            next_node = cursor.fetchone()
            
            if not next_node:
                return
            
            target_node, req_value = next_node
            
            try:
                req_data = json.loads(req_value)
                target_value = req_data.get(metric_type, 0)
                
                if target_value > 0:
                    # Calcular porcentaje
                    progress = min(100, (value / target_value) * 100)
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO node_progress
                        (bot_id, target_node, requirement_type, current_value, target_value, progress_percentage, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (bot_id, target_node, metric_type, value, target_value, progress))
                    
                    conn.commit()
                    
            except json.JSONDecodeError:
                pass
                
        except Exception as e:
            print(f"Error actualizando progreso: {e}")
        
        finally:
            conn.close()
