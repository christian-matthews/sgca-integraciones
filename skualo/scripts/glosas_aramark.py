#!/usr/bin/env python3
"""
Extraer glosas de facturas FIDI → Aramark
"""

import os
import json
import csv
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://api.skualo.cl"
TOKEN = os.getenv("SKUALO_API_TOKEN")
FIDI_RUT = "77285542-7"

OUTPUT_DIR = Path(__file__).parent.parent / "generados"
OUTPUT_DIR.mkdir(exist_ok=True)

# IDs de las facturas a Aramark (actualizado 29-dic-2025)
FACTURAS_ARAMARK = [
    {"id": "ae89f359-2a2f-47aa-bdad-bb2bce8c694b", "tipo": 33, "folio": 340, "fecha": "2025-12-29"},
    {"id": "26fe7946-0c0d-4e58-ab5a-d6838279596c", "tipo": 33, "folio": 341, "fecha": "2025-12-29"},
    {"id": "69a101dd-0d27-43ce-9db6-855a4fd24829", "tipo": 33, "folio": 334, "fecha": "2025-11-27"},
    {"id": "574efa8e-00ad-417c-97d8-24ba96b5a7a9", "tipo": 33, "folio": 335, "fecha": "2025-11-27"},
    {"id": "da83a138-eb70-4306-a152-f60ef47ffbad", "tipo": 61, "folio": 28, "fecha": "2025-11-27"},
    {"id": "1d46bdb9-7b7d-452e-a4d8-ff489fdbd1b3", "tipo": 33, "folio": 333, "fecha": "2025-11-24"},
    {"id": "47d34918-b5b4-42a3-bcdd-82d53807b0b1", "tipo": 33, "folio": 328, "fecha": "2025-10-20"},
    {"id": "5330a614-e638-4d43-abfd-8c9894f0c160", "tipo": 33, "folio": 147, "fecha": "2025-09-25"},
    {"id": "b9bf78cb-f998-437f-9d64-3fb1e8aef36b", "tipo": 33, "folio": 145, "fecha": "2025-09-16"},
    {"id": "1624b870-4806-4bb5-a476-4f2c3c3b10e7", "tipo": 33, "folio": 146, "fecha": "2025-09-16"},
    {"id": "0a9d5b38-ad53-4218-871a-00f36ede55d0", "tipo": 33, "folio": 141, "fecha": "2025-08-21"},
    {"id": "1b6790d1-f001-4278-9d62-a06f5a024bf5", "tipo": 33, "folio": 140, "fecha": "2025-08-07"},
    {"id": "cbd07a32-a79a-46a2-9579-139b02ff3574", "tipo": 33, "folio": 137, "fecha": "2025-07-02"},
    {"id": "2a5febe1-813d-432e-b064-c918d75f0439", "tipo": 61, "folio": 8, "fecha": "2025-05-09"},
    {"id": "e904c05a-c00c-44bd-aea6-d5404ae61f58", "tipo": 61, "folio": 9, "fecha": "2025-05-09"},
    {"id": "ee8b414e-2337-4f39-9ac4-a1a99ad4ad26", "tipo": 61, "folio": 10, "fecha": "2025-05-09"},
]


def get_headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json"
    }


def get_documento_detalle(doc_id: str):
    """Obtiene el detalle completo de un documento."""
    url = f"{API_BASE}/{FIDI_RUT}/documentos/{doc_id}"
    try:
        r = requests.get(url, headers=get_headers(), timeout=30)
        if r.ok:
            return r.json()
        else:
            print(f"   ❌ Error {r.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ {e}")
        return None


def main():
    print("=" * 80)
    print("GLOSAS DE FACTURAS FIDI → ARAMARK")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_docs = []
    all_glosas = []
    
    for fac in FACTURAS_ARAMARK:
        tipo_str = "Factura" if fac["tipo"] == 33 else "Nota Crédito"
        print(f"\n📄 {tipo_str} Folio {fac['folio']} ({fac['fecha']})")
        
        doc = get_documento_detalle(fac["id"])
        
        if doc:
            all_docs.append(doc)
            
            # Extraer glosas de los detalles
            detalles = doc.get("detalles", [])
            
            if detalles:
                for i, det in enumerate(detalles, 1):
                    glosa = det.get("glosa") or det.get("descripcion") or det.get("nombre") or "Sin glosa"
                    cantidad = det.get("cantidad", 1)
                    precio = det.get("precioUnitario") or det.get("precio") or 0
                    total = det.get("montoItem") or det.get("total") or (cantidad * precio)
                    
                    print(f"   {i}. {glosa[:70]}")
                    if precio:
                        print(f"      Cant: {cantidad} x ${precio:,.0f} = ${total:,.0f}")
                    
                    all_glosas.append({
                        "tipo": tipo_str,
                        "folio": fac["folio"],
                        "fecha": fac["fecha"],
                        "linea": i,
                        "glosa": glosa,
                        "cantidad": cantidad,
                        "precio_unitario": precio,
                        "total": total
                    })
            else:
                # Buscar glosa en otros campos
                glosa_doc = doc.get("glosa") or doc.get("observacion") or "Sin detalle"
                print(f"   → {glosa_doc}")
                all_glosas.append({
                    "tipo": tipo_str,
                    "folio": fac["folio"],
                    "fecha": fac["fecha"],
                    "linea": 1,
                    "glosa": glosa_doc,
                    "cantidad": 1,
                    "precio_unitario": doc.get("neto") or doc.get("montoNeto") or 0,
                    "total": doc.get("total") or doc.get("montoTotal") or 0
                })
        else:
            print("   ⚠️ No se pudo obtener detalle")
    
    # Guardar JSON completo
    json_path = OUTPUT_DIR / f"aramark_detalles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)
    print(f"\n💾 JSON completo: {json_path}")
    
    # Guardar CSV de glosas
    csv_path = OUTPUT_DIR / f"aramark_glosas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["tipo", "folio", "fecha", "linea", "glosa", "cantidad", "precio_unitario", "total"])
        writer.writeheader()
        writer.writerows(all_glosas)
    print(f"💾 CSV glosas: {csv_path}")
    
    # Resumen de glosas únicas
    print("\n" + "=" * 80)
    print("RESUMEN DE GLOSAS ÚNICAS")
    print("=" * 80)
    
    glosas_unicas = {}
    for g in all_glosas:
        key = g["glosa"][:100]  # Truncar para agrupar
        if key not in glosas_unicas:
            glosas_unicas[key] = {"count": 0, "total": 0}
        glosas_unicas[key]["count"] += 1
        glosas_unicas[key]["total"] += g["total"] or 0
    
    for glosa, data in sorted(glosas_unicas.items(), key=lambda x: -x[1]["total"]):
        print(f"\n• {glosa}")
        print(f"  Apariciones: {data['count']} | Total: ${data['total']:,.0f}")


if __name__ == "__main__":
    main()

