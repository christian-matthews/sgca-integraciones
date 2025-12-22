"""
Explorar endpoints de Documentos - Skualo API
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://api.skualo.cl"
TOKEN = os.getenv("SKUALO_API_TOKEN")

with open("tenants.json", "r") as f:
    TENANTS = json.load(f)

TENANT = TENANTS["FIDI"]


def api_get(path, accept="application/json"):
    """Llamada GET a la API"""
    url = f"{API_BASE}/{TENANT['rut']}{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "accept": accept
    }
    print(f"\n🔄 GET {path[:80]}...")
    
    response = requests.get(url, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.ok:
        if accept == "text/xml":
            return response.text
        return response.json()
    else:
        print(f"   Error: {response.text[:150]}")
        return None


def main():
    print("═" * 60)
    print("   EXPLORAR DOCUMENTOS - FILTROS CORRECTOS")
    print("═" * 60)

    # Probar con filtros correctos
    print("\n" + "─" * 60)
    print("PROBAR /documentos CON FILTROS CORRECTOS")
    print("─" * 60)
    
    # IDTipoDocumento = tipo DTE (33=Factura, 34=Exenta, etc.)
    # IDTipoDT = tipo documento interno (FAVE, FACE, etc.)
    
    filtros_probar = [
        "IDTipoDocumento=33",
        "IDTipoDT=33",
        "IDTipoDT=FAVE",
        "Fecha=2025-11-01",
        "Folio=1",
        "IDEstado=1",
    ]
    
    for filtro in filtros_probar:
        docs = api_get(f"/documentos?{filtro}")
        if docs:
            if isinstance(docs, dict) and "items" in docs:
                items = docs["items"]
            else:
                items = docs if isinstance(docs, list) else [docs]
            
            print(f"   ✅ {len(items)} documentos")
            if items:
                print(f"   Campos: {list(items[0].keys())[:10]}...")
                # Guardar primer resultado
                with open(f"docs_{filtro.replace('=', '_')}.json", "w") as f:
                    json.dump(items[:3], f, indent=2, ensure_ascii=False)

    # Probar combinaciones
    print("\n" + "─" * 60)
    print("COMBINACIONES DE FILTROS")
    print("─" * 60)
    
    combos = [
        "IDTipoDocumento=33&Fecha=2025-11-01",
        "IDTipoDocumento=33&Folio=1",
    ]
    
    for combo in combos:
        docs = api_get(f"/documentos?{combo}")
        if docs:
            if isinstance(docs, dict) and "items" in docs:
                items = docs["items"]
            else:
                items = docs if isinstance(docs, list) else [docs]
            
            print(f"   ✅ {len(items)} documentos")
            if items and len(items) > 0:
                # Guardar para análisis
                with open("documentos_encontrados.json", "w") as f:
                    json.dump(items, f, indent=2, ensure_ascii=False)
                print(f"   💾 Guardado: documentos_encontrados.json")
                
                # Mostrar estructura
                doc = items[0]
                print(f"\n   📋 Estructura del documento:")
                for key, value in doc.items():
                    val_str = str(value)[:50] if value else "null"
                    print(f"      {key}: {val_str}")

    print("\n" + "═" * 60)


if __name__ == "__main__":
    main()
