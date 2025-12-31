#!/usr/bin/env python3
"""
SGCA Smoke Test E2E - FactorIT
==============================

Test end-to-end que valida:
1. Conexión a Odoo (obtener pendientes)
2. Conexión a Supabase (SGCA Core)
3. Ejecución del bridge (sync Odoo → checks)
4. Ejecución del motor (daily_run.py) - si está disponible
5. Consulta de resultados (checks y findings)

Uso:
    python scripts/smoke_test_factorit_e2e.py
    python scripts/smoke_test_factorit_e2e.py --period 2025-01 --only FactorIT
    python scripts/smoke_test_factorit_e2e.py --skip-motor  # No ejecutar daily_run.py

NO modifica sgca-core.
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

# Agregar paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Imports locales
try:
    from odoo.pendientes import obtener_pendientes_empresa, DATABASES
    ODOO_AVAILABLE = True
except ImportError as e:
    ODOO_AVAILABLE = False
    print(f"⚠️ Odoo module no disponible: {e}")

try:
    from bridge.sync_odoo_to_checks import sync_all, get_supabase
    from bridge.sla_calculator import today_chile, now_chile
    BRIDGE_AVAILABLE = True
except ImportError as e:
    BRIDGE_AVAILABLE = False
    print(f"⚠️ Bridge module no disponible: {e}")

# Path al core (si existe)
SGCA_CORE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "sgca-core"
)


def print_header(text: str):
    """Imprime header con formato."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")


def print_section(text: str):
    """Imprime sección con formato."""
    print(f"\n{'─'*50}")
    print(f"  {text}")
    print(f"{'─'*50}")


def test_odoo_connection(db_alias: str = "FactorIT") -> Dict[str, Any]:
    """
    Test 1: Conexión a Odoo y obtención de pendientes.
    """
    print_section(f"TEST 1: Conexión Odoo ({db_alias})")
    
    result = {
        "test": "odoo_connection",
        "empresa": db_alias,
        "success": False,
        "pendientes": None,
        "error": None,
    }
    
    if not ODOO_AVAILABLE:
        result["error"] = "Módulo Odoo no disponible"
        print(f"  ❌ {result['error']}")
        return result
    
    try:
        pendientes = obtener_pendientes_empresa(db_alias)
        
        result["success"] = True
        result["pendientes"] = {
            "sii": pendientes["pendientes_sii"]["cantidad"],
            "contabilizar": pendientes["pendientes_contabilizar"]["cantidad"],
            "conciliar": pendientes["pendientes_conciliar"]["cantidad"],
        }
        
        print(f"  ✅ Conexión exitosa")
        print(f"     📄 Pendientes SII: {result['pendientes']['sii']}")
        print(f"     📝 Por contabilizar: {result['pendientes']['contabilizar']}")
        print(f"     🏦 Por conciliar: {result['pendientes']['conciliar']}")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"  ❌ Error: {e}")
    
    return result


def test_supabase_connection() -> Dict[str, Any]:
    """
    Test 2: Conexión a Supabase (SGCA Core).
    """
    print_section("TEST 2: Conexión Supabase (SGCA Core)")
    
    result = {
        "test": "supabase_connection",
        "success": False,
        "companies_count": 0,
        "error": None,
    }
    
    if not BRIDGE_AVAILABLE:
        result["error"] = "Módulo Bridge no disponible"
        print(f"  ❌ {result['error']}")
        return result
    
    try:
        sb = get_supabase()
        
        # Contar empresas
        companies = sb.table("companies").select("company_id, name").execute()
        result["companies_count"] = len(companies.data) if companies.data else 0
        result["success"] = True
        
        print(f"  ✅ Conexión exitosa")
        print(f"     🏢 Empresas en SGCA: {result['companies_count']}")
        
        if companies.data:
            for c in companies.data[:5]:
                print(f"        - {c['name']} ({c['company_id'][:8]}...)")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"  ❌ Error: {e}")
    
    return result


def test_bridge_sync(year: int, month: int, only: Optional[str] = None) -> Dict[str, Any]:
    """
    Test 3: Ejecutar bridge sync.
    """
    empresa_str = only if only else "todas las empresas"
    print_section(f"TEST 3: Bridge Sync ({year}-{month:02d}, {empresa_str})")
    
    result = {
        "test": "bridge_sync",
        "periodo": f"{year}-{month:02d}",
        "empresa": only,
        "success": False,
        "sync_result": None,
        "error": None,
    }
    
    if not BRIDGE_AVAILABLE:
        result["error"] = "Módulo Bridge no disponible"
        print(f"  ❌ {result['error']}")
        return result
    
    try:
        sync_result = sync_all(year, month, only, dry_run=False, sla_type="all")
        result["success"] = True
        result["sync_result"] = {
            "empresas": len(sync_result["empresas"]),
            "checks_creados": sync_result["totales"]["checks_creados"],
            "checks_actualizados": sync_result["totales"]["checks_actualizados"],
            "checks_autocerrados": sync_result["totales"]["checks_autocerrados"],
            "backlog_contabilizar": sync_result["totales"]["backlog_contabilizar"],
            "backlog_conciliar": sync_result["totales"]["backlog_conciliar"],
        }
        
        print(f"  ✅ Sync exitoso")
        print(f"     📊 Empresas procesadas: {result['sync_result']['empresas']}")
        print(f"     ➕ Checks creados: {result['sync_result']['checks_creados']}")
        print(f"     🔄 Checks actualizados: {result['sync_result']['checks_actualizados']}")
        print(f"     ✅ Checks autocerrados: {result['sync_result']['checks_autocerrados']}")
        print(f"     📝 Backlog contabilizar: {result['sync_result']['backlog_contabilizar']}")
        print(f"     🏦 Backlog conciliar: {result['sync_result']['backlog_conciliar']}")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"  ❌ Error: {e}")
    
    return result


def test_motor_execution() -> Dict[str, Any]:
    """
    Test 4: Ejecutar motor SGCA (daily_run.py) si está disponible.
    """
    print_section("TEST 4: Motor SGCA (daily_run.py)")
    
    result = {
        "test": "motor_execution",
        "success": False,
        "output": None,
        "error": None,
    }
    
    daily_run_path = os.path.join(SGCA_CORE_PATH, "jobs", "daily_run.py")
    
    if not os.path.exists(daily_run_path):
        result["error"] = f"daily_run.py no encontrado en {daily_run_path}"
        print(f"  ⚠️ {result['error']}")
        print(f"     Esto es esperado si sgca-core no está en la misma carpeta")
        return result
    
    try:
        print(f"  🔄 Ejecutando {daily_run_path}...")
        
        # Ejecutar el motor
        process = subprocess.run(
            [sys.executable, daily_run_path],
            cwd=SGCA_CORE_PATH,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        result["output"] = process.stdout + process.stderr
        
        if process.returncode == 0:
            result["success"] = True
            print(f"  ✅ Motor ejecutado exitosamente")
            # Mostrar últimas líneas
            lines = result["output"].strip().split("\n")[-10:]
            for line in lines:
                print(f"     {line}")
        else:
            result["error"] = f"Exit code: {process.returncode}"
            print(f"  ❌ Error: {result['error']}")
            print(f"     {process.stderr[:500]}")
            
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout (>120s)"
        print(f"  ❌ {result['error']}")
    except Exception as e:
        result["error"] = str(e)
        print(f"  ❌ Error: {e}")
    
    return result


def test_query_results(only: Optional[str] = None) -> Dict[str, Any]:
    """
    Test 5: Consultar resultados (checks y findings).
    """
    print_section("TEST 5: Consultar Resultados")
    
    result = {
        "test": "query_results",
        "success": False,
        "checks_by_company": {},
        "findings_by_company": {},
        "error": None,
    }
    
    if not BRIDGE_AVAILABLE:
        result["error"] = "Módulo Bridge no disponible"
        print(f"  ❌ {result['error']}")
        return result
    
    try:
        sb = get_supabase()
        
        # Obtener empresas
        companies_query = sb.table("companies").select("company_id, name")
        if only:
            companies_query = companies_query.ilike("name", f"%{only}%")
        companies = companies_query.execute()
        
        for company in (companies.data or []):
            company_id = company["company_id"]
            company_name = company["name"]
            
            # Contar checks
            checks = sb.table("expected_item_checks").select(
                "expected_item_code, is_completed, review_status"
            ).eq("company_id", company_id).execute()
            
            checks_data = checks.data or []
            total_checks = len(checks_data)
            completed_checks = sum(1 for c in checks_data if c.get("is_completed"))
            pending_checks = total_checks - completed_checks
            
            result["checks_by_company"][company_name] = {
                "total": total_checks,
                "completed": completed_checks,
                "pending": pending_checks,
            }
            
            # Contar findings OPEN
            findings = sb.table("findings").select(
                "finding_id, severity, status"
            ).eq("company_id", company_id).eq("status", "OPEN").execute()
            
            findings_data = findings.data or []
            
            result["findings_by_company"][company_name] = {
                "open": len(findings_data),
                "by_severity": {},
            }
            
            # Agrupar por severidad
            for f in findings_data:
                sev = f.get("severity", "UNKNOWN")
                if sev not in result["findings_by_company"][company_name]["by_severity"]:
                    result["findings_by_company"][company_name]["by_severity"][sev] = 0
                result["findings_by_company"][company_name]["by_severity"][sev] += 1
        
        result["success"] = True
        
        # Mostrar resultados
        print(f"\n  📋 EXPECTED_ITEM_CHECKS:")
        for company_name, data in result["checks_by_company"].items():
            print(f"\n     🏢 {company_name}:")
            print(f"        Total: {data['total']}")
            print(f"        ✅ Completados: {data['completed']}")
            print(f"        ❌ Pendientes: {data['pending']}")
        
        print(f"\n  🚨 FINDINGS OPEN:")
        for company_name, data in result["findings_by_company"].items():
            print(f"\n     🏢 {company_name}:")
            print(f"        Total OPEN: {data['open']}")
            if data["by_severity"]:
                for sev, count in data["by_severity"].items():
                    print(f"        {sev}: {count}")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"  ❌ Error: {e}")
    
    return result


def run_smoke_test(
    year: int,
    month: int,
    only: Optional[str] = None,
    skip_motor: bool = False
) -> Dict[str, Any]:
    """
    Ejecuta todos los tests del smoke test E2E.
    """
    print_header(f"SGCA SMOKE TEST E2E - {now_chile().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Período: {year}-{month:02d}")
    print(f"  Empresa: {only or 'TODAS'}")
    print(f"  Skip motor: {skip_motor}")
    
    results = {
        "timestamp": now_chile().isoformat(),
        "period": f"{year}-{month:02d}",
        "empresa": only,
        "tests": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
        }
    }
    
    # Test 1: Odoo
    test_empresas = [only] if only else list(DATABASES.keys())
    for db_alias in test_empresas:
        test_result = test_odoo_connection(db_alias)
        results["tests"].append(test_result)
        results["summary"]["total"] += 1
        if test_result["success"]:
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1
    
    # Test 2: Supabase
    test_result = test_supabase_connection()
    results["tests"].append(test_result)
    results["summary"]["total"] += 1
    if test_result["success"]:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1
    
    # Test 3: Bridge sync
    test_result = test_bridge_sync(year, month, only)
    results["tests"].append(test_result)
    results["summary"]["total"] += 1
    if test_result["success"]:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1
    
    # Test 4: Motor (opcional)
    if not skip_motor:
        test_result = test_motor_execution()
        results["tests"].append(test_result)
        results["summary"]["total"] += 1
        if test_result["success"]:
            results["summary"]["passed"] += 1
        elif test_result.get("error", "").startswith("daily_run.py no encontrado"):
            # No contar como fallo si el motor no está disponible
            pass
        else:
            results["summary"]["failed"] += 1
    
    # Test 5: Query results
    test_result = test_query_results(only)
    results["tests"].append(test_result)
    results["summary"]["total"] += 1
    if test_result["success"]:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1
    
    # Resumen final
    print_header("RESUMEN SMOKE TEST")
    print(f"  Tests ejecutados: {results['summary']['total']}")
    print(f"  ✅ Passed: {results['summary']['passed']}")
    print(f"  ❌ Failed: {results['summary']['failed']}")
    
    if results["summary"]["failed"] == 0:
        print(f"\n  🎉 TODOS LOS TESTS PASARON")
    else:
        print(f"\n  ⚠️ HAY TESTS FALLIDOS")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Smoke Test E2E para SGCA + FactorIT'
    )
    parser.add_argument(
        '--period',
        type=str,
        help='Período YYYY-MM (default: mes actual)',
        default=None
    )
    parser.add_argument(
        '--only',
        type=str,
        choices=['FactorIT', 'FactorIT2'],
        help='Solo probar esta empresa',
        default=None
    )
    parser.add_argument(
        '--skip-motor',
        action='store_true',
        help='No ejecutar daily_run.py'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output en JSON'
    )
    
    args = parser.parse_args()
    
    # Parsear período
    if args.period:
        try:
            parts = args.period.split('-')
            year = int(parts[0])
            month = int(parts[1])
        except:
            print(f"Error: período inválido '{args.period}'. Usar formato YYYY-MM")
            sys.exit(1)
    else:
        today = today_chile()
        year = today.year
        month = today.month
    
    # Ejecutar smoke test
    try:
        results = run_smoke_test(year, month, args.only, args.skip_motor)
        
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        
        # Exit code basado en fallos
        sys.exit(1 if results["summary"]["failed"] > 0 else 0)
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()







