#!/usr/bin/env python3
"""
Skualo - Cliente de Pendientes
==============================

Módulo para obtener pendientes desde la plataforma Skualo.
Equivalente a odoo/pendientes.py pero para Skualo.

Estructura de salida normalizada (compatible con bridge):
{
    "empresa": "Nombre Empresa",
    "database": "alias",  # Para compatibilidad con Odoo
    "rut": "12345678-9",
    "fecha_consulta": "2025-01-15T10:30:00",
    "pendientes_sii": {"cantidad": N, "total": M, "documentos": [...]},
    "pendientes_contabilizar": {"cantidad": N, "documentos": [...]},
    "pendientes_conciliar": {"cantidad": N, "movimientos": [...]}
}

Uso:
    from skualo.pendientes import obtener_pendientes_empresa
    
    data = obtener_pendientes_empresa("77285542-7")
    # o
    data = obtener_pendientes_empresa("FIDI")  # Por alias
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv
load_dotenv()


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

TOKEN = os.getenv('SKUALO_API_TOKEN')
BASE_URL = os.getenv('SKUALO_BASE_URL', 'https://api.skualo.cl')
DIAS_ACEPTACION_TACITA = 8

# Cargar tenants
_tenants_cache = None

def _get_tenants() -> Dict[str, Dict]:
    """Carga y cachea tenants.json."""
    global _tenants_cache
    if _tenants_cache is None:
        tenants_file = Path(__file__).parent / 'config' / 'tenants.json'
        try:
            with open(tenants_file, 'r') as f:
                _tenants_cache = json.load(f)
        except FileNotFoundError:
            _tenants_cache = {}
    return _tenants_cache




# Mapeo de tipos DTE
TIPO_DTE_A_INTERNO = {
    33: 'FACE',   # Factura Electrónica
    34: 'FXCE',   # Factura No Afecta o Exenta Electrónica
    61: 'NCCE',   # Nota de Crédito Electrónica
    56: 'NDCE',   # Nota de Débito Electrónica
    52: 'GDES',   # Guía de Despacho Electrónica
    110: 'FEXP',  # Factura de Exportación Electrónica
}

# Tipos DTE a excluir del análisis de pendientes (no requieren contabilización)
TIPOS_DTE_EXCLUIR = {52}  # Guías de Despacho


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS API
# ═══════════════════════════════════════════════════════════════════════════════

def _get_headers() -> Dict[str, str]:
    """Retorna headers para API Skualo."""
    return {
        'Authorization': f'Bearer {TOKEN}',
        'accept': 'application/json'
    }


def _api_get(rut: str, endpoint: str, params: dict = None) -> Optional[Any]:
    """Realiza llamada GET a la API."""
    url = f'{BASE_URL}/{rut}{endpoint}'
    try:
        r = requests.get(url, headers=_get_headers(), params=params, timeout=30)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return None


def _api_get_all(rut: str, endpoint: str, params: dict = None) -> List[Any]:
    """Obtiene todos los registros paginados."""
    all_items = []
    page = 1
    base_params = params or {}
    
    while True:
        paged_params = {**base_params, 'PageSize': 100, 'Page': page}
        data = _api_get(rut, endpoint, paged_params)
        if not data:
            break
        items = data.get('items', data) if isinstance(data, dict) else data
        if isinstance(items, list):
            all_items.extend(items)
        if not data.get('next'):
            break
        page += 1
    
    return all_items


def _detectar_cuentas_bancarias(balance: list) -> list:
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


def _resolve_rut(empresa_id: str) -> tuple:
    """
    Resuelve un identificador de empresa a (rut, nombre).
    
    Args:
        empresa_id: Puede ser RUT (77285542-7) o alias (FIDI)
    
    Returns:
        Tupla (rut, nombre)
    """
    tenants = _get_tenants()
    
    # Si es un alias
    if empresa_id.upper() in tenants:
        config = tenants[empresa_id.upper()]
        return config['rut'], config.get('nombre', empresa_id)
    
    # Si es un RUT, buscar nombre en tenants
    for key, config in tenants.items():
        if config['rut'] == empresa_id:
            return empresa_id, config.get('nombre', key)
    
    # RUT sin nombre conocido
    return empresa_id, empresa_id


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════════

def obtener_pendientes_empresa(empresa_id: str) -> Dict[str, Any]:
    """
    Obtiene todos los pendientes de una empresa Skualo.
    
    Estructura normalizada compatible con bridge:
    - pendientes_sii: Documentos por aceptar en SII
    - pendientes_contabilizar: Documentos por contabilizar
    - pendientes_conciliar: Movimientos bancarios sin conciliar
    
    Args:
        empresa_id: RUT (77285542-7) o alias (FIDI)
    
    Returns:
        Dict con estructura normalizada de pendientes
    """
    rut, nombre = _resolve_rut(empresa_id)
    
    resultado = {
        'empresa': nombre,
        'database': empresa_id,  # Compatibilidad con Odoo
        'rut': rut,
        'fecha_consulta': datetime.now().isoformat(),
        'pendientes_sii': {'cantidad': 0, 'total': 0, 'documentos': []},
        'pendientes_contabilizar': {'cantidad': 0, 'documentos': []},
        'pendientes_conciliar': {'cantidad': 0, 'movimientos': []},
    }
    
    periodo = datetime.now().strftime('%Y%m')
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. DOCUMENTOS RECIBIDOS SII (solo año actual)
    # ═══════════════════════════════════════════════════════════════════
    dtes_raw = _api_get_all(rut, '/sii/dte/recibidos')
    
    hoy = datetime.now()
    anio_actual = str(hoy.year)
    
    # Filtrar solo DTEs del año actual
    dtes = [d for d in dtes_raw if d.get('fechaEmision', '').startswith(anio_actual)]
    
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
            except (ValueError, TypeError):
                pass
        
        dte_info = {
            'id': dte.get('id'),
            'fecha': dte.get('fechaEmision'),
            'tipo': dte.get('tipoDocumento'),
            'tipo_id': dte.get('idTipoDocumento'),
            'folio': dte.get('folio'),
            'proveedor_rut': dte.get('rutEmisor'),
            'proveedor_nombre': dte.get('emisor'),
            'monto': dte.get('montoTotal', 0),
            'dias_desde_recepcion': dias,
            'fecha_respuesta': fecha_respuesta,
        }
        
        if not fecha_respuesta and dias <= DIAS_ACEPTACION_TACITA:
            pendientes_aceptar.append(dte_info)
        else:
            aceptados.append(dte_info)
    
    total_sii = sum(d['monto'] or 0 for d in pendientes_aceptar)
    
    resultado['pendientes_sii'] = {
        'cantidad': len(pendientes_aceptar),
        'total': total_sii,
        'documentos': pendientes_aceptar,
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # 2. DOCUMENTOS POR CONTABILIZAR (optimizado: libro de compras 2025)
    # ═══════════════════════════════════════════════════════════════════
    pendientes_contabilizar = []
    
    # Obtener libro de compras de todo 2025 (12 llamadas vs N por DTE)
    folios_contabilizados = set()
    meses_consultados = 0
    
    hoy = datetime.now()
    mes_actual = hoy.month
    
    # Consultar desde enero hasta el mes actual
    for mes in range(1, mes_actual + 1):
        periodo = f'2025{mes:02d}'
        
        libro = _api_get(rut, f'/contabilidad/reportes/librocompras/{periodo}', {'IdSucursal': 0})
        
        if libro and isinstance(libro, list):
            meses_consultados += 1
            for item in libro:
                # Campo es 'NumDoc' (mayúscula) en libro de compras
                folio = item.get('NumDoc') or item.get('numDoc') or item.get('folio')
                if folio:
                    folios_contabilizados.add(str(folio))
    
    # Cruzar: DTEs aceptados que NO están en el libro = pendientes
    # Excluir Guías de Despacho (tipo 52) que no requieren contabilización
    for dte in aceptados:
        tipo_id = dte.get('tipo_id')
        
        # Omitir tipos excluidos (Guías de Despacho, etc.)
        if tipo_id in TIPOS_DTE_EXCLUIR:
            continue
        
        folio = str(dte.get('folio', ''))
        tipo_interno = TIPO_DTE_A_INTERNO.get(tipo_id, 'FACE')
        
        if folio and folio not in folios_contabilizados:
            pendientes_contabilizar.append({**dte, 'tipo_interno': tipo_interno})
    
    resultado['pendientes_contabilizar'] = {
        'cantidad': len(pendientes_contabilizar),
        'documentos': pendientes_contabilizar,
        '_libro_compras_count': len(folios_contabilizados),
        '_meses_consultados': meses_consultados
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. MOVIMIENTOS BANCARIOS SIN CONCILIAR
    # ═══════════════════════════════════════════════════════════════════
    balance = _api_get(rut, f'/contabilidad/reportes/balancetributario/{periodo}')
    
    if balance:
        cuentas_banco = _detectar_cuentas_bancarias(balance)
        movimientos_pendientes = []
        total_abonos = 0
        total_cargos = 0
        
        for cuenta in cuentas_banco:
            codigo = cuenta['idCuenta']
            nombre_cuenta = cuenta['cuenta']
            
            # Obtener movimientos
            all_movimientos = _api_get_all(rut, f'/bancos/{codigo}')
            
            # Filtrar no conciliados
            sin_conciliar = [m for m in all_movimientos if not m.get('conciliado', True)]
            
            for m in sin_conciliar:
                cargo = m.get('montoCargo', 0) or 0
                abono = m.get('montoAbono', 0) or 0
                total_abonos += abono
                total_cargos += cargo
                
                movimientos_pendientes.append({
                    'id': m.get('id'),
                    'fecha': m.get('fecha'),
                    'banco': nombre_cuenta,
                    'banco_codigo': codigo,
                    'descripcion': m.get('glosa'),
                    'numero_doc': m.get('numDoc'),
                    'monto': abono - cargo,  # Normalizado como en Odoo
                    'referencia': m.get('numDoc'),
                })
        
        resultado['pendientes_conciliar'] = {
            'cantidad': len(movimientos_pendientes),
            'total_abonos': total_abonos,
            'total_cargos': total_cargos,
            'total_neto': total_abonos - total_cargos,
            'movimientos': movimientos_pendientes,
        }
    
    return resultado


def obtener_pendientes(empresa_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtiene pendientes de una o todas las empresas.
    
    Args:
        empresa_id: ID de empresa (FIDI, CISI) o RUT. None = todas las activas.
    
    Returns:
        Dict con estructura de reporte
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
            'total_conciliar': 0,
        }
    }
    
    tenants = _get_tenants()
    
    # Determinar empresas a procesar
    if empresa_id:
        rut, nombre = _resolve_rut(empresa_id)
        ruts = [(rut, nombre)]
    else:
        ruts = [
            (config['rut'], config.get('nombre', key))
            for key, config in tenants.items()
            if config.get('activo', True)
        ]
    
    for rut, nombre in ruts:
        try:
            pendientes = obtener_pendientes_empresa(rut)
            reporte['empresas'].append(pendientes)
            
            # Acumular totales
            reporte['resumen']['total_sii'] += pendientes['pendientes_sii']['cantidad']
            reporte['resumen']['total_sii_monto'] += pendientes['pendientes_sii']['total']
            reporte['resumen']['total_contabilizar'] += pendientes['pendientes_contabilizar']['cantidad']
            reporte['resumen']['total_conciliar'] += pendientes['pendientes_conciliar']['cantidad']
            
        except Exception as e:
            reporte['empresas'].append({
                'empresa': nombre,
                'rut': rut,
                'error': str(e),
            })
    
    return reporte


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI para testing."""
    import sys
    
    empresa_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("=" * 70)
    print("   PENDIENTES SKUALO")
    print("=" * 70)
    
    if not TOKEN:
        print("❌ Error: SKUALO_API_TOKEN no configurado")
        sys.exit(1)
    
    reporte = obtener_pendientes(empresa_id)
    
    for emp in reporte['empresas']:
        if 'error' in emp:
            print(f"\n❌ {emp['empresa']}: {emp['error']}")
            continue
        
        print(f"\n🏢 {emp['empresa']} ({emp['rut']})")
        print(f"   📄 SII: {emp['pendientes_sii']['cantidad']} docs")
        print(f"   📝 Contabilizar: {emp['pendientes_contabilizar']['cantidad']} docs")
        print(f"   🏦 Conciliar: {emp['pendientes_conciliar']['cantidad']} movs")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()






