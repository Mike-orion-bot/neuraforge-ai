"""
🚀 GESTOR DE CRECIMIENTO - Sistema principal de nodos
Conecta con toda la infraestructura existente
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .database.growth_models import GrowthDatabase
from .database.models import DatabaseManager  # Sistema existente

class GrowthManager:
    """Gestor principal del sistema de crecimiento"""
    
    def __init__(self):
        self.growth_db = GrowthDatabase()
        self.main_db = DatabaseManager()  # Base de datos principal existente
        
        # Configuración de nodos por tipo de bot
        self.node_configs = {
            'sat': {
                'levels': ['nivel_1', 'nivel_2', 'nivel_3'],
                'display_name': '🌱 SAT Assistant Pro',
                'color_scheme': 'var(--sat-accent)'
            },
            'pizza': {
                'levels': ['nivel_1', 'nivel_2', 'nivel_3'],
                'display_name': '🍕 Pizza Delivery Master',
                'color_scheme': 'var(--pizza-accent)'
            },
            'crypto': {
                'levels': ['nivel_1', 'nivel_2', 'nivel_3'],
                'display_name': '💰 Crypto Trading Pro',
                'color_scheme': 'var(--crypto-accent)'
            }
        }

   async def get_meta_ai_config_for_bot(self, bot_id: str):
    """Devuelve qué modelo de Meta AI usar según el nivel del bot (Monetización)"""
    status = self.growth_db.get_bot_growth_status(bot_id)
    
    if 'error' in status:
        return {"model": "Muse Spark Contributor", "cost": 0.10} # Default barato
    
    nivel = status['current_node']['current_node']
    bot_type = status['current_node']['bot_type']
    
    # Configuración de modelos Meta por nivel
    if nivel == 'nivel_3':
        # Premium: Imágenes y Código
        return {
            "model": "Muse Image", 
            "cost": 0.01,
            "features": ["generacion_imagenes_premium", "analisis_codigo"],
            "server": "google_cloud_premium"
        }
    elif nivel == 'nivel_2':
        # Intermedio: Soporte avanzado con contexto 1M
        return {
            "model": "Muse Spark 1.2", 
            "cost": 1.25,
            "features": ["analisis_datos", "soporte_avanzado"],
            "server": "google_cloud_standard"
        }
    else:
        # Básico: Chat barato para no perder dinero
        return {
            "model": "Muse Spark 1.2 Contributor", 
            "cost": 0.10,
            "features": ["chat_basico", "textos_venta"],
            "server": "google_cloud_basic"
        }
    async def initialize_bot_growth(self, bot_id: str, bot_type: str, owner_id: str = None):
        """Inicializa el sistema de crecimiento para un bot nuevo"""
        
        # Verificar si ya existe
        status = self.growth_db.get_bot_growth_status(bot_id)
        if 'error' not in status:
            return status
        
        # Crear entrada inicial
        conn = self.growth_db.db_path
        import sqlite3
        db = sqlite3.connect(conn)
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO growth_nodes 
            (bot_id, bot_type, current_node, unlocked_modules, daily_quota, commission_rate)
            VALUES (?, ?, 'nivel_1', ?, 100, 10.0)
        ''', (bot_id, bot_type, json.dumps(self.get_initial_modules(bot_type))))
        
        # Registrar evento
        cursor.execute('''
            INSERT INTO growth_events 
            (bot_id, event_type, to_node, trigger_type, event_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (bot_id, 'bot_created', 'nivel_1', 'system', json.dumps({
            'bot_type': bot_type,
            'owner': owner_id,
            'timestamp': datetime.now().isoformat()
        })))
        
        db.commit()
        db.close()
        
        # Sincronizar con sistema principal
        await self.sync_with_main_system(bot_id)
        
        return self.growth_db.get_bot_growth_status(bot_id)
    
    def get_initial_modules(self, bot_type: str) -> List[str]:
        """Obtiene módulos iniciales según tipo de bot"""
        modules_map = {
            'sat': ['declaracion_anual', 'consulta_rfc', 'guia_basica'],
            'pizza': ['pedidos_basicos', 'menu_digital', 'clientes_registro'],
            'crypto': ['monitoreo_basico', 'alertas_simples', 'portafolio_basico']
        }
        return modules_map.get(bot_type, [])
    
    async def sync_with_main_system(self, bot_id: str):
        """Sincroniza datos con el sistema principal"""
        try:
            # Obtener datos del bot del sistema principal
            main_bot_data = self.main_db.get_bot_by_id(bot_id)
            
            if main_bot_data:
                # Extraer métricas importantes
                total_sales = main_bot_data.get('total_sales', 0)
                total_donations = main_bot_data.get('total_donations', 0.0)
                active_days = main_bot_data.get('active_days', 1)
                
                # Actualizar en sistema de crecimiento
                conn = self.growth_db.db_path
                import sqlite3
                db = sqlite3.connect(conn)
                cursor = db.cursor()
                
                cursor.execute('''
                    UPDATE growth_nodes 
                    SET total_sales = ?, total_donations = ?, growth_score = ?
                    WHERE bot_id = ?
                ''', (total_sales, total_donations, self.calculate_growth_score(total_sales, total_donations, active_days), bot_id))
                
                # Actualizar progresos
                self.growth_db.update_progress(bot_id, 'sales', total_sales)
                self.growth_db.update_progress(bot_id, 'donation', total_donations)
                
                db.commit()
                db.close()
                
        except Exception as e:
            print(f"⚠️ Error en sincronización: {e}")
    
    def calculate_growth_score(self, sales: int, donations: float, active_days: int) -> int:
        """Calcula puntuación de crecimiento del bot"""
        score = (sales * 10) + (donations * 2) + (active_days * 5)
        return min(1000, score)  # Máximo 1000 puntos
    
    async def process_donation_for_growth(self, bot_id: str, amount: float, payment_method: str = None):
        """Procesa una donación y actualiza crecimiento"""
        
        # Registrar donación en sistema principal (existente)
        donation_result = await self.record_donation_in_main(bot_id, amount, payment_method)
        
        if donation_result.get('success'):
            # Actualizar en sistema de crecimiento
            conn = self.growth_db.db_path
            import sqlite3
            db = sqlite3.connect(conn)
            cursor = db.cursor()
            
            cursor.execute('''
                UPDATE growth_nodes 
                SET total_donations = total_donations + ?
                WHERE bot_id = ?
            ''', (amount, bot_id))
            
            # Registrar evento
            cursor.execute('''
                INSERT INTO growth_events 
                (bot_id, event_type, trigger_type, trigger_value, event_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                bot_id, 
                'donation_received',
                'donation',
                amount,
                json.dumps({
                    'amount': amount,
                    'method': payment_method,
                    'timestamp': datetime.now().isoformat()
                })
            ))
            
            db.commit()
            db.close()
            
            # Actualizar progreso
            self.growth_db.update_progress(bot_id, 'donation', 
                self.get_total_donations(bot_id) + amount)
            
            # Verificar si desbloquea nuevo nodo
            upgrade_check = await self.check_and_upgrade_node(bot_id, 'donation', amount)
            
            return {
                **donation_result,
                'growth_updated': True,
                'possible_upgrade': upgrade_check.get('can_upgrade', False)
            }
        
        return donation_result
    
    async def record_donation_in_main(self, bot_id: str, amount: float, method: str) -> Dict:
        """Registra donación en sistema principal (método existente)"""
        # Aquí integras con tu sistema de pagos existente
        # Este es un placeholder - debes conectarlo con tu payment processor real
        
        try:
            # Simulación de conexión con sistema existente
            # En producción, usa tu módulo de pagos real
            from core.payment.processor import PaymentProcessor
            
            processor = PaymentProcessor()
            result = await processor.process_donation({
                'bot_id': bot_id,
                'amount': amount,
                'currency': 'MXN',
                'method': method,
                'purpose': 'growth_upgrade'
            })
            
            return {
                'success': True,
                'transaction_id': result.get('id'),
                'message': 'Donación procesada exitosamente'
            }
            
        except ImportError:
            # Si no existe el módulo, simular éxito
            print(f"⚠️ Módulo de pagos no encontrado, simulando donación de ${amount}")
            return {
                'success': True,
                'transaction_id': f"DON_{bot_id}_{int(datetime.now().timestamp())}",
                'message': 'Donación simulada (integra con tu sistema real)'
            }
    
    def get_total_donations(self, bot_id: str) -> float:
        """Obtiene total de donaciones de un bot"""
        conn = self.growth_db.db_path
        import sqlite3
        db = sqlite3.connect(conn)
        cursor = db.cursor()
        
        cursor.execute('SELECT total_donations FROM growth_nodes WHERE bot_id = ?', (bot_id,))
        result = cursor.fetchone()
        db.close()
        
        return result[0] if result else 0.0
    
    async def check_and_upgrade_node(self, bot_id: str, trigger_type: str, trigger_value: float = None) -> Dict:
        """Verifica y aplica upgrade automático si se cumplen requisitos"""
        
        can_upgrade = self.growth_db.check_upgrade_eligibility(bot_id)
        
        if can_upgrade:
            # Obtener siguiente nodo
            status = self.growth_db.get_bot_growth_status(bot_id)
            current_node = status['current_node']['current_node']
            
            # Encontrar siguiente nodo
            bot_type = status['current_node']['bot_type']
            current_level = self.node_configs[bot_type]['levels'].index(current_node)
            
            if current_level < len(self.node_configs[bot_type]['levels']) - 1:
                next_node = self.node_configs[bot_type]['levels'][current_level + 1]
                
                # Aplicar upgrade
                upgrade_result = self.growth_db.upgrade_bot_node(bot_id, next_node, {
                    'trigger_type': trigger_type,
                    'trigger_value': trigger_value,
                    'auto_upgrade': True
                })
                
                if upgrade_result['success']:
                    # Notificar al sistema principal
                    await self.notify_main_system_upgrade(bot_id, current_node, next_node)
                    
                    return {
                        'success': True,
                        'upgraded': True,
                        'from_node': current_node,
                        'to_node': next_node,
                        'message': f'¡Bot actualizado automáticamente a {next_node}!'
                    }
        
        return {
            'success': True,
            'upgraded': False,
            'can_upgrade': can_upgrade,
            'message': 'Requisitos no cumplidos para upgrade'
        }
    
    async def notify_main_system_upgrade(self, bot_id: str, from_node: str, to_node: str):
        """Notifica al sistema principal sobre el upgrade"""
        # Aquí debes conectar con tu sistema de notificaciones existente
        
        try:
            # Ejemplo: Actualizar licencia del bot
            from core.token import LicenseManager
            
            license_mgr = LicenseManager()
            await license_mgr.upgrade_bot_license(bot_id, {
                'new_tier': to_node,
                'old_tier': from_node,
                'unlocked_features': self.get_node_features(to_node)
            })
            
        except ImportError:
            print(f"⚠️ Sistema de licencias no encontrado, upgrade registrado solo en crecimiento")
    
    def get_node_features(self, node_name: str) -> List[str]:
        """Obtiene características desbloqueadas por nodo"""
        features_map = {
            'nivel_1': ['funcionalidades_basicas', 'soporte_email'],
            'nivel_2': ['api_access', 'analytics', 'soporte_prioritario'],
            'nivel_3': ['dashboard_avanzado', 'ia_integrada', 'soporte_vip', 'customization']
        }
        return features_map.get(node_name, [])
    
    def get_growth_dashboard_data(self, bot_id: str) -> Dict:
        """Obtiene datos para dashboard de crecimiento"""
        growth_status = self.growth_db.get_bot_growth_status(bot_id)
        
        if 'error' in growth_status:
            return {}
        
        # Calcular estadísticas
        current = growth_status['current_node']
        progress = growth_status['progress']
        
        # Agrupar progreso por nodo
        progress_by_node = {}
        for p in progress:
            node = p['target_node']
            if node not in progress_by_node:
                progress_by_node[node] = []
            progress_by_node[node].append(p)
        
        # Calcular progreso general por nodo
        node_progress = {}
        for node, metrics in progress_by_node.items():
            total_progress = sum(m['progress_percentage'] for m in metrics)
            avg_progress = total_progress / len(metrics) if metrics else 0
            node_progress[node] = {
                'percentage': avg_progress,
                'metrics': metrics
            }
        
        # Obtener siguiente nodo objetivo
        next_node = None
        if growth_status['available_nodes']:
            for node in growth_status['available_nodes']:
                if not node['is_current'] and node['is_upgradeable']:
                    next_node = node
                    break
        
        return {
            'current_node': {
                'name': current['current_node'],
                'display_name': self.get_node_display_name(current['current_node']),
                'modules': json.loads(current.get('unlocked_modules', '[]')),
                'quota': current['daily_quota'],
                'commission': current['commission_rate']
            },
            'progress': node_progress,
            'next_node': next_node,
            'recent_events': growth_status['recent_events'][:5],
            'growth_score': current['growth_score'],
            'can_upgrade': growth_status.get('can_upgrade', False)
        }
    
    def get_node_display_name(self, node_code: str) -> str:
        """Obtiene nombre para mostrar del nodo"""
        display_names = {
            'nivel_1': '🌱 Nodo Básico',
            'nivel_2': '⚡ Nodo Avanzado',
            'nivel_3': '👑 Nodo Maestro'
        }
        return display_names.get(node_code, node_code)
    
    async def get_all_bots_growth_summary(self, owner_id: str = None) -> List[Dict]:
        """Obtiene resumen de crecimiento de todos los bots"""
        
        # Conectar con sistema principal para obtener bots del dueño
        try:
            if owner_id:
                user_bots = self.main_db.get_user_bots(owner_id)
                bot_ids = [bot['id'] for bot in user_bots]
            else:
                # Todos los bots (admin)
                all_bots = self.main_db.get_all_bots()
                bot_ids = [bot['id'] for bot in all_bots]
                
        except:
            # Fallback: obtener de growth_nodes
            conn = self.growth_db.db_path
            import sqlite3
            db = sqlite3.connect(conn)
            cursor = db.cursor()
            
            if owner_id:
                # Necesitarías tener owner_id en growth_nodes o conectarlo
                cursor.execute('SELECT bot_id FROM growth_nodes')
            else:
                cursor.execute('SELECT bot_id FROM growth_nodes')
            
            bot_ids = [row[0] for row in cursor.fetchall()]
            db.close()
        
        # Obtener datos de cada bot
        summaries = []
        for bot_id in bot_ids[:50]:  # Limitar a 50 para performance
            try:
                status = self.growth_db.get_bot_growth_status(bot_id)
                if 'error' not in status:
                    current = status['current_node']
                    summaries.append({
                        'bot_id': bot_id,
                        'bot_type': current['bot_type'],
                        'current_node': current['current_node'],
                        'growth_score': current['growth_score'],
                        'total_sales': current['total_sales'],
                        'total_donations': current['total_donations'],
                        'last_upgrade': current['last_upgrade'],
                        'can_upgrade': status.get('can_upgrade', False)
                    })
            except:
                continue
        
        # Ordenar por crecimiento
        summaries.sort(key=lambda x: x['growth_score'], reverse=True)
        
        return summaries

# Singleton para acceso global
growth_manager = GrowthManager()
