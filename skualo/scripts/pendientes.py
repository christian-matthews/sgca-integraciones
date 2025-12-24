#!/usr/bin/env python3
"""
Reporte de Pendientes Skualo - JSON
===================================

Genera un JSON con todos los pendientes:
- Documentos por aceptar en SII
- Documentos por contabilizar
- Movimientos bancarios por conciliar

Uso:
    python -m skualo.scripts.pendientes              # Todas las empresas
    python -m skualo.scripts.pendientes FIDI         # Una empresa específica
    python -m skualo.scripts.pendientes --output pendientes.json

Como módulo:
    from skualo.scripts.pendientes import obtener_pendientes
    data = obtener_pendientes()
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# Configuración
TOKEN = os.getenv('SKUALO_API_TOKEN')
BASE_URL = 'https://api.skualo.cl'
DIAS_ACEPTACION_TACITA = 8

# Cargar tenants
SCRIPT_DIR = Path(__file__).parent
TENANTS_FILE = SCRIPT_DIR.parent / 'config' / 'tenants.json'
with open(TENANTS_FILE, 'r') as f:
    TENANTS = json.load(f)

# Mapeo de tipos DTE
TIPO_DTE_A_INTERNO = {
    33: 'FACE',   # Factura Electrónica
    34: 'FXCE',   # Factura No Afecta o Exenta Electrónica
    61: 'NCCE',   # Nota de Crédito Electrónica
    56: 'NDCE',   # Nota de Débito Electrónica
    52: 'GDES',   # Guía de Despacho Electrónica
    110: 'FEXP',  # Factura de Exportación Electrónica
}


class JSONEncoder(json.JSONEncoder):
    """Encoder para tipos especiales."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def get_headers():
    return {
        'Authorization': f'Bearer {TOKEN}',
        'accept': 'application/json'
    }


def api_get(rut: str, endpoint: str, params: dict = None):
    """Realiza llamada GET a la API."""
    url = f'{BASE_URL}/{rut}{endpoint}'
    try:
        r = requests.get(url, headers=get_headers(), params=params, timeout=30)
        if r.ok:
            return r.json()
    except Exception as e:
        print(f'   Error API: {e}')
    return None


def api_get_all(rut: str, endpoint: str, params: dict = None) -> list:
    """Obtiene todos los registros paginados."""
    all_items = []
    page = 1
    base_params = params or {}
    
    while True:
        paged_params = {**base_params, 'PageSize': 100, 'Page': page}
        data = api_get(rut, endpoint, paged_params)
        if not data:
            break
        items = data.get('items', data) if isinstance(data, dict) else data
        if isinstance(items, list):
            all_items.extend(items)
        if not data.get('next'):
            break
        page += 1
    
    return all_items


def detectar_cuentas_bancarias(balance: list) -> list:
    """Detecta cuentas bancarias del balance."""
    cuentas_banco = []
    palabras_banco = [
        'banco', 'santander', 'chile', 'estado', 'bci', 'scotiabank', 
        'itau', 'itaú', 'security', 'bice', 'falabella', 'ripley',
        'consorcio', 'internacional', 'corpbanca', 'tapp', 'tenpo',
        'mercado pago', 'cuenta corriente', 'cta cte', 'cta. cte'
    ]
    
    for cuenta in balance:
        codigo = cuenta.get('idCuenta', '')
        nombre = cuenta.get('cuenta', '').lower()
        
        if codigo.startswith('1102'):
            cuentas_banco.append(cuenta)
        elif any(palabra in nombre for palabra in palabras_banco):
            if codigo.startswith('1'):
                cuentas_banco.append(cuenta)
    
    return cuentas_banco


def obtener_pendientes_empresa(rut: str) -> dict:
    """Obtiene todos los pendientes de una empresa Skualo."""
    
    # Buscar nombre de empresa
    nombre_empresa = rut
    for key, data in TENANTS.items():
        if data['rut'] == rut:
            nombre_empresa = data.get('nombre', key)
            break
    
    resultado = {
        'empresa': nombre_empresa,
        'rut': rut,
        'fecha_consulta': datetime.now().isoformat(),
        'pendientes_sii': {},
        'pendientes_contabilizar': {},
        'pendientes_conciliar': {},
    }
    
    periodo = datetime.now().strftime('%Y%m')
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. DOCUMENTOS RECIBIDOS SII
    # ═══════════════════════════════════════════════════════════════════
    dtes = api_get_all(rut, '/sii/dte/recibidos')
    
    hoy = datetime.now()
    pendientes_aceptar = []
    aceptados = []
    
    for dte in dtes:
        fecha_respuesta = dte.get('fechaRespuesta')
        
        # Calcular días desde recepción
        dias = 999
        fecha_recep_str = dte.get('creadoEl', '')
        if fecha_recep_str:
            try:
                fecha_recep = datetime.fromisoformat(fecha_recep_str.split('.')[0])
                dias = (hoy - fecha_recep).days
            except:
                pass
        
        dte_info = {
            'id': dte.get('id'),
            'fecha': dte.get('fechaEmision'),
            'tipo': dte.get('tipoDocumento'),
            'tipo_id': dte.get('idTipoDocumento'),
            'folio': dte.get('folio'),
            'emisor_rut': dte.get('rutEmisor'),
            'emisor_nombre': dte.get('emisor'),
            'monto': dte.get('montoTotal', 0),
            'dias_desde_recepcion': dias,
            'fecha_respuesta': fecha_respuesta,
        }
        
        if not fecha_respuesta and dias <= DIAS_ACEPTACION_TACITA:
            pendientes_aceptar.append(dte_info)
        else:
            aceptados.append(dte_info)
    
    total_sii = sum(d['monto'] for d in pendientes_aceptar)
    
    resultado['pendientes_sii'] = {
        'cantidad': len(pendientes_aceptar),
        'total': total_sii,
        'documentos': pendientes_aceptar,
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # 2. DOCUMENTOS POR CONTABILIZAR
    # ═══════════════════════════════════════════════════════════════════
    pendientes_contabilizar = []
    ya_contabilizados = []
    
    for dte in aceptados:
        tipo_dte = dte.get('tipo_id')
        folio = dte.get('folio')
        tipo_interno = TIPO_DTE_A_INTERNO.get(tipo_dte, 'FACE')
        
        # Verificar si existe en documentos
        doc = api_get(rut, f'/documentos/{tipo_interno}/{folio}')
        
        if doc:
            ya_contabilizados.append({**dte, 'tipo_interno': tipo_interno})
        else:
            pendientes_contabilizar.append({**dte, 'tipo_interno': tipo_interno})
    
    total_contabilizar = sum(d['monto'] for d in pendientes_contabilizar)
    
    resultado['pendientes_contabilizar'] = {
        'cantidad': len(pendientes_contabilizar),
        'total': total_contabilizar,
        'ya_contabilizados': len(ya_contabilizados),
        'documentos': pendientes_contabilizar,
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. MOVIMIENTOS BANCARIOS SIN CONCILIAR
    # ═══════════════════════════════════════════════════════════════════
    balance = api_get(rut, f'/contabilidad/reportes/balancetributario/{periodo}')
    
    if balance:
        cuentas_banco = detectar_cuentas_bancarias(balance)
        
        movimientos_pendientes = []
        total_abonos = 0
        total_cargos = 0
        resumen_bancos = []
        
        for cuenta in cuentas_banco:
            codigo = cuenta['idCuenta']
            nombre = cuenta['cuenta']
            
            # Obtener movimientos
            all_movimientos = api_get_all(rut, f'/bancos/{codigo}')
            
            # Filtrar no conciliados
            sin_conciliar = [m for m in all_movimientos if not m.get('conciliado', True)]
            
            abonos_cuenta = sum(m.get('montoAbono', 0) or 0 for m in sin_conciliar)
            cargos_cuenta = sum(m.get('montoCargo', 0) or 0 for m in sin_conciliar)
            
            if sin_conciliar:
                resumen_bancos.append({
                    'banco': nombre,
                    'codigo': codigo,
                    'cantidad': len(sin_conciliar),
                    'abonos': abonos_cuenta,
                    'cargos': cargos_cuenta,
                    'neto': abonos_cuenta - cargos_cuenta,
                })
                
                total_abonos += abonos_cuenta
                total_cargos += cargos_cuenta
                
                for m in sin_conciliar:
                    movimientos_pendientes.append({
                        'id': m.get('id'),
                        'fecha': m.get('fecha'),
                        'banco': nombre,
                        'banco_codigo': codigo,
                        'descripcion': m.get('glosa'),
                        'numero_doc': m.get('numDoc'),
                        'cargo': m.get('montoCargo', 0) or 0,
                        'abono': m.get('montoAbono', 0) or 0,
                    })
        
        resultado['pendientes_conciliar'] = {
            'cantidad': len(movimientos_pendientes),
            'total_abonos': total_abonos,
            'total_cargos': total_cargos,
            'total_neto': total_abonos - total_cargos,
            'cuentas_detectadas': len(cuentas_banco),
            'por_banco': resumen_bancos,
            'movimientos': movimientos_pendientes,
        }
    else:
        resultado['pendientes_conciliar'] = {
            'cantidad': 0,
            'total_abonos': 0,
            'total_cargos': 0,
            'total_neto': 0,
            'cuentas_detectadas': 0,
            'por_banco': [],
            'movimientos': [],
        }
    
    return resultado


def obtener_pendientes(empresa_id: str = None) -> dict:
    """
    Obtiene pendientes de una o todas las empresas.
    
    Args:
        empresa_id: ID de empresa (FIDI, CISI) o RUT. None = todas.
    
    Returns:
        dict con estructura de pendientes
    """
    
    reporte = {
        'generado': datetime.now().isoformat(),
        'version': '1.0',
        'sistema': 'skualo',
        'empresas': [],
        'resumen': {
            'total_sii': 0,
            'total_sii_monto': 0,
            'total_contabilizar': 0,
            'total_contabilizar_monto': 0,
            'total_conciliar': 0,
        }
    }
    
    # Determinar empresas a procesar
    if empresa_id:
        if '-' in empresa_id:
            ruts = [empresa_id]
        elif empresa_id.upper() in TENANTS:
            ruts = [TENANTS[empresa_id.upper()]['rut']]
        else:
            raise ValueError(f"Empresa '{empresa_id}' no encontrada")
    else:
        ruts = [data['rut'] for data in TENANTS.values()]
    
    for rut in ruts:
        try:
            print(f"   Procesando {rut}...")
            pendientes = obtener_pendientes_empresa(rut)
            reporte['empresas'].append(pendientes)
            
            # Acumular totales
            reporte['resumen']['total_sii'] += pendientes['pendientes_sii']['cantidad']
            reporte['resumen']['total_sii_monto'] += pendientes['pendientes_sii']['total']
            reporte['resumen']['total_contabilizar'] += pendientes['pendientes_contabilizar']['cantidad']
            reporte['resumen']['total_contabilizar_monto'] += pendientes['pendientes_contabilizar']['total']
            reporte['resumen']['total_conciliar'] += pendientes['pendientes_conciliar']['cantidad']
            
        except Exception as e:
            nombre = rut
            for key, data in TENANTS.items():
                if data['rut'] == rut:
                    nombre = data.get('nombre', key)
            reporte['empresas'].append({
                'empresa': nombre,
                'rut': rut,
                'error': str(e),
            })
    
    return reporte


def main():
    """Función principal."""
    
    # Parsear argumentos
    empresa_id = None
    output_file = None
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--output' and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif not args[i].startswith('--'):
            empresa_id = args[i]
            i += 1
        else:
            i += 1
    
    print("=" * 70)
    print("   REPORTE DE PENDIENTES SKUALO")
    print("=" * 70)
    print()
    
    if not TOKEN:
        print("❌ Error: SKUALO_API_TOKEN no configurado en .env")
        sys.exit(1)
    
    # Obtener datos
    print("📊 Consultando pendientes...")
    reporte = obtener_pendientes(empresa_id)
    
    # Mostrar resumen
    print()
    print("=" * 70)
    print("   RESUMEN")
    print("=" * 70)
    
    for emp in reporte['empresas']:
        if 'error' in emp:
            print(f"\n❌ {emp['empresa']}: {emp['error']}")
            continue
        
        print(f"\n🏢 {emp['empresa']} ({emp['rut']})")
        print(f"   📄 SII pendientes: {emp['pendientes_sii']['cantidad']} docs (${emp['pendientes_sii']['total']:,.0f})")
        print(f"   📝 Por contabilizar: {emp['pendientes_contabilizar']['cantidad']} docs (${emp['pendientes_contabilizar']['total']:,.0f})")
        print(f"   🏦 Por conciliar: {emp['pendientes_conciliar']['cantidad']} movimientos")
    
    print()
    print("-" * 70)
    print(f"📊 TOTALES:")
    print(f"   Documentos SII: {reporte['resumen']['total_sii']} (${reporte['resumen']['total_sii_monto']:,.0f})")
    print(f"   Por contabilizar: {reporte['resumen']['total_contabilizar']} (${reporte['resumen']['total_contabilizar_monto']:,.0f})")
    print(f"   Movimientos banco: {reporte['resumen']['total_conciliar']}")
    
    # Guardar JSON
    if output_file is None:
        output_dir = SCRIPT_DIR.parent.parent / 'temp'
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sufijo = f"_{empresa_id}" if empresa_id else ""
        output_file = output_dir / f'pendientes_skualo{sufijo}_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, cls=JSONEncoder, ensure_ascii=False, indent=2)
    
    print()
    print(f"✅ JSON guardado: {output_file}")
    print("=" * 70)
    
    return reporte


if __name__ == '__main__':
    main()





