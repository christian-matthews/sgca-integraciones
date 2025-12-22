#!/usr/bin/env python3
"""
Explorador de Base de Datos Odoo (FactorIT)
============================================

Explora tablas y datos disponibles de forma segura (solo SELECT).
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_env_clean(key, default=None):
    val = os.getenv(key)
    return val.strip() if val else default

DB_CONFIG = {
    'host': get_env_clean('SERVER'),
    'port': get_env_clean('PORT', '5432'),
    'user': get_env_clean('DB_USER'),
    'password': get_env_clean('PASSWORD'),
}


def explorar_db(db_name):
    """Explora una base de datos y muestra tablas/datos útiles."""
    
    print(f"\n{'='*70}")
    print(f"   EXPLORANDO: {db_name}")
    print(f"{'='*70}")
    
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=db_name,
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
    )
    cursor = conn.cursor()
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. TABLAS PRINCIPALES
    # ═══════════════════════════════════════════════════════════════════
    print("\n📋 TABLAS PRINCIPALES (con más de 100 registros):")
    print("-" * 70)
    
    cursor.execute("""
        SELECT relname as tabla, n_live_tup as rows
        FROM pg_stat_user_tables
        WHERE n_live_tup > 100
        ORDER BY n_live_tup DESC
        LIMIT 30
    """)
    
    for table, rows in cursor.fetchall():
        print(f"   {table:<45} {rows:>10,} rows")
    
    # ═══════════════════════════════════════════════════════════════════
    # 2. TABLAS DE CONTABILIDAD
    # ═══════════════════════════════════════════════════════════════════
    print("\n\n💰 TABLAS DE CONTABILIDAD:")
    print("-" * 70)
    
    cursor.execute("""
        SELECT relname, n_live_tup
        FROM pg_stat_user_tables
        WHERE relname LIKE 'account_%'
        ORDER BY n_live_tup DESC
    """)
    
    for table, rows in cursor.fetchall():
        print(f"   {table:<45} {rows:>10,} rows")
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. TABLAS SII/DTE
    # ═══════════════════════════════════════════════════════════════════
    print("\n\n📄 TABLAS SII/DTE:")
    print("-" * 70)
    
    cursor.execute("""
        SELECT relname, n_live_tup
        FROM pg_stat_user_tables
        WHERE relname LIKE '%sii%' OR relname LIKE '%dte%'
        ORDER BY n_live_tup DESC
    """)
    
    for table, rows in cursor.fetchall():
        print(f"   {table:<45} {rows:>10,} rows")
    
    # ═══════════════════════════════════════════════════════════════════
    # 4. PARTNERS (CLIENTES/PROVEEDORES)
    # ═══════════════════════════════════════════════════════════════════
    print("\n\n👥 PARTNERS (Clientes/Proveedores):")
    print("-" * 70)
    
    cursor.execute("""
        SELECT COUNT(*) FROM res_partner
    """)
    total_partners = cursor.fetchone()[0]
    print(f"   Total partners: {total_partners:,}")
    
    cursor.execute("""
        SELECT 
            CASE WHEN customer THEN 'Cliente' ELSE '' END || 
            CASE WHEN supplier THEN ' Proveedor' ELSE '' END as tipo,
            COUNT(*)
        FROM res_partner
        WHERE customer OR supplier
        GROUP BY customer, supplier
    """)
    for tipo, count in cursor.fetchall():
        print(f"   {tipo.strip()}: {count:,}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 5. PRODUCTOS
    # ═══════════════════════════════════════════════════════════════════
    print("\n\n📦 PRODUCTOS:")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM product_product")
    total_prod = cursor.fetchone()[0]
    print(f"   Total productos: {total_prod:,}")
    
    cursor.execute("SELECT COUNT(*) FROM product_template")
    total_templ = cursor.fetchone()[0]
    print(f"   Templates: {total_templ:,}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 6. FACTURAS/INVOICES
    # ═══════════════════════════════════════════════════════════════════
    print("\n\n🧾 FACTURAS (account_invoice):")
    print("-" * 70)
    
    try:
        cursor.execute("""
            SELECT type, state, COUNT(*), SUM(amount_total)
            FROM account_invoice
            GROUP BY type, state
            ORDER BY type, state
        """)
        
        for tipo, estado, count, total in cursor.fetchall():
            total_fmt = f"${total:,.0f}" if total else "$0"
            print(f"   {tipo:<15} {estado:<12} {count:>6} docs  {total_fmt:>18}")
    except:
        print("   (Tabla no disponible o estructura diferente)")
    
    # ═══════════════════════════════════════════════════════════════════
    # 7. MOVIMIENTOS CONTABLES
    # ═══════════════════════════════════════════════════════════════════
    print("\n\n📊 MOVIMIENTOS CONTABLES (account_move):")
    print("-" * 70)
    
    try:
        cursor.execute("""
            SELECT state, COUNT(*), 
                   SUM(amount) as total
            FROM account_move
            GROUP BY state
        """)
        
        for estado, count, total in cursor.fetchall():
            total_fmt = f"${total:,.0f}" if total else "$0"
            print(f"   {estado:<15} {count:>8} movimientos  {total_fmt:>18}")
    except:
        print("   (Tabla no disponible o estructura diferente)")
    
    # ═══════════════════════════════════════════════════════════════════
    # 8. CUENTAS CONTABLES
    # ═══════════════════════════════════════════════════════════════════
    print("\n\n📒 PLAN DE CUENTAS (account_account):")
    print("-" * 70)
    
    try:
        cursor.execute("""
            SELECT user_type_id, COUNT(*)
            FROM account_account
            GROUP BY user_type_id
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """)
        
        total_cuentas = sum(row[1] for row in cursor.fetchall())
        cursor.execute("SELECT COUNT(*) FROM account_account")
        total_cuentas = cursor.fetchone()[0]
        print(f"   Total cuentas contables: {total_cuentas:,}")
        
        cursor.execute("""
            SELECT code, name 
            FROM account_account 
            ORDER BY code 
            LIMIT 15
        """)
        print("\n   Primeras cuentas:")
        for code, name in cursor.fetchall():
            print(f"   {code:<10} {name[:50]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # ═══════════════════════════════════════════════════════════════════
    # 9. LIBROS DE COMPRA/VENTA
    # ═══════════════════════════════════════════════════════════════════
    print("\n\n📚 LIBROS CONTABLES:")
    print("-" * 70)
    
    try:
        cursor.execute("""
            SELECT name, code, type, COUNT(am.id) as movimientos
            FROM account_journal aj
            LEFT JOIN account_move am ON am.journal_id = aj.id
            GROUP BY aj.id, aj.name, aj.code, aj.type
            ORDER BY movimientos DESC
        """)
        
        for name, code, tipo, movs in cursor.fetchall():
            print(f"   [{code}] {name[:30]:<30} ({tipo:<10}) {movs:>6} movs")
    except:
        print("   (No disponible)")
    
    # ═══════════════════════════════════════════════════════════════════
    # 10. DATOS ÚTILES ADICIONALES
    # ═══════════════════════════════════════════════════════════════════
    print("\n\n🔍 OTROS DATOS ÚTILES:")
    print("-" * 70)
    
    queries_utiles = [
        ("Usuarios del sistema", "SELECT COUNT(*) FROM res_users"),
        ("Compañías", "SELECT COUNT(*) FROM res_company"),
        ("Monedas activas", "SELECT COUNT(*) FROM res_currency WHERE active"),
        ("Bancos", "SELECT COUNT(*) FROM res_bank"),
        ("Sucursales", "SELECT COUNT(*) FROM sii_sucursal" if db_name else None),
    ]
    
    for desc, query in queries_utiles:
        if query:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"   {desc}: {count:,}")
            except:
                pass
    
    # ═══════════════════════════════════════════════════════════════════
    # 11. DOCUMENTOS PENDIENTES DETALLE
    # ═══════════════════════════════════════════════════════════════════
    print("\n\n📄 DOCUMENTOS PENDIENTES SII (Detalle estados):")
    print("-" * 70)
    
    try:
        cursor.execute("""
            SELECT state, COUNT(*), SUM(amount)
            FROM mail_message_dte_document
            GROUP BY state
            ORDER BY COUNT(*) DESC
        """)
        
        for state, count, total in cursor.fetchall():
            total_fmt = f"${total:,.0f}" if total else "$0"
            print(f"   {state:<20} {count:>6} docs  {total_fmt:>18}")
    except:
        print("   (No disponible)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)


def main():
    print("=" * 70)
    print("   EXPLORADOR DE BASE DE DATOS ODOO (FACTORIT)")
    print("   Solo lectura - Sin modificaciones")
    print("=" * 70)
    
    for db in ['FactorIT', 'FactorIT2']:
        try:
            explorar_db(db)
        except Exception as e:
            print(f"\n❌ Error en {db}: {e}")


if __name__ == '__main__':
    main()

