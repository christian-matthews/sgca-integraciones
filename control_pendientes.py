#!/usr/bin/env python3
"""
Control de Pendientes - Skualo ERP
==================================
Script 100% genérico para cualquier empresa.

Genera reporte de:
1. Movimientos bancarios sin conciliar
2. Documentos pendientes de aceptar en SII
3. Documentos pendientes de contabilizar

Uso:
    python control_pendientes.py FIDI
    python control_pendientes.py CISI
    python control_pendientes.py 77285542-7
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Configuración
load_dotenv()
TOKEN = os.getenv('SKUALO_API_TOKEN')
BASE_URL = 'https://api.skualo.cl'
DIAS_ACEPTACION_TACITA = 8

# Cargar tenants
TENANTS_FILE = os.path.join(os.path.dirname(__file__), 'tenants.json')
with open(TENANTS_FILE, 'r') as f:
    TENANTS = json.load(f)

# Mapeo de tipos DTE del SII a tipos internos Skualo
TIPO_DTE_A_INTERNO = {
    33: 'FACE',   # Factura Electrónica
    34: 'FXCE',   # Factura No Afecta o Exenta Electrónica
    61: 'NCCE',   # Nota de Crédito Electrónica
    56: 'NDCE',   # Nota de Débito Electrónica
    52: 'GDES',   # Guía de Despacho Electrónica
    110: 'FEXP',  # Factura de Exportación Electrónica
    46: 'FACE',   # Factura de Compra Electrónica (menos común)
}


def get_headers():
    return {
        'Authorization': f'Bearer {TOKEN}',
        'accept': 'application/json'
    }


def get_rut(empresa_id):
    """Obtiene el RUT de la empresa por ID o lo devuelve si ya es un RUT."""
    if '-' in empresa_id:
        return empresa_id
    if empresa_id.upper() in TENANTS:
        return TENANTS[empresa_id.upper()]['rut']
    raise ValueError(f"Empresa '{empresa_id}' no encontrada en tenants.json")


def get_nombre_empresa(rut):
    """Obtiene el nombre de la empresa por RUT."""
    for key, data in TENANTS.items():
        if data['rut'] == rut:
            return data.get('nombre', key)
    return rut


def api_get(rut, endpoint, params=None):
    """Realiza una llamada GET a la API."""
    url = f'{BASE_URL}/{rut}{endpoint}'
    r = requests.get(url, headers=get_headers(), params=params)
    if r.ok:
        return r.json()
    return None


def detectar_cuentas_bancarias(balance):
    """
    Detecta cuentas bancarias del balance de forma inteligente.
    No depende de códigos hardcodeados.
    """
    cuentas_banco = []
    
    # Palabras clave que indican cuenta bancaria
    palabras_banco = [
        'banco', 'santander', 'chile', 'estado', 'bci', 'scotiabank', 
        'itau', 'itaú', 'security', 'bice', 'falabella', 'ripley',
        'consorcio', 'internacional', 'corpbanca', 'tapp', 'tenpo',
        'mercado pago', 'cuenta corriente', 'cta cte', 'cta. cte'
    ]
    
    for cuenta in balance:
        codigo = cuenta.get('idCuenta', '')
        nombre = cuenta.get('cuenta', '').lower()
        
        # Método 1: Prefijo 1102 (estándar para bancos en Chile)
        if codigo.startswith('1102'):
            cuentas_banco.append(cuenta)
            continue
        
        # Método 2: Nombre contiene palabra clave de banco
        if any(palabra in nombre for palabra in palabras_banco):
            # Verificar que sea cuenta de activo (empieza con 1)
            if codigo.startswith('1'):
                cuentas_banco.append(cuenta)
                continue
    
    return cuentas_banco


def obtener_movimientos_sin_conciliar(rut, periodo=None):
    """
    Obtiene todos los movimientos bancarios sin conciliar.
    Detecta automáticamente las cuentas bancarias.
    """
    # Determinar período (usar el mes actual si no se especifica)
    if not periodo:
        periodo = datetime.now().strftime('%Y%m')
    
    # Obtener balance para detectar cuentas bancarias
    balance = api_get(rut, f'/contabilidad/reportes/balancetributario/{periodo}')
    if not balance:
        return [], []
    
    # Detectar cuentas bancarias
    cuentas_banco = detectar_cuentas_bancarias(balance)
    
    # Obtener movimientos sin conciliar de cada cuenta
    resultado = []
    
    for cuenta in cuentas_banco:
        codigo = cuenta['idCuenta']
        nombre = cuenta['cuenta']
        
        # Obtener todos los movimientos (paginado)
        all_movimientos = []
        page = 1
        while True:
            data = api_get(rut, f'/bancos/{codigo}', {'PageSize': 100, 'Page': page})
            if not data:
                break
            items = data.get('items', [])
            all_movimientos.extend(items)
            if not data.get('next'):
                break
            page += 1
        
        # Filtrar no conciliados
        sin_conciliar = [m for m in all_movimientos if not m.get('conciliado', True)]
        
        if sin_conciliar:
            resultado.append({
                'cuenta_codigo': codigo,
                'cuenta_nombre': nombre,
                'total_movimientos': len(all_movimientos),
                'sin_conciliar': len(sin_conciliar),
                'movimientos': sin_conciliar
            })
    
    return resultado, cuentas_banco


def obtener_dtes_recibidos(rut):
    """Obtiene todos los DTEs recibidos del SII."""
    all_dtes = []
    page = 1
    while True:
        data = api_get(rut, '/sii/dte/recibidos', {'PageSize': 100, 'Page': page})
        if not data:
            break
        items = data.get('items', [])
        all_dtes.extend(items)
        if not data.get('next'):
            break
        page += 1
    return all_dtes


def clasificar_dtes(dtes):
    """
    Clasifica los DTEs recibidos en:
    - Pendientes de aceptar (< 8 días sin respuesta)
    - Aceptados (> 8 días o con respuesta)
    """
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
            **dte,
            'dias_desde_recepcion': dias
        }
        
        if not fecha_respuesta and dias <= DIAS_ACEPTACION_TACITA:
            pendientes_aceptar.append(dte_info)
        else:
            aceptados.append(dte_info)
    
    return pendientes_aceptar, aceptados


def verificar_contabilizados(rut, dtes_aceptados):
    """
    Verifica cuáles DTEs aceptados ya están contabilizados.
    Un DTE está contabilizado si existe en /documentos/{tipo}/{folio}
    """
    pendientes_contabilizar = []
    ya_contabilizados = []
    
    for dte in dtes_aceptados:
        tipo_dte = dte.get('idTipoDocumento')
        folio = dte.get('folio')
        
        # Mapear tipo DTE a tipo interno
        tipo_interno = TIPO_DTE_A_INTERNO.get(tipo_dte, 'FACE')
        
        # Verificar si existe en documentos
        doc = api_get(rut, f'/documentos/{tipo_interno}/{folio}')
        
        if doc:
            ya_contabilizados.append({**dte, 'tipo_interno': tipo_interno})
        else:
            pendientes_contabilizar.append({**dte, 'tipo_interno': tipo_interno})
    
    return pendientes_contabilizar, ya_contabilizados


def generar_reporte(empresa_id):
    """Genera el reporte completo de pendientes."""
    rut = get_rut(empresa_id)
    nombre = get_nombre_empresa(rut)
    hoy = datetime.now()
    periodo = hoy.strftime('%Y%m')
    
    print('=' * 80)
    print(f'CONTROL DE PENDIENTES - {nombre}')
    print(f'RUT: {rut}')
    print(f'Fecha: {hoy.strftime("%Y-%m-%d %H:%M")}')
    print('=' * 80)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 1. MOVIMIENTOS BANCARIOS SIN CONCILIAR
    # ═══════════════════════════════════════════════════════════════════════════
    print('\n' + '─' * 80)
    print('1. 🏦 MOVIMIENTOS BANCARIOS SIN CONCILIAR')
    print('─' * 80)
    
    movimientos_result, cuentas_detectadas = obtener_movimientos_sin_conciliar(rut, periodo)
    
    print(f'\n   Cuentas bancarias detectadas: {len(cuentas_detectadas)}')
    for c in cuentas_detectadas:
        print(f'      • {c["idCuenta"]}: {c["cuenta"]}')
    
    total_sin_conciliar = 0
    if movimientos_result:
        print(f'\n   Movimientos sin conciliar:')
        for cuenta in movimientos_result:
            print(f'\n   📌 {cuenta["cuenta_nombre"]} ({cuenta["cuenta_codigo"]})')
            print(f'      Total movimientos: {cuenta["total_movimientos"]}')
            print(f'      Sin conciliar: {cuenta["sin_conciliar"]}')
            total_sin_conciliar += cuenta["sin_conciliar"]
            
            # Mostrar detalle de movimientos sin conciliar
            if cuenta["movimientos"]:
                print(f'\n      {"Fecha":<12} {"NumDoc":<12} {"Cargo":>12} {"Abono":>12} {"Glosa":<25}')
                print(f'      {"-"*73}')
                for m in cuenta["movimientos"][:10]:
                    fecha = str(m.get('fecha', ''))[:10]
                    num = str(m.get('numDoc', ''))[:12]
                    cargo = m.get('montoCargo', 0) or 0
                    abono = m.get('montoAbono', 0) or 0
                    glosa = str(m.get('glosa', ''))[:25]
                    cargo_s = f'{cargo:>12,.0f}' if cargo else ' ' * 12
                    abono_s = f'{abono:>12,.0f}' if abono else ' ' * 12
                    print(f'      {fecha:<12} {num:<12} {cargo_s} {abono_s} {glosa}')
                if len(cuenta["movimientos"]) > 10:
                    print(f'      ... y {len(cuenta["movimientos"]) - 10} más')
    else:
        print('\n   ✅ Todos los movimientos están conciliados')
    
    print(f'\n   📊 TOTAL MOVIMIENTOS SIN CONCILIAR: {total_sin_conciliar}')
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 2. DOCUMENTOS PENDIENTES DE ACEPTAR EN SII
    # ═══════════════════════════════════════════════════════════════════════════
    print('\n' + '─' * 80)
    print('2. 📄 DOCUMENTOS PENDIENTES DE ACEPTAR EN SII (< 8 días)')
    print('─' * 80)
    
    dtes = obtener_dtes_recibidos(rut)
    pendientes_aceptar, aceptados = clasificar_dtes(dtes)
    
    if pendientes_aceptar:
        print(f'\n   {"Emisor":<30} {"Tipo":<15} {"Folio":<10} {"Días":>5} {"Total":>15}')
        print(f'   {"-"*77}')
        total = 0
        for dte in sorted(pendientes_aceptar, key=lambda x: x['dias_desde_recepcion']):
            emisor = str(dte.get('emisor', ''))[:30]
            tipo = str(dte.get('tipoDocumento', ''))[:15]
            folio = dte.get('folio', '')
            dias = dte.get('dias_desde_recepcion', 0)
            monto = dte.get('montoTotal', 0)
            total += monto
            print(f'   {emisor:<30} {tipo:<15} {folio:<10} {dias:>5} {monto:>15,.0f}')
        print(f'   {"-"*77}')
        print(f'   {"TOTAL":>62} {total:>15,.0f}')
    else:
        print('\n   ✅ No hay documentos pendientes de aceptar')
    
    print(f'\n   📊 TOTAL PENDIENTES DE ACEPTAR: {len(pendientes_aceptar)}')
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3. DOCUMENTOS PENDIENTES DE CONTABILIZAR
    # ═══════════════════════════════════════════════════════════════════════════
    print('\n' + '─' * 80)
    print('3. 📋 DOCUMENTOS PENDIENTES DE CONTABILIZAR')
    print('─' * 80)
    
    print(f'\n   Verificando {len(aceptados)} DTEs aceptados...')
    pendientes_contabilizar, ya_contabilizados = verificar_contabilizados(rut, aceptados)
    
    if pendientes_contabilizar:
        print(f'\n   {"Emisor":<30} {"Tipo":<15} {"Folio":<10} {"Fecha":<12} {"Total":>15}')
        print(f'   {"-"*84}')
        total = 0
        for dte in sorted(pendientes_contabilizar, key=lambda x: x.get('fechaEmision', ''), reverse=True):
            emisor = str(dte.get('emisor', ''))[:30]
            tipo = str(dte.get('tipoDocumento', ''))[:15]
            folio = dte.get('folio', '')
            fecha = str(dte.get('fechaEmision', ''))[:10]
            monto = dte.get('montoTotal', 0)
            total += monto
            print(f'   {emisor:<30} {tipo:<15} {folio:<10} {fecha:<12} {monto:>15,.0f}')
        print(f'   {"-"*84}')
        print(f'   {"TOTAL":>69} {total:>15,.0f}')
    else:
        print('\n   ✅ Todos los documentos están contabilizados')
    
    print(f'\n   📊 TOTAL PENDIENTES DE CONTABILIZAR: {len(pendientes_contabilizar)}')
    print(f'   📊 YA CONTABILIZADOS: {len(ya_contabilizados)}')
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ═══════════════════════════════════════════════════════════════════════════
    print('\n' + '=' * 80)
    print('RESUMEN EJECUTIVO')
    print('=' * 80)
    print(f'''
   🏦 Movimientos sin conciliar:     {total_sin_conciliar:>5}
   📄 Documentos por aceptar SII:    {len(pendientes_aceptar):>5}
   📋 Documentos por contabilizar:   {len(pendientes_contabilizar):>5}
   ✅ Documentos contabilizados:     {len(ya_contabilizados):>5}
''')
    print('=' * 80)
    
    return {
        'empresa': nombre,
        'rut': rut,
        'fecha': hoy.isoformat(),
        'movimientos_sin_conciliar': total_sin_conciliar,
        'pendientes_aceptar': len(pendientes_aceptar),
        'pendientes_contabilizar': len(pendientes_contabilizar),
        'ya_contabilizados': len(ya_contabilizados),
    }


def main():
    if len(sys.argv) < 2:
        print('Uso: python control_pendientes.py <EMPRESA>')
        print('')
        print('Empresas disponibles:')
        for key, data in TENANTS.items():
            print(f'  {key}: {data.get("nombre", "")} ({data["rut"]})')
        sys.exit(1)
    
    empresa = sys.argv[1]
    
    try:
        generar_reporte(empresa)
    except ValueError as e:
        print(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'Error inesperado: {e}')
        raise


if __name__ == '__main__':
    main()

