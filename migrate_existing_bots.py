#!/usr/bin/env python3
"""
📊 MIGRADOR DE BOTS EXISTENTES AL SISTEMA DE CRECIMIENTO
Conecta todos los bots actuales con el nuevo sistema
"""

import sqlite3
import json
from datetime import datetime, timedelta
import sys
import os

def migrate_existing_bots():
    """Migra bots existentes al sistema de crecimiento"""
    
    # Ruta a la base de datos principal
    main_db_path = "neuraforge.db"
    growth_db_path = "neuraforge.db"  # Misma base de datos
    
    if not os.path.exists(main_db_path):
        print(f"❌ Base de datos no encontrada: {main_db_path}")
        return
    
    print("🚀 Iniciando migración de bots existentes...")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(main_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Verificar si existe tabla de bots en sistema principal
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bots'")
        if not cursor.fetchone():
            print("⚠️ Tabla 'bots' no encontrada. Buscando otras tablas...")
            
            # Buscar posibles tablas con datos de bots
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"📋 Tablas disponibles: {', '.join(tables)}")
            
            # Intentar encontrar datos de bots
            bots_data = []
            
            for table in tables:
                if 'bot' in table.lower() or 'license' in table.lower():
                    cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                    columns = [desc[0] for desc in cursor.description]
                    print(f"🔍 Tabla {table}: Columnas {columns}")
                    
                    # Intentar extraer datos
                    try:
                        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                        count = cursor.fetchone()['count']
                        print(f"   📊 {count} registros encontrados")
                        
                        # Ejemplo: adaptar según tu estructura real
                        if 'license' in table.lower():
                            cursor.execute(f'''
                                SELECT DISTINCT 
                                    license_key as bot_id,
                                    bot_type,
                                    owner_name,
                                    created_at
                                FROM {table}
                                WHERE license_key IS NOT NULL
                            ''')
                            bots_data.extend(cursor.fetchall())
                            
                    except Exception as e:
                        print(f"   ⚠️ Error leyendo tabla {table}: {e}")
            
            if not bots_data:
                print("❌ No se encontraron datos de bots. Creando datos de ejemplo...")
                bots_data = create_sample_bots()
                
        else:
            # Leer bots de tabla 'bots'
            cursor.execute('''
                SELECT id as bot_id, type as bot_type, owner_id, created_at
                FROM bots
                WHERE id IS NOT NULL
            ''')
            bots_data = cursor.fetchall()
        
        print(f"📊 Encontrados {len(bots_data)} bots para migrar")
        
        # 2. Verificar/crear tablas de crecimiento
        print("🔧 Verificando tablas de crecimiento...")
        
        # Ejecutar el script de inicialización de crecimiento
        from core.database.growth_models import GrowthDatabase
        growth_db = GrowthDatabase()
        
        # 3. Migrar cada bot
        migrated_count = 0
        for bot in bots_data:
            bot_id = bot['bot_id']
            bot_type = bot.get('bot_type', 'sat')  # Default a SAT si no hay tipo
            
            # Verificar si ya está migrado
            cursor.execute('SELECT COUNT(*) as count FROM growth_nodes WHERE bot_id = ?', (bot_id,))
            if cursor.fetchone()['count'] > 0:
                print(f"   ⏭️  Bot {bot_id} ya migrado, omitiendo...")
                continue
            
            # Determinar nodo inicial basado en actividad
            current_node = 'nivel_1'
            total_sales = 0
            total_donations = 0.0
            
            # Intentar obtener métricas del sistema principal
            try:
                # Buscar ventas relacionadas
                cursor.execute('''
                    SELECT COUNT(*) as sales_count, SUM(amount) as total_amount
                    FROM sales 
                    WHERE bot_id = ? OR affiliate_id = ?
                ''', (bot_id, bot_id))
                
                sales_data = cursor.fetchone()
                total_sales = sales_data['sales_count'] or 0
                
                # Buscar donaciones
                cursor.execute('''
                    SELECT SUM(amount) as total_donations
                    FROM donations 
                    WHERE bot_id = ? OR user_id = ?
                ''', (bot_id, bot_id))
                
                donations_data = cursor.fetchone()
                total_donations = donations_data['total_donations'] or 0.0
                
                # Determinar nodo basado en actividad
                if total_donations >= 1500 or total_sales >= 20:
                    current_node = 'nivel_3'
                elif total_donations >= 500 or total_sales >= 5:
                    current_node = 'nivel_2'
                
            except sqlite3.OperationalError:
                # Las tablas pueden no existir
                print(f"   ⚠️  No se encontraron métricas para {bot_id}, usando valores por defecto")
            
            # Obtener módulos desbloqueados según nodo
            cursor.execute('''
                SELECT unlocked_modules FROM node_requirements 
                WHERE bot_type = ? AND node_name = ?
            ''', (bot_type, current_node))
            
            modules_result = cursor.fetchone()
            unlocked_modules = modules_result['unlocked_modules'] if modules_result else '[]'
            
            # Calcular puntuación de crecimiento
            created_at = bot.get('created_at', datetime.now().isoformat())
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                active_days = (datetime.now() - created_date).days
            except:
                active_days = 30  # Default
            
            growth_score = (total_sales * 10) + (total_donations * 2) + (active_days * 5)
            growth_score = min(1000, growth_score)
            
            # Insertar en growth_nodes
            cursor.execute('''
                INSERT INTO growth_nodes 
                (bot_id, bot_type, current_node, unlocked_modules, 
                 daily_quota, commission_rate, total_sales, total_donations, 
                 growth_score, last_upgrade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bot_id,
                bot_type,
                current_node,
                unlocked_modules,
                100 if current_node == 'nivel_1' else 500 if current_node == 'nivel_2' else 9999,
                10.0 if current_node == 'nivel_1' else 20.0 if current_node == 'nivel_2' else 30.0,
                total_sales,
                total_donations,
                growth_score,
                datetime.now().isoformat()
            ))
            
            # Registrar evento
            cursor.execute('''
                INSERT INTO growth_events 
                (bot_id, event_type, to_node, trigger_type, event_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                bot_id,
                'bot_migrated',
                current_node,
                'migration',
                json.dumps({
                    'original_data': dict(bot),
                    'migration_date': datetime.now().isoformat(),
                    'calculated_metrics': {
                        'sales': total_sales,
                        'donations': total_donations,
                        'active_days': active_days,
                        'growth_score': growth_score
                    }
                })
            ))
            
            migrated_count += 1
            print(f"   ✅ Migrado bot {bot_id} a nodo {current_node} (score: {growth_score})")
        
        conn.commit()
        
        # 4. Actualizar progresos
        print("🔄 Actualizando progresos de crecimiento...")
        
        cursor.execute('SELECT bot_id FROM growth_nodes')
        all_bots = [row[0] for row in cursor.fetchall()]
        
        for bot_id in all_bots:
            # Obtener datos del bot
            cursor.execute('''
                SELECT gn.current_node, gn.total_sales, gn.total_donations, gn.bot_type
                FROM growth_nodes gn
                WHERE gn.bot_id = ?
            ''', (bot_id,))
            
            bot_data = cursor.fetchone()
            
            if bot_data:
                current_node, total_sales, total_donations, bot_type = bot_data
                
                # Buscar siguiente nodo
                cursor.execute('''
                    SELECT node_name, requirement_value
                    FROM node_requirements
                    WHERE bot_type = ? AND node_name > ?
                    ORDER BY display_order
                    LIMIT 1
                ''', (bot_type, current_node))
                
                next_node = cursor.fetchone()
                
                if next_node:
                    target_node, req_value = next_node
                    
                    try:
                        req_data = json.loads(req_value)
                        
                        # Actualizar progreso para cada requisito
                        for req_type, target_value in req_data.items():
                            if req_type in ['sales', 'donation']:
                                current_value = total_sales if req_type == 'sales' else total_donations
                                progress = min(100, (current_value / target_value) * 100) if target_value > 0 else 0
                                
                                cursor.execute('''
                                    INSERT OR REPLACE INTO node_progress
                                    (bot_id, target_node, requirement_type, current_value, target_value, progress_percentage)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (bot_id, target_node, req_type, current_value, target_value, progress))
                                
                    except json.JSONDecodeError:
                        pass
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 MIGRACIÓN COMPLETADA!")
        print(f"✅ Total bots migrados: {migrated_count}")
        print(f"📊 Base de datos actualizada: {main_db_path}")
        
        # Mostrar resumen
        show_migration_summary(main_db_path)
        
    except Exception as e:
        print(f"❌ Error durante migración: {e}")
        import traceback
        traceback.print_exc()

def create_sample_bots():
    """Crea datos de bots de ejemplo si no hay datos reales"""
    print("🔧 Creando datos de bots de ejemplo...")
    
    sample_bots = [
        {'bot_id': 'SAT-001', 'bot_type': 'sat', 'owner_name': 'Juan Pérez', 'created_at': '2024-01-15'},
        {'bot_id': 'SAT-002', 'bot_type': 'sat', 'owner_name': 'María López', 'created_at': '2024-02-20'},
        {'bot_id': 'PIZZA-001', 'bot_type': 'pizza', 'owner_name': 'Carlos Ruiz', 'created_at': '2024-03-10'},
        {'bot_id': 'CRYPTO-001', 'bot_type': 'crypto', 'owner_name': 'Ana García', 'created_at': '2024-04-05'},
        {'bot_id': 'SAT-003', 'bot_type': 'sat', 'owner_name': 'Pedro Martínez', 'created_at': '2024-05-12'}
    ]
    
    return sample_bots

def show_migration_summary(db_path):
    """Muestra resumen de la migración"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Estadísticas generales
    cursor.execute('SELECT COUNT(*) as total FROM growth_nodes')
    total_bots = cursor.fetchone()['total']
    
    cursor.execute('''
        SELECT bot_type, COUNT(*) as count, 
               AVG(growth_score) as avg_score,
               SUM(total_sales) as total_sales,
               SUM(total_donations) as total_donations
        FROM growth_nodes
        GROUP BY bot_type
    ''')
    
    print("\n📈 RESUMEN DE MIGRACIÓN:")
    print("=" * 50)
    
    for row in cursor.fetchall():
        print(f"\n🤖 {row['bot_type'].upper()} Bots:")
        print(f"   Cantidad: {row['count']}")
        print(f"   Puntuación promedio: {row['avg_score']:.1f}")
        print(f"   Ventas totales: {row['total_sales']}")
        print(f"   Donaciones totales: ${row['total_donations']:.2f}")
    
    # Distribución por nodo
    cursor.execute('''
        SELECT current_node, COUNT(*) as count,
               (COUNT(*) * 100.0 / ?) as percentage
        FROM growth_nodes
        GROUP BY current_node
        ORDER BY current_node
    ''', (total_bots,))
    
    print(f"\n🌳 DISTRIBUCIÓN POR NODO (Total: {total_bots} bots):")
    for row in cursor.fetchall():
        node_name = row['current_node']
        display_name = {
            'nivel_1': '🌱 Nodo Básico',
            'nivel_2': '⚡ Nodo Avanzado',
            'nivel_3': '👑 Nodo Maestro'
        }.get(node_name, node_name)
        
        print(f"   {display_name}: {row['count']} bots ({row['percentage']:.1f}%)")
    
    # Bots listos para upgrade
    cursor.execute('''
        SELECT COUNT(*) as ready_count
        FROM growth_nodes gn
        WHERE EXISTS (
            SELECT 1 FROM node_requirements nr
            WHERE nr.bot_type = gn.bot_type 
            AND nr.node_name > gn.current_node
            AND (
                (nr.requirement_type = 'donation' AND gn.total_donations >= json_extract(nr.requirement_value, '$.donation')) OR
                (nr.requirement_type = 'sales' AND gn.total_sales >= json_extract(nr.requirement_value, '$.sales')) OR
                (nr.requirement_type = 'hybrid' AND 
                 gn.total_donations >= json_extract(nr.requirement_value, '$.donation') AND
                 gn.total_sales >= json_extract(nr.requirement_value, '$.sales'))
            )
        )
    ''')
    
    ready_count = cursor.fetchone()['ready_count']
    print(f"\n🚀 Bots listos para upgrade: {ready_count} ({ready_count/total_bots*100:.1f}%)")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Migración completada exitosamente!")
    print("🎯 Los bots ahora tienen sistema de crecimiento activo")

if __name__ == "__main__":
    print("🚀 NEURAFORGE AI - MIGRADOR DE SISTEMA DE CRECIMIENTO")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("core"):
        print("❌ Error: Debes ejecutar este script desde el directorio raíz de NeuraForge")
        print("   Directorio actual:", os.getcwd())
        sys.exit(1)
    
    migrate_existing_bots()
    
    print("\n🎯 Próximos pasos:")
    print("1. Reinicia el servidor: python main.py")
    print("2. Verifica el panel admin en http://localhost:8080")
    print("3. Los bots ahora mostrarán su progreso de crecimiento")
