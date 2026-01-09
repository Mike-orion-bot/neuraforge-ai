"""
🌐 API ENDPOINTS PARA SISTEMA DE CRECIMIENTO
Endpoints REST para integración con frontend y apps
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from pydantic import BaseModel
import asyncio

# Importar nuestro gestor de crecimiento
try:
    from core.growth_manager import growth_manager
    GROWTH_ENABLED = True
except ImportError:
    GROWTH_ENABLED = False
    print("⚠️ Sistema de crecimiento no disponible")

router = APIRouter(prefix="/api/growth", tags=["growth"])

# Modelos Pydantic
class GrowthStatusResponse(BaseModel):
    bot_id: str
    current_node: Dict
    progress: List[Dict]
    recent_events: List[Dict]
    available_nodes: List[Dict]
    can_upgrade: bool

class UpgradeRequest(BaseModel):
    target_node: str
    payment_method: Optional[str] = None
    confirm: bool = False

class DonationRequest(BaseModel):
    amount: float
    payment_method: str
    bot_id: str
    purpose: Optional[str] = "growth_upgrade"

class GrowthSummary(BaseModel):
    bot_id: str
    bot_type: str
    current_node: str
    growth_score: int
    total_sales: int
    total_donations: float
    last_upgrade: Optional[str]
    can_upgrade: bool

# Endpoints
@router.get("/status/{bot_id}", response_model=GrowthStatusResponse)
async def get_growth_status(bot_id: str):
    """Obtiene estado completo de crecimiento de un bot"""
    if not GROWTH_ENABLED:
        raise HTTPException(status_code=501, detail="Sistema de crecimiento no disponible")
    
    try:
        status = growth_manager.growth_db.get_bot_growth_status(bot_id)
        
        if 'error' in status:
            # Intentar inicializar si no existe
            bot_type = await get_bot_type_from_main(bot_id)
            if bot_type:
                status = await growth_manager.initialize_bot_growth(bot_id, bot_type)
            else:
                raise HTTPException(status_code=404, detail="Bot no encontrado")
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")

@router.post("/upgrade/{bot_id}")
async def request_upgrade(bot_id: str, request: UpgradeRequest):
    """Solicita upgrade de nodo para un bot"""
    if not GROWTH_ENABLED:
        raise HTTPException(status_code=501, detail="Sistema de crecimiento no disponible")
    
    try:
        # Verificar elegibilidad
        can_upgrade = growth_manager.growth_db.check_upgrade_eligibility(bot_id)
        
        if not can_upgrade:
            # Obtener requisitos faltantes
            status = growth_manager.growth_db.get_bot_growth_status(bot_id)
            current = status['current_node']
            
            # Buscar requisitos del nodo objetivo
            import json
            import sqlite3
            from core.database.growth_models import GrowthDatabase
            
            db = GrowthDatabase()
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT requirement_value FROM node_requirements
                WHERE bot_type = ? AND node_name = ?
            ''', (current['bot_type'], request.target_node))
            
            result = cursor.fetchone()
            conn.close()
            
            requirements = json.loads(result[0]) if result else {}
            
            # Obtener valores actuales
            current_sales = current['total_sales']
            current_donations = current['total_donations']
            
            missing = []
            if 'sales' in requirements and current_sales < requirements['sales']:
                missing.append(f"{requirements['sales'] - current_sales} ventas más")
            if 'donation' in requirements and current_donations < requirements['donation']:
                missing.append(f"${requirements['donation'] - current_donations:.2f} MXN en donaciones")
            
            return {
                "success": False,
                "can_upgrade": False,
                "missing_requirements": missing,
                "requirements": requirements,
                "current_values": {
                    "sales": current_sales,
                    "donations": current_donations
                }
            }
        
        # Procesar upgrade
        if request.payment_method and request.confirm:
            # Procesar pago primero
            from core.payment.processor import PaymentProcessor
            
            processor = PaymentProcessor()
            
            # Determinar monto necesario
            node_cost = await get_node_cost(bot_id, request.target_node)
            
            payment_result = await processor.process_upgrade_payment({
                'bot_id': bot_id,
                'amount': node_cost,
                'method': request.payment_method,
                'node': request.target_node
            })
            
            if not payment_result.get('success'):
                raise HTTPException(status_code=402, detail=f"Pago fallido: {payment_result.get('error')}")
        
        # Aplicar upgrade
        upgrade_data = {
            'trigger_type': 'manual',
            'payment_method': request.payment_method
        }
        
        result = growth_manager.growth_db.upgrade_bot_node(bot_id, request.target_node, upgrade_data)
        
        if result['success']:
            # Sincronizar con sistema principal
            await growth_manager.sync_with_main_system(bot_id)
            
            return {
                "success": True,
                "message": result['message'],
                "new_node": result['new_node'],
                "unlocked_modules": result['unlocked_modules']
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en upgrade: {str(e)}")

@router.post("/donate")
async def process_growth_donation(request: DonationRequest):
    """Procesa una donación para crecimiento"""
    if not GROWTH_ENABLED:
        raise HTTPException(status_code=501, detail="Sistema de crecimiento no disponible")
    
    try:
        result = await growth_manager.process_donation_for_growth(
            request.bot_id, 
            request.amount, 
            request.payment_method
        )
        
        if result.get('success'):
            return {
                "success": True,
                "transaction_id": result.get('transaction_id'),
                "message": result.get('message'),
                "growth_updated": result.get('growth_updated', True),
                "possible_upgrade": result.get('possible_upgrade', False)
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Error desconocido'))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando donación: {str(e)}")

@router.get("/dashboard/{bot_id}")
async def get_growth_dashboard(bot_id: str):
    """Obtiene datos para dashboard de crecimiento"""
    if not GROWTH_ENABLED:
        raise HTTPException(status_code=501, detail="Sistema de crecimiento no disponible")
    
    try:
        dashboard_data = growth_manager.get_growth_dashboard_data(bot_id)
        
        if not dashboard_data:
            raise HTTPException(status_code=404, detail="Bot no encontrado en sistema de crecimiento")
        
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo dashboard: {str(e)}")

@router.get("/summary")
async def get_growth_summary(
    owner_id: Optional[str] = Query(None, description="ID del dueño para filtrar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados")
):
    """Obtiene resumen de crecimiento de múltiples bots"""
    if not GROWTH_ENABLED:
        raise HTTPException(status_code=501, detail="Sistema de crecimiento no disponible")
    
    try:
        summaries = await growth_manager.get_all_bots_growth_summary(owner_id)
        
        return {
            "total_bots": len(summaries),
            "summary": summaries[:limit],
            "stats": calculate_growth_stats(summaries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen: {str(e)}")

@router.get("/nodes/{bot_type}")
async def get_available_nodes(bot_type: str):
    """Obtiene todos los nodos disponibles para un tipo de bot"""
    if not GROWTH_ENABLED:
        raise HTTPException(status_code=501, detail="Sistema de crecimiento no disponible")
    
    try:
        import sqlite3
        from core.database.growth_models import GrowthDatabase
        
        db = GrowthDatabase()
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM node_requirements 
            WHERE bot_type = ? 
            ORDER BY display_order
        ''', (bot_type,))
        
        nodes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "bot_type": bot_type,
            "nodes": nodes,
            "total_levels": len(nodes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo nodos: {str(e)}")

# Funciones auxiliares
async def get_bot_type_from_main(bot_id: str) -> Optional[str]:
    """Obtiene tipo de bot desde sistema principal"""
    try:
        from core.database.models import DatabaseManager
        db = DatabaseManager()
        bot_data = db.get_bot_by_id(bot_id)
        return bot_data.get('type') if bot_data else None
    except:
        return None

async def get_node_cost(bot_id: str, node_name: str) -> float:
    """Obtiene costo de un nodo"""
    try:
        import sqlite3
        from core.database.growth_models import GrowthDatabase
        
        db = GrowthDatabase()
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gn.bot_type FROM growth_nodes gn WHERE gn.bot_id = ?
        ''', (bot_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return 0.0
        
        bot_type = result[0]
        
        cursor.execute('''
            SELECT requirement_value FROM node_requirements
            WHERE bot_type = ? AND node_name = ?
        ''', (bot_type, node_name))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            import json
            req_data = json.loads(result[0])
            return float(req_data.get('donation', 0))
        
        return 0.0
        
    except:
        return 0.0

def calculate_growth_stats(summaries: List[Dict]) -> Dict:
    """Calcula estadísticas de crecimiento"""
    if not summaries:
        return {}
    
    total_bots = len(summaries)
    avg_growth_score = sum(s['growth_score'] for s in summaries) / total_bots
    total_sales = sum(s['total_sales'] for s in summaries)
    total_donations = sum(s['total_donations'] for s in summaries)
    
    # Distribución por nodo
    node_distribution = {}
    for s in summaries:
        node = s['current_node']
        node_distribution[node] = node_distribution.get(node, 0) + 1
    
    # Bots listos para upgrade
    ready_for_upgrade = sum(1 for s in summaries if s['can_upgrade'])
    
    return {
        "total_bots": total_bots,
        "average_growth_score": round(avg_growth_score, 2),
        "total_sales": total_sales,
        "total_donations": round(total_donations, 2),
        "node_distribution": node_distribution,
        "ready_for_upgrade": ready_for_upgrade,
        "upgrade_rate": round((ready_for_upgrade / total_bots) * 100, 2) if total_bots > 0 else 0
    }
