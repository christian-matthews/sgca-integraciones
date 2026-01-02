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
from datetime import datetime, date, timedelta
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

# Fecha mínima para considerar pendientes de conciliación
# Solo considera movimientos desde esta fecha en adelante
CONCILIACION_FECHA_MINIMA = '2025-01-01'

# ═══════════════════════════════════════════════════════════════════════════
# POLÍTICA SII - ACEPTACIÓN TÁCITA
# ═══════════════════════════════════════════════════════════════════════════
# Según normativa SII Chile, los DTEs se aceptan tácitamente después de 8 días
# naturales si no son explícitamente aceptados o rechazados.
#
# - ACCIONABLES: Documentos con < 8 días → requieren revisión y acción
# - TÁCITOS SIN REVISAR: Documentos con >= 8 días en estado 'draft' → 
#   fueron aceptados automáticamente por SII sin que el usuario los revisara
#   (esto representa un riesgo de control)
# ═══════════════════════════════════════════════════════════════════════════
SII_DIAS_ACEPTACION_TACITA = 8


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
    # Separamos en dos grupos:
    # - ACCIONABLES: < 8 días, requieren revisión y decisión
    # - TÁCITOS SIN REVISAR: >= 8 días, SII los aceptó automáticamente
    # ═══════════════════════════════════════════════════════════════════
    
    fecha_limite_tacito = date.today() - timedelta(days=SII_DIAS_ACEPTACION_TACITA)
    
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
    
    docs_accionables = []
    docs_tacitos = []
    total_accionables = 0
    total_tacitos = 0
    
    for row in cursor.fetchall():
        doc_id, fecha, tipo, folio, proveedor, monto = row
        monto = float(monto or 0)
        
        # Parsear RUT y nombre del proveedor
        rut = ''
        nombre = proveedor or ''
        if proveedor and ' ' in proveedor:
            parts = proveedor.split(' ', 1)
            rut = parts[0]
            nombre = parts[1] if len(parts) > 1 else ''
        
        doc = {
            'id': doc_id,
            'fecha': fecha,
            'tipo': tipo,
            'folio': folio,
            'proveedor_rut': rut,
            'proveedor_nombre': nombre,
            'monto': monto,
        }
        
        # Clasificar según fecha
        if fecha and fecha >= fecha_limite_tacito:
            # Documento reciente (< 8 días) → requiere acción
            docs_accionables.append(doc)
            total_accionables += monto
        else:
            # Documento antiguo (>= 8 días) → aceptado tácitamente sin revisar
            doc['dias_sin_revisar'] = (date.today() - fecha).days if fecha else None
            docs_tacitos.append(doc)
            total_tacitos += monto
    
    resultado['pendientes_sii'] = {
        # Resumen general (para compatibilidad)
        'cantidad': len(docs_accionables) + len(docs_tacitos),
        'total': total_accionables + total_tacitos,
        
        # ACCIONABLES: Los que realmente requieren trabajo
        'accionables': {
            'cantidad': len(docs_accionables),
            'total': total_accionables,
            'documentos': docs_accionables,
            'descripcion': f'Documentos con menos de {SII_DIAS_ACEPTACION_TACITA} días, requieren revisión',
        },
        
        # TÁCITOS: Aceptados automáticamente sin revisar (riesgo de control)
        'tacitos_sin_revisar': {
            'cantidad': len(docs_tacitos),
            'total': total_tacitos,
            'documentos': docs_tacitos,
            'descripcion': f'Documentos con {SII_DIAS_ACEPTACION_TACITA}+ días, aceptados tácitamente por SII',
        },
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # 2. FACTURAS POR CONTABILIZAR
    # ═══════════════════════════════════════════════════════════════════
    # CRITERIO CORRECTO: Documentos SII aceptados que NO tienen asiento
    # contable asociado. Se verifica:
    # - invoice_id IS NULL (sin vínculo directo)
    # - Y NO existe un asiento posted con ese folio en la referencia
    # ═══════════════════════════════════════════════════════════════════
    
    cursor.execute(f'''
        SELECT 
            a.id,
            a.date,
            b.doc_code_prefix as tipo,
            a.number as folio,
            a.new_partner as proveedor,
            a.amount
        FROM mail_message_dte_document a
        JOIN sii_document_class b ON a.document_class_id = b.id
        WHERE a.state = 'accepted'
          AND a.invoice_id IS NULL
          AND a.date >= '{CONCILIACION_FECHA_MINIMA}'
          AND NOT EXISTS (
              SELECT 1 FROM account_move am
              WHERE am.state = 'posted'
                AND am.ref LIKE '%' || a.number::text || '%'
          )
        ORDER BY a.date DESC
    ''')
    
    facturas_sin_contabilizar = []
    for row in cursor.fetchall():
        doc_id, fecha, tipo, folio, proveedor, monto = row
        facturas_sin_contabilizar.append({
            'id': doc_id,
            'fecha': fecha,
            'tipo': tipo,
            'folio': folio,
            'proveedor': proveedor,
            'monto': float(monto) if monto else 0,
        })
    
    # Resumen por tipo de documento
    resumen_tipos = {}
    for f in facturas_sin_contabilizar:
        tipo = f['tipo'] or 'Otro'
        resumen_tipos[tipo] = resumen_tipos.get(tipo, 0) + 1
    
    resultado['pendientes_contabilizar'] = {
        'cantidad': len(facturas_sin_contabilizar),
        'por_tipo': resumen_tipos,
        'total_monto': sum(f['monto'] for f in facturas_sin_contabilizar),
        'facturas': facturas_sin_contabilizar,
        # Alias para compatibilidad
        'asientos': facturas_sin_contabilizar,
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. MOVIMIENTOS BANCARIOS POR CONCILIAR
    # ═══════════════════════════════════════════════════════════════════
    # CRITERIO CORRECTO: Un movimiento está pendiente de conciliar si
    # NO tiene un account_move_line asociado (statement_line_id).
    # Esto es lo que Odoo usa en su interfaz de conciliación.
    # ═══════════════════════════════════════════════════════════════════
    
    # Extractos abiertos (solo desde CONCILIACION_FECHA_MINIMA)
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
        AND abs.date >= %s
        ORDER BY abs.date DESC
    ''', (CONCILIACION_FECHA_MINIMA,))
    
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
    
    # Movimientos SIN conciliar (sin account_move_line.statement_line_id)
    # Este es el criterio correcto que usa Odoo internamente
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
        WHERE abl.date >= %s
        AND NOT EXISTS (
            SELECT 1 FROM account_move_line aml 
            WHERE aml.statement_line_id = abl.id
        )
        ORDER BY abl.date DESC
    ''', (CONCILIACION_FECHA_MINIMA,))
    
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
    
    # Resumen por banco (solo pendientes reales)
    cursor.execute('''
        SELECT 
            aj.name as banco,
            COUNT(*) as cantidad,
            SUM(CASE WHEN abl.amount > 0 THEN abl.amount ELSE 0 END) as abonos,
            SUM(CASE WHEN abl.amount < 0 THEN abl.amount ELSE 0 END) as cargos
        FROM account_bank_statement_line abl
        JOIN account_bank_statement abs ON abl.statement_id = abs.id
        JOIN account_journal aj ON abs.journal_id = aj.id
        WHERE abl.date >= %s
        AND NOT EXISTS (
            SELECT 1 FROM account_move_line aml 
            WHERE aml.statement_line_id = abl.id
        )
        GROUP BY aj.name
        ORDER BY COUNT(*) DESC
    ''', (CONCILIACION_FECHA_MINIMA,))
    
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
        
        sii = emp['pendientes_sii']
        accionables = sii.get('accionables', {})
        tacitos = sii.get('tacitos_sin_revisar', {})
        
        print(f"\n🏢 {emp['empresa']} ({emp['database']})")
        print(f"   📄 SII pendientes:")
        print(f"      ⚡ Accionables (<8d): {accionables.get('cantidad', 0)} docs (${accionables.get('total', 0):,.0f})")
        print(f"      ⚠️  Tácitos (≥8d):    {tacitos.get('cantidad', 0)} docs (${tacitos.get('total', 0):,.0f})")
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





