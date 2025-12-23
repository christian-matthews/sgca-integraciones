#!/usr/bin/env python3
"""
Seed FactorIT Companies en SGCA Core
====================================

Crea las empresas FactorIT en Supabase (SGCA Core) si no existen.
Esto es necesario para que el bridge pueda sincronizar checks.

Uso:
    python scripts/seed_factorit_companies.py
    python scripts/seed_factorit_companies.py --dry-run

NO modifica sgca-core (solo escribe a la tabla companies de Supabase).
"""

import os
import sys
import argparse
import uuid
from datetime import datetime

# Agregar paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from bridge.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
from supabase import create_client, Client


# Tenant por defecto (debe existir)
DEFAULT_TENANT_ID = "11111111-1111-1111-1111-111111111111"

# Empresas a crear
FACTORIT_COMPANIES = [
    {
        "name": "FactorIT SpA",
        "package_code": "ESTANDAR",  # Semanal
        "health_status": "AL_DIA",
        "status_lock_level": None,  # Sin bloqueo
    },
    {
        "name": "FactorIT Ltda",
        "package_code": "ESTANDAR",  # Semanal
        "health_status": "AL_DIA",
        "status_lock_level": None,  # Sin bloqueo
    },
]


def get_supabase() -> Client:
    """Retorna cliente Supabase."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY requeridos en .env")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def seed_companies(dry_run: bool = False):
    """Crea las empresas FactorIT si no existen."""
    
    print("=" * 60)
    print("  SEED FACTORIT COMPANIES")
    print("=" * 60)
    
    if dry_run:
        print("\n⚠️ DRY-RUN: No se escribirá nada")
    
    sb = get_supabase()
    
    # Verificar empresas existentes
    existing = sb.table("companies").select("name, company_id").execute()
    existing_names = {c["name"] for c in (existing.data or [])}
    
    print(f"\n📊 Empresas existentes en SGCA: {len(existing_names)}")
    for name in existing_names:
        print(f"   - {name}")
    
    created = 0
    skipped = 0
    
    for company in FACTORIT_COMPANIES:
        name = company["name"]
        
        if name in existing_names:
            print(f"\n⏭️ {name}: Ya existe, saltando")
            skipped += 1
            continue
        
        if dry_run:
            print(f"\n[DRY-RUN] Crearía: {name}")
            continue
        
        # Obtener tenant_id del primer tenant existente o usar el default
        tenant_id = DEFAULT_TENANT_ID
        tenants = sb.table("tenants").select("tenant_id").limit(1).execute()
        if tenants.data:
            tenant_id = tenants.data[0]["tenant_id"]
        
        # Crear empresa (schema según SYSTEM_INDEX_TRUTH)
        new_company = {
            "company_id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "name": company["name"],
            "package_code": company["package_code"],
            "health_status": company["health_status"],
            "status_lock_level": company["status_lock_level"],
            "created_at": datetime.now().isoformat(),
        }
        
        try:
            result = sb.table("companies").insert(new_company).execute()
            
            if result.data:
                print(f"\n✅ {name}: Creada ({result.data[0]['company_id'][:8]}...)")
                created += 1
            else:
                print(f"\n❌ {name}: Error al crear")
                
        except Exception as e:
            print(f"\n❌ {name}: Error: {e}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    print(f"  Creadas: {created}")
    print(f"  Saltadas (ya existían): {skipped}")
    
    if dry_run:
        print("\n⚠️ DRY-RUN completado. Ejecutar sin --dry-run para crear.")
    
    return created


def main():
    parser = argparse.ArgumentParser(
        description='Seed empresas FactorIT en SGCA Core'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='No escribir, solo mostrar qué haría'
    )
    
    args = parser.parse_args()
    
    try:
        seed_companies(args.dry_run)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

