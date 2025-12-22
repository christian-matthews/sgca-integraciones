#!/usr/bin/env python3
"""
Movimientos Bancarios Pendientes de Conciliar - Odoo/FactorIT
==============================================================

Extrae movimientos bancarios que no han sido conciliados.

CRITERIO CORRECTO:
- Extracto con state='open' = Pendiente de conciliar
- Extracto con state='confirm' = Ya conciliado

(El campo move_name NO indica conciliación en esta versión de Odoo)

Uso:
    python -m odoo.bancos_pendientes
"""

import os
from datetime import datetime
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

DATABASES = {
    'FactorIT': 'FactorIT SpA',
    'FactorIT2': 'FactorIT Ltda',
}


# Query para movimientos sin conciliar (extractos en estado 'open')
QUERY_PENDIENTES = """
SELECT 
    bsl.date as fecha,
    aj.name as banco,
    bsl.name as descripcion,
    bsl.ref as referencia,
    bsl.amount as monto,
    bsl.partner_name as tercero,
    bs.name as periodo_extracto
FROM account_bank_statement_line bsl
JOIN account_bank_statement bs ON bsl.statement_id = bs.id
LEFT JOIN account_journal aj ON bsl.journal_id = aj.id
WHERE bs.state = 'open'
ORDER BY aj.name, bsl.date DESC
"""

# Query para resumen por banco (solo extractos abiertos)
QUERY_RESUMEN_BANCO = """
SELECT 
    aj.name as banco,
    COUNT(*) as cantidad,
    SUM(CASE WHEN bsl.amount > 0 THEN bsl.amount ELSE 0 END) as total_abonos,
    SUM(CASE WHEN bsl.amount < 0 THEN bsl.amount ELSE 0 END) as total_cargos,
    SUM(bsl.amount) as neto
FROM account_bank_statement_line bsl
JOIN account_bank_statement bs ON bsl.statement_id = bs.id
LEFT JOIN account_journal aj ON bsl.journal_id = aj.id
WHERE bs.state = 'open'
GROUP BY aj.name
ORDER BY COUNT(*) DESC
"""

# Query para resumen por extracto
QUERY_RESUMEN_EXTRACTOS = """
SELECT 
    bs.name as periodo,
    aj.name as banco,
    bs.state as estado,
    COUNT(bsl.id) as lineas,
    SUM(bsl.amount) as total
FROM account_bank_statement bs
LEFT JOIN account_journal aj ON bs.journal_id = aj.id
LEFT JOIN account_bank_statement_line bsl ON bsl.statement_id = bs.id
WHERE bs.state = 'open'
GROUP BY bs.id, bs.name, aj.name, bs.state
ORDER BY bs.date DESC, aj.name
"""


def obtener_pendientes(db_name, empresa_nombre):
    """Obtiene movimientos bancarios pendientes de conciliar."""
    
    print(f"\n{'='*70}")
    print(f"   {empresa_nombre} ({db_name})")
    print(f"{'='*70}")
    
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=db_name,
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
        )
        cursor = conn.cursor()
        
        # Primero mostrar estado general de extractos
        cursor.execute("""
            SELECT state, COUNT(*), 
                   (SELECT COUNT(*) FROM account_bank_statement_line bsl 
                    WHERE bsl.statement_id IN (SELECT id FROM account_bank_statement WHERE state = bs.state))
            FROM account_bank_statement bs
            GROUP BY state
        """)
        print("\n📋 ESTADO DE EXTRACTOS BANCARIOS:")
        print("-" * 50)
        for state, ext_count, mov_count in cursor.fetchall():
            estado = "✅ Confirmado" if state == 'confirm' else "📂 Abierto (pendiente)"
            print(f"   {estado}: {ext_count} extractos, {mov_count} movimientos")
        
        # Resumen de extractos abiertos
        print("\n📂 EXTRACTOS ABIERTOS (Pendientes de Conciliar):")
        print("-" * 70)
        
        cursor.execute(QUERY_RESUMEN_EXTRACTOS)
        extractos = cursor.fetchall()
        
        if extractos:
            print(f"{'Período':<12} {'Banco':<30} {'Líneas':>8} {'Total':>18}")
            print("-" * 70)
            for periodo, banco, estado, lineas, total in extractos:
                if lineas and lineas > 0:
                    total = total or 0
                    print(f"{periodo:<12} {(banco or '')[:30]:<30} {lineas:>8} ${total:>17,.0f}")
        else:
            print("   ✅ No hay extractos pendientes de conciliar")
        
        # Resumen por banco
        print("\n📊 RESUMEN POR BANCO (solo pendientes):")
        print("-" * 70)
        print(f"{'Banco':<30} {'Cant':>6} {'Abonos':>15} {'Cargos':>15} {'Neto':>15}")
        print("-" * 70)
        
        cursor.execute(QUERY_RESUMEN_BANCO)
        resumen = cursor.fetchall()
        
        total_movs = 0
        total_abonos = 0
        total_cargos = 0
        total_neto = 0
        
        for banco, cant, abonos, cargos, neto in resumen:
            banco_str = (banco or 'Sin banco')[:30]
            abonos = abonos or 0
            cargos = cargos or 0
            neto = neto or 0
            print(f"{banco_str:<30} {cant:>6} ${abonos:>14,.0f} ${cargos:>14,.0f} ${neto:>14,.0f}")
            total_movs += cant
            total_abonos += abonos
            total_cargos += cargos
            total_neto += neto
        
        if total_movs > 0:
            print("-" * 70)
            print(f"{'TOTAL':<30} {total_movs:>6} ${total_abonos:>14,.0f} ${total_cargos:>14,.0f} ${total_neto:>14,.0f}")
        else:
            print("   ✅ No hay movimientos pendientes")
        
        # Detalle de movimientos recientes
        print(f"\n📋 MOVIMIENTOS PENDIENTES (últimos 20):")
        print("-" * 100)
        print(f"{'Fecha':<12} {'Banco':<20} {'Monto':>15} {'Descripción':<50}")
        print("-" * 100)
        
        cursor.execute(QUERY_PENDIENTES + " LIMIT 20")
        movimientos = cursor.fetchall()
        
        for row in movimientos:
            fecha, banco, desc, ref, monto, tercero = row[0], row[1], row[2], row[3], row[4], row[5]
            fecha_str = str(fecha) if fecha else ''
            banco_str = (banco or '')[:20]
            desc_str = (desc or ref or tercero or '')[:50]
            print(f"{fecha_str:<12} {banco_str:<20} ${monto:>14,.0f} {desc_str}")
        
        if total_movs > 20:
            print(f"\n   ... y {total_movs - 20} movimientos más")
        
        # Obtener todos los movimientos para retornar
        cursor.execute(QUERY_PENDIENTES)
        todos_movimientos = cursor.fetchall()
        
        # Obtener extractos para el resultado
        cursor.execute(QUERY_RESUMEN_EXTRACTOS)
        extractos_result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'empresa': empresa_nombre,
            'database': db_name,
            'total_movimientos': total_movs,
            'total_abonos': total_abonos,
            'total_cargos': total_cargos,
            'neto': total_neto,
            'resumen_bancos': resumen,
            'extractos_abiertos': extractos_result,
            'movimientos': todos_movimientos
        }
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {
            'success': False,
            'empresa': empresa_nombre,
            'database': db_name,
            'error': str(e)
        }


def main():
    print("=" * 70)
    print("   MOVIMIENTOS BANCARIOS PENDIENTES DE CONCILIAR")
    print(f"   Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 70)
    
    resultados = []
    
    for db_name, empresa_nombre in DATABASES.items():
        resultado = obtener_pendientes(db_name, empresa_nombre)
        resultados.append(resultado)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("   RESUMEN GENERAL")
    print("=" * 70)
    
    for r in resultados:
        if r['success']:
            print(f"\n   {r['empresa']}:")
            print(f"      Movimientos sin conciliar: {r['total_movimientos']:,}")
            print(f"      Total abonos: ${r['total_abonos']:,.0f}")
            print(f"      Total cargos: ${r['total_cargos']:,.0f}")
            print(f"      Neto: ${r['neto']:,.0f}")
        else:
            print(f"\n   ❌ {r['empresa']}: Error - {r.get('error', 'Desconocido')}")
    
    print("\n" + "=" * 70)
    
    return resultados


if __name__ == '__main__':
    main()

