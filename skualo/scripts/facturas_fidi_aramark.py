#!/usr/bin/env python3
"""
Obtener todas las facturas de FIDI a Aramark desde Skualo.

Uso:
    python -m skualo.scripts.facturas_fidi_aramark

Genera:
    - JSON con todas las facturas
    - CSV resumen para Excel
"""

import os
import json
import csv
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

API_BASE = "https://api.skualo.cl"
TOKEN = os.getenv("SKUALO_API_TOKEN")

# FIDI
FIDI_RUT = "77285542-7"

# Aramark
ARAMARK_RUT = "76178360-2"
ARAMARK_NOMBRE = "Central de restaurant aramark Ltda"

# Directorio de salida
OUTPUT_DIR = Path(__file__).parent.parent / "generados"
OUTPUT_DIR.mkdir(exist_ok=True)


def get_headers():
    """Headers para la API."""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json"
    }


def api_get(endpoint, params=None):
    """Llamada GET a la API de Skualo."""
    url = f"{API_BASE}/{FIDI_RUT}{endpoint}"
    print(f"📡 GET {endpoint}")
    
    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=60)
        if response.ok:
            return response.json()
        else:
            print(f"   ❌ Error {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None


def api_get_paginated(endpoint, params=None, page_size=100):
    """Obtiene todos los registros paginados."""
    all_items = []
    page = 1
    base_params = params or {}
    
    while True:
        paged_params = {**base_params, "PageSize": page_size, "Page": page}
        data = api_get(endpoint, paged_params)
        
        if not data:
            break
            
        items = data.get("items", data) if isinstance(data, dict) else data
        if isinstance(items, list):
            all_items.extend(items)
            print(f"   📦 Página {page}: {len(items)} registros (total: {len(all_items)})")
        
        # Verificar si hay más páginas
        if isinstance(data, dict) and data.get("next"):
            page += 1
        else:
            break
    
    return all_items


def get_analisis_por_auxiliar(rut_auxiliar: str):
    """
    Obtiene el análisis de documentos por auxiliar (cliente/proveedor).
    
    Endpoint: GET /{RUT}/contabilidad/reportes/analisisporauxiliar/{idAuxiliar}
    """
    endpoint = f"/contabilidad/reportes/analisisporauxiliar/{rut_auxiliar}"
    return api_get(endpoint)


def get_sii_dte_emitidos():
    """
    Obtiene todos los DTEs emitidos (ventas) desde el SII.
    
    Endpoint: GET /{RUT}/sii/dte
    """
    return api_get_paginated("/sii/dte", page_size=100)


def filtrar_facturas_aramark(dtes: list) -> list:
    """Filtra solo las facturas dirigidas a Aramark."""
    facturas = []
    
    for dte in dtes:
        # Buscar por RUT del receptor
        rut_receptor = dte.get("rutReceptor") or dte.get("receptor", {}).get("rut") or ""
        
        # Normalizar RUT (quitar puntos, mantener guión)
        rut_norm = rut_receptor.replace(".", "").strip()
        
        if ARAMARK_RUT in rut_norm:
            facturas.append(dte)
    
    return facturas


def get_documento_detalle(id_doc: str):
    """Obtiene el detalle de un documento específico."""
    return api_get(f"/documentos/{id_doc}")


def get_documento_por_tipo_folio(tipo_interno: str, folio: int):
    """Obtiene documento por tipo interno y folio."""
    return api_get(f"/documentos/{tipo_interno}/{folio}")


def main():
    print("=" * 70)
    print("FACTURAS FIDI → ARAMARK")
    print(f"FIDI: {FIDI_RUT}")
    print(f"Aramark: {ARAMARK_RUT} - {ARAMARK_NOMBRE}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    if not TOKEN:
        print("❌ ERROR: SKUALO_API_TOKEN no configurado")
        print("   Configura la variable en .env")
        return
    
    # ─────────────────────────────────────────────────────────────────────────
    # MÉTODO 1: Análisis por Auxiliar (más directo)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("📊 MÉTODO 1: Análisis por Auxiliar (cartera Aramark)")
    print("─" * 70)
    
    analisis = get_analisis_por_auxiliar(ARAMARK_RUT)
    
    facturas_analisis = []
    if analisis:
        # El análisis puede ser una lista de movimientos contables
        if isinstance(analisis, list):
            facturas_analisis = analisis
        elif isinstance(analisis, dict):
            facturas_analisis = analisis.get("items", analisis.get("detalles", [analisis]))
        
        print(f"   ✅ Encontrados: {len(facturas_analisis)} registros")
        
        # Guardar JSON
        json_path = OUTPUT_DIR / f"aramark_analisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analisis, f, ensure_ascii=False, indent=2)
        print(f"   💾 Guardado: {json_path}")
    else:
        print("   ⚠️ No se obtuvo respuesta del análisis por auxiliar")
    
    # ─────────────────────────────────────────────────────────────────────────
    # MÉTODO 2: DTEs emitidos y filtrar por Aramark
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("📄 MÉTODO 2: DTEs emitidos (filtrar por Aramark)")
    print("─" * 70)
    
    dtes = get_sii_dte_emitidos()
    
    if dtes:
        print(f"   📑 Total DTEs emitidos: {len(dtes)}")
        
        # Filtrar solo Aramark
        facturas_aramark = filtrar_facturas_aramark(dtes)
        print(f"   🎯 Facturas a Aramark: {len(facturas_aramark)}")
        
        if facturas_aramark:
            # Ordenar por fecha
            facturas_aramark.sort(
                key=lambda x: x.get("fechaEmision") or x.get("fecha") or "1900-01-01",
                reverse=True
            )
            
            # Guardar JSON completo
            json_path = OUTPUT_DIR / f"facturas_aramark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(facturas_aramark, f, ensure_ascii=False, indent=2)
            print(f"   💾 JSON: {json_path}")
            
            # Generar CSV resumen
            csv_path = OUTPUT_DIR / f"facturas_aramark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Tipo", "Folio", "Fecha Emisión", "RUT Receptor", "Razón Social",
                    "Neto", "IVA", "Total", "Estado", "Track ID"
                ])
                
                for fac in facturas_aramark:
                    receptor_data = fac.get("receptor")
                    if isinstance(receptor_data, dict):
                        rut_receptor = fac.get("rutReceptor") or receptor_data.get("rut")
                        razon_social = fac.get("razonSocialReceptor") or receptor_data.get("razonSocial")
                    else:
                        rut_receptor = fac.get("rutReceptor")
                        razon_social = receptor_data  # Es string directo
                    
                    writer.writerow([
                        fac.get("tipoDTE") or fac.get("tipo") or fac.get("idTipoDocumento"),
                        fac.get("folio"),
                        fac.get("fechaEmision") or fac.get("fecha"),
                        rut_receptor,
                        razon_social,
                        fac.get("montoNeto") or fac.get("neto"),
                        fac.get("montoIva") or fac.get("iva"),
                        fac.get("montoTotal") or fac.get("total"),
                        fac.get("estado") or fac.get("estadoSII") or ("✅" if fac.get("recibidoSII") else "⏳"),
                        fac.get("trackId")
                    ])
            print(f"   💾 CSV: {csv_path}")
            
            # Mostrar resumen
            print("\n" + "─" * 70)
            print("📋 RESUMEN DE FACTURAS A ARAMARK")
            print("─" * 70)
            
            total_neto = 0
            total_iva = 0
            total_total = 0
            
            for i, fac in enumerate(facturas_aramark[:20], 1):
                tipo = fac.get("tipoDTE") or fac.get("tipo") or fac.get("idTipoDT")
                folio = fac.get("folio")
                fecha = fac.get("fechaEmision") or fac.get("fecha")
                monto = fac.get("montoTotal") or fac.get("total") or 0
                estado = fac.get("estado") or fac.get("estadoSII") or "?"
                
                print(f"  {i:3}. Tipo {tipo:3} | Folio {folio:6} | {fecha} | ${monto:>12,} | {estado}")
                
                neto = fac.get("montoNeto") or fac.get("neto") or 0
                iva = fac.get("montoIva") or fac.get("iva") or 0
                tot = fac.get("montoTotal") or fac.get("total") or 0
                
                if isinstance(neto, (int, float)):
                    total_neto += neto
                if isinstance(iva, (int, float)):
                    total_iva += iva
                if isinstance(tot, (int, float)):
                    total_total += tot
            
            if len(facturas_aramark) > 20:
                print(f"  ... y {len(facturas_aramark) - 20} más")
            
            print("─" * 70)
            print(f"TOTALES ({len(facturas_aramark)} documentos):")
            print(f"  Neto:  ${total_neto:>15,}")
            print(f"  IVA:   ${total_iva:>15,}")
            print(f"  Total: ${total_total:>15,}")
            
    else:
        print("   ⚠️ No se obtuvieron DTEs emitidos")
    
    # ─────────────────────────────────────────────────────────────────────────
    # RESUMEN FINAL
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print(f"   Archivos en: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()

