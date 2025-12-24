#!/usr/bin/env python3
"""
Reporte de Pendientes FactorIT - JSON
=====================================

Genera un JSON con todos los pendientes:
- Documentos por aceptar en SII
- Asientos por contabilizar
- Movimientos bancarios por conciliar

Uso:
    python -m odoo.pendientes              # Muestra en consola y guarda JSON
    python -m odoo.pendientes --output pendientes.json

Como módulo:
    from odoo.pendientes import obtener_pendientes
    data = obtener_pendientes()
"""

import os
import sys
import json
from datetime import datetime, date
from decimal import Decimal
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


class JSONEncoder(json.JSONEncoder):
    """Encoder personalizado para tipos de datos especiales."""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def obtener_pendientes_empresa(db_name: str) -> dict:
    """Obtiene todos los pendientes de una empresa."""
    
    empresa_nombre = DATABASES.get(db_name, db_name)
    
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=db_name,
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
    )
    cursor = conn.cursor()
    
    resultado = {
        'empresa': empresa_nombre,
        'database': db_name,
        'fecha_consulta': datetime.now().isoformat(),
        'pendientes_sii': {},
        'pendientes_contabilizar': {},
        'pendientes_conciliar': {},
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. DOCUMENTOS POR ACEPTAR EN SII
    # ═══════════════════════════════════════════════════════════════════
    cursor.execute('''
        SELECT 
            a.id,
            a.date,
            b.doc_code_prefix as tipo,
            a.number as folio,
            a.new_partner as proveedor,
            a.amount as monto
        FROM mail_message_dte_document a
        JOIN sii_document_class b ON a.document_class_id = b.id
        WHERE a.state = 'draft'
        ORDER BY a.date DESC
    ''')
    
    docs_sii = []
    total_sii = 0
    for row in cursor.fetchall():
        doc_id, fecha, tipo, folio, proveedor, monto = row
        monto = float(monto or 0)
        total_sii += monto
        
        # Parsear RUT y nombre del proveedor
        rut = ''
        nombre = proveedor or ''
        if proveedor and ' ' in proveedor:
            parts = proveedor.split(' ', 1)
            rut = parts[0]
            nombre = parts[1] if len(parts) > 1 else ''
        
        docs_sii.append({
            'id': doc_id,
            'fecha': fecha,
            'tipo': tipo,
            'folio': folio,
            'proveedor_rut': rut,
            'proveedor_nombre': nombre,
            'monto': monto,
        })
    
    resultado['pendientes_sii'] = {
        'cantidad': len(docs_sii),
        'total': total_sii,
        'documentos': docs_sii,
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # 2. ASIENTOS POR CONTABILIZAR (state=draft)
    # ═══════════════════════════════════════════════════════════════════
    cursor.execute('''
        SELECT 
            am.id,
            am.date,
            aj.name as diario,
            am.name as referencia,
            rp.name as tercero,
            am.ref as descripcion
        FROM account_move am
        JOIN account_journal aj ON am.journal_id = aj.id
        LEFT JOIN res_partner rp ON am.partner_id = rp.id
        WHERE am.state = 'draft'
        ORDER BY am.date DESC
    ''')
    
    asientos_draft = []
    for row in cursor.fetchall():
        asiento_id, fecha, diario, referencia, tercero, descripcion = row
        asientos_draft.append({
            'id': asiento_id,
            'fecha': fecha,
            'diario': diario,
            'referencia': referencia,
            'tercero': tercero,
            'descripcion': descripcion,
        })
    
    # Resumen por diario
    cursor.execute('''
        SELECT aj.name as diario, COUNT(*) as cantidad
        FROM account_move am
        JOIN account_journal aj ON am.journal_id = aj.id
        WHERE am.state = 'draft'
        GROUP BY aj.name
        ORDER BY COUNT(*) DESC
    ''')
    resumen_diarios = {row[0]: row[1] for row in cursor.fetchall()}
    
    resultado['pendientes_contabilizar'] = {
        'cantidad': len(asientos_draft),
        'por_diario': resumen_diarios,
        'asientos': asientos_draft,
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. MOVIMIENTOS BANCARIOS POR CONCILIAR
    # ═══════════════════════════════════════════════════════════════════
    
    # Extractos abiertos
    cursor.execute('''
        SELECT 
            abs.id,
            abs.name,
            abs.date,
            aj.name as banco,
            abs.balance_start,
            abs.balance_end_real
        FROM account_bank_statement abs
        JOIN account_journal aj ON abs.journal_id = aj.id
        WHERE abs.state = 'open'
        ORDER BY abs.date DESC
    ''')
    
    extractos = []
    for row in cursor.fetchall():
        ext_id, nombre, fecha, banco, saldo_ini, saldo_fin = row
        extractos.append({
            'id': ext_id,
            'nombre': nombre,
            'fecha': fecha,
            'banco': banco,
            'saldo_inicial': float(saldo_ini or 0),
            'saldo_final': float(saldo_fin or 0),
        })
    
    # Movimientos en extractos abiertos
    cursor.execute('''
        SELECT 
            abl.id,
            abl.date,
            aj.name as banco,
            abl.name as descripcion,
            rp.name as tercero,
            abl.amount,
            abl.ref as referencia
        FROM account_bank_statement_line abl
        JOIN account_bank_statement abs ON abl.statement_id = abs.id
        JOIN account_journal aj ON abs.journal_id = aj.id
        LEFT JOIN res_partner rp ON abl.partner_id = rp.id
        WHERE abs.state = 'open'
        ORDER BY abl.date DESC
    ''')
    
    movimientos = []
    total_abonos = 0
    total_cargos = 0
    for row in cursor.fetchall():
        mov_id, fecha, banco, descripcion, tercero, monto, referencia = row
        monto = float(monto or 0)
        if monto > 0:
            total_abonos += monto
        else:
            total_cargos += monto
        
        movimientos.append({
            'id': mov_id,
            'fecha': fecha,
            'banco': banco,
            'descripcion': descripcion,
            'tercero': tercero,
            'monto': monto,
            'referencia': referencia,
        })
    
    # Resumen por banco
    cursor.execute('''
        SELECT 
            aj.name as banco,
            COUNT(*) as cantidad,
            SUM(CASE WHEN abl.amount > 0 THEN abl.amount ELSE 0 END) as abonos,
            SUM(CASE WHEN abl.amount < 0 THEN abl.amount ELSE 0 END) as cargos
        FROM account_bank_statement_line abl
        JOIN account_bank_statement abs ON abl.statement_id = abs.id
        JOIN account_journal aj ON abs.journal_id = aj.id
        WHERE abs.state = 'open'
        GROUP BY aj.name
        ORDER BY COUNT(*) DESC
    ''')
    
    resumen_bancos = []
    for row in cursor.fetchall():
        banco, cantidad, abonos, cargos = row
        resumen_bancos.append({
            'banco': banco,
            'cantidad': cantidad,
            'abonos': float(abonos or 0),
            'cargos': float(cargos or 0),
            'neto': float((abonos or 0) + (cargos or 0)),
        })
    
    resultado['pendientes_conciliar'] = {
        'cantidad': len(movimientos),
        'total_abonos': total_abonos,
        'total_cargos': total_cargos,
        'total_neto': total_abonos + total_cargos,
        'extractos_abiertos': extractos,
        'por_banco': resumen_bancos,
        'movimientos': movimientos,
    }
    
    cursor.close()
    conn.close()
    
    return resultado


def obtener_pendientes() -> dict:
    """Obtiene pendientes de todas las empresas configuradas."""
    
    reporte = {
        'generado': datetime.now().isoformat(),
        'version': '1.0',
        'empresas': [],
        'resumen': {
            'total_sii': 0,
            'total_sii_monto': 0,
            'total_contabilizar': 0,
            'total_conciliar': 0,
        }
    }
    
    for db_name in DATABASES.keys():
        try:
            pendientes = obtener_pendientes_empresa(db_name)
            reporte['empresas'].append(pendientes)
            
            # Acumular totales
            reporte['resumen']['total_sii'] += pendientes['pendientes_sii']['cantidad']
            reporte['resumen']['total_sii_monto'] += pendientes['pendientes_sii']['total']
            reporte['resumen']['total_contabilizar'] += pendientes['pendientes_contabilizar']['cantidad']
            reporte['resumen']['total_conciliar'] += pendientes['pendientes_conciliar']['cantidad']
            
        except Exception as e:
            reporte['empresas'].append({
                'empresa': DATABASES[db_name],
                'database': db_name,
                'error': str(e),
            })
    
    return reporte


def main():
    """Función principal."""
    
    # Parsear argumentos
    output_file = None
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    print("=" * 70)
    print("   REPORTE DE PENDIENTES FACTORIT")
    print("=" * 70)
    print()
    
    # Obtener datos
    print("📊 Consultando pendientes...")
    reporte = obtener_pendientes()
    
    # Mostrar resumen
    print()
    print("=" * 70)
    print("   RESUMEN")
    print("=" * 70)
    
    for emp in reporte['empresas']:
        if 'error' in emp:
            print(f"\n❌ {emp['empresa']}: {emp['error']}")
            continue
        
        print(f"\n🏢 {emp['empresa']} ({emp['database']})")
        print(f"   📄 SII pendientes: {emp['pendientes_sii']['cantidad']} docs (${emp['pendientes_sii']['total']:,.0f})")
        print(f"   📝 Por contabilizar: {emp['pendientes_contabilizar']['cantidad']} asientos")
        print(f"   🏦 Por conciliar: {emp['pendientes_conciliar']['cantidad']} movimientos")
    
    print()
    print("-" * 70)
    print(f"📊 TOTALES:")
    print(f"   Documentos SII: {reporte['resumen']['total_sii']} (${reporte['resumen']['total_sii_monto']:,.0f})")
    print(f"   Asientos borrador: {reporte['resumen']['total_contabilizar']}")
    print(f"   Movimientos banco: {reporte['resumen']['total_conciliar']}")
    
    # Guardar JSON
    if output_file is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'pendientes_factorit_{timestamp}.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, cls=JSONEncoder, ensure_ascii=False, indent=2)
    
    print()
    print(f"✅ JSON guardado: {output_file}")
    print("=" * 70)
    
    return reporte


if __name__ == '__main__':
    main()





