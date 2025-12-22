#!/usr/bin/env python3
"""
Test de Conexión a Bases de Datos FactorIT (Odoo)
==================================================

Prueba la conexión a las bases de datos de:
- FactorIT SpA (DB: FactorIT)
- FactorIT Ltda (DB: FactorIT2)

Uso:
    python -m odoo.test_connection
    
Variables de entorno requeridas en .env:
    SERVER=host_del_servidor
    PORT=5432
    USER=usuario_db
    PASSWORD=password_db
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar que psycopg2 esté instalado
try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 no está instalado.")
    print("   Ejecuta: pip install psycopg2-binary")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

# Credenciales desde .env (limpiando espacios extra)
def get_env_clean(key, default=None):
    """Obtiene variable de entorno y limpia espacios/tabs."""
    val = os.getenv(key)
    return val.strip() if val else default

DB_CONFIG = {
    'host': get_env_clean('SERVER'),
    'port': get_env_clean('PORT', '5432'),
    'user': get_env_clean('DB_USER'),  # Usar DB_USER para evitar conflicto con USER del sistema
    'password': get_env_clean('PASSWORD'),
}

# Bases de datos a probar
DATABASES = {
    'FactorIT': {
        'name': 'FactorIT',
        'empresa': 'FactorIT SpA',
    },
    'FactorIT2': {
        'name': 'FactorIT2',
        'empresa': 'FactorIT Ltda',
    },
}

# Query para documentos pendientes SII
QUERY_PENDIENTES_SII = """
SELECT 
    a.date, 
    b.doc_code_prefix, 
    a.number, 
    a.new_partner, 
    a.amount 
FROM mail_message_dte_document a,
     sii_document_class b
WHERE a.state = 'draft' 
  AND a.document_class_id = b.id
ORDER BY a.date DESC
"""


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES
# ═══════════════════════════════════════════════════════════════════════════════

def verificar_config():
    """Verifica que las variables de entorno estén configuradas."""
    print("\n📋 Verificando configuración...")
    print("─" * 50)
    
    errores = []
    for key in ['host', 'user', 'password']:
        valor = DB_CONFIG.get(key)
        if not valor:
            errores.append(f"   ❌ {key.upper()} no está configurado en .env")
        else:
            # Mostrar parcialmente (por seguridad)
            if key == 'password':
                mostrar = '*' * len(valor)
            else:
                mostrar = valor
            print(f"   ✅ {key.upper()}: {mostrar}")
    
    print(f"   ✅ PORT: {DB_CONFIG['port']}")
    
    if errores:
        print("\n" + "\n".join(errores))
        print("\n💡 Asegúrate de tener estas variables en tu archivo .env:")
        print("   SERVER=tu_servidor")
        print("   PORT=5432")
        print("   USER=tu_usuario")
        print("   PASSWORD=tu_password")
        return False
    
    return True


def test_connection(db_name, db_info):
    """Prueba la conexión a una base de datos específica."""
    print(f"\n🔌 Probando conexión: {db_info['empresa']} (DB: {db_name})")
    print("─" * 50)
    
    try:
        # Conectar
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=db_name,
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            connect_timeout=10
        )
        
        print(f"   ✅ Conexión exitosa")
        
        # Obtener versión PostgreSQL
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   📊 PostgreSQL: {version.split(',')[0]}")
        
        # Ejecutar query de pendientes SII
        print(f"\n   📄 Ejecutando query de documentos pendientes SII...")
        cursor.execute(QUERY_PENDIENTES_SII)
        rows = cursor.fetchall()
        
        if rows:
            print(f"   ✅ {len(rows)} documentos pendientes encontrados\n")
            
            # Mostrar encabezados
            print(f"   {'Fecha':<12} {'Tipo':<8} {'Número':<12} {'Partner':<40} {'Monto':>15}")
            print(f"   {'-'*90}")
            
            # Mostrar primeros 10 registros
            for row in rows[:10]:
                fecha = str(row[0])[:10] if row[0] else ''
                tipo = str(row[1] or '')[:8]
                numero = str(row[2] or '')[:12]
                partner = str(row[3] or '')[:40]
                monto = row[4] or 0
                print(f"   {fecha:<12} {tipo:<8} {numero:<12} {partner:<40} ${monto:>14,.0f}")
            
            if len(rows) > 10:
                print(f"\n   ... y {len(rows) - 10} documentos más")
            
            # Resumen por tipo
            print(f"\n   📊 Resumen por tipo de documento:")
            cursor.execute("""
                SELECT b.doc_code_prefix, COUNT(*), SUM(a.amount)
                FROM mail_message_dte_document a,
                     sii_document_class b
                WHERE a.state = 'draft' 
                  AND a.document_class_id = b.id
                GROUP BY b.doc_code_prefix
                ORDER BY COUNT(*) DESC
            """)
            resumen = cursor.fetchall()
            for tipo, cantidad, total in resumen:
                print(f"      {tipo or 'N/A'}: {cantidad} docs, ${total or 0:,.0f}")
        else:
            print(f"   ℹ️  No hay documentos pendientes")
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'empresa': db_info['empresa'],
            'database': db_name,
            'pendientes': len(rows) if rows else 0,
            'datos': rows
        }
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"   ❌ Error de conexión:")
        
        if "could not connect to server" in error_msg:
            print(f"      No se puede conectar al servidor {DB_CONFIG['host']}:{DB_CONFIG['port']}")
            print(f"      Verifica que el servidor esté accesible")
        elif "password authentication failed" in error_msg:
            print(f"      Credenciales incorrectas")
        elif "database" in error_msg and "does not exist" in error_msg:
            print(f"      La base de datos '{db_name}' no existe")
        else:
            print(f"      {error_msg}")
        
        return {
            'success': False,
            'empresa': db_info['empresa'],
            'database': db_name,
            'error': error_msg
        }
        
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return {
            'success': False,
            'empresa': db_info['empresa'],
            'database': db_name,
            'error': str(e)
        }


def main():
    """Función principal."""
    print("=" * 60)
    print("   TEST DE CONEXIÓN - FACTORIT (ODOO/POSTGRESQL)")
    print("=" * 60)
    
    # Verificar configuración
    if not verificar_config():
        sys.exit(1)
    
    # Probar cada base de datos
    resultados = []
    for db_name, db_info in DATABASES.items():
        resultado = test_connection(db_name, db_info)
        resultados.append(resultado)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("   RESUMEN DE CONEXIONES")
    print("=" * 60)
    
    for r in resultados:
        status = "✅" if r['success'] else "❌"
        if r['success']:
            print(f"   {status} {r['empresa']} ({r['database']}): {r['pendientes']} docs pendientes")
        else:
            print(f"   {status} {r['empresa']} ({r['database']}): Error de conexión")
    
    print("=" * 60)
    
    # Retornar resultados para uso programático
    return resultados


if __name__ == '__main__':
    main()

