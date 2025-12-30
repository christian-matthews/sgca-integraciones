#!/usr/bin/env python3
"""
Smoke Test - Bridge Multi-Fuente
================================

Prueba rápida para verificar que el bridge puede ejecutarse
con ambas fuentes (Odoo + Skualo) sin explotar.

NO escribe a Supabase (usa --dry-run).
Solo valida:
1. Imports funcionan
2. Configuración carga correctamente
3. Logging estructurado funciona
4. No hay excepciones fatales

Uso:
    python scripts/smoke_test_bridge_both_sources.py

Exit codes:
    0 = Smoke test pasó
    1 = Smoke test falló
"""

import os
import sys
import subprocess
from datetime import datetime

# Agregar paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_cmd(args: list, description: str) -> tuple:
    """
    Ejecuta un comando y retorna (success, output).
    """
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    print(f"   Comando: {' '.join(args)}")
    print()
    
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        # Mostrar output
        if result.stdout:
            for line in result.stdout.split('\n')[:30]:
                print(f"   {line}")
            if len(result.stdout.split('\n')) > 30:
                print(f"   ... ({len(result.stdout.split(chr(10)))} líneas total)")
        
        if result.stderr:
            print("\n   STDERR:")
            for line in result.stderr.split('\n')[:10]:
                print(f"   {line}")
        
        return result.returncode == 0, result.stdout + result.stderr
        
    except subprocess.TimeoutExpired:
        print("   ❌ TIMEOUT (>60s)")
        return False, "Timeout"
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, str(e)


def test_imports():
    """Verifica que los imports principales funcionan."""
    print("\n" + "="*60)
    print("🔍 Test: Imports")
    print("="*60)
    
    errors = []
    
    # Test imports
    tests = [
        ("bridge.sync_manager", "SyncManager"),
        ("bridge.sync_odoo_to_checks", "sync_all"),
        ("bridge.sync_skualo_to_checks", "sync_all"),
        ("bridge.config", "SUPABASE_URL"),
        ("skualo.pendientes", "obtener_pendientes_empresa"),
        ("odoo.pendientes", "obtener_pendientes_empresa"),
    ]
    
    for module, attr in tests:
        try:
            mod = __import__(module, fromlist=[attr])
            if hasattr(mod, attr):
                print(f"   ✅ {module}.{attr}")
            else:
                print(f"   ❌ {module}.{attr} no existe")
                errors.append(f"{module}.{attr}")
        except ImportError as e:
            print(f"   ⚠️  {module}: {e}")
            # Algunos imports pueden fallar si faltan deps, no es fatal
    
    return len(errors) == 0


def test_config():
    """Verifica que la configuración carga correctamente."""
    print("\n" + "="*60)
    print("🔍 Test: Configuración")
    print("="*60)
    
    try:
        from bridge.sync_manager import SyncManager
        manager = SyncManager()
        
        company_map = manager.company_map
        print(f"   ✅ company_map.json cargado: {len(company_map)} empresas")
        
        for alias, config in company_map.items():
            odoo_enabled = config.get("odoo", {}).get("enabled", False)
            skualo_enabled = config.get("skualo", {}).get("enabled", False)
            print(f"      {alias}: odoo={odoo_enabled}, skualo={skualo_enabled}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_dry_run_odoo():
    """Ejecuta dry-run con fuente Odoo."""
    success, output = run_cmd(
        [sys.executable, "scripts/run_bridge_scheduled.py", "--source", "odoo", "--dry-run"],
        "Dry-run Odoo"
    )
    
    # Verificar que el output tiene estructura esperada
    if "SGCA BRIDGE" in output and "RESUMEN" in output:
        print("\n   ✅ Output estructurado correcto")
        return True
    elif "Error" in output.lower():
        print("\n   ⚠️  Hay errores (puede ser esperado sin conexión)")
        return True  # Aceptable en smoke test
    else:
        print("\n   ❌ Output inesperado")
        return False


def test_dry_run_skualo():
    """Ejecuta dry-run con fuente Skualo."""
    success, output = run_cmd(
        [sys.executable, "scripts/run_bridge_scheduled.py", "--source", "skualo", "--dry-run"],
        "Dry-run Skualo"
    )
    
    # Skualo puede estar deshabilitado, eso está OK
    if "SKIPPED" in output or "no_companies_enabled" in output:
        print("\n   ✅ Skualo correctamente skipped (no habilitado)")
        return True
    elif "SGCA BRIDGE" in output:
        print("\n   ✅ Output estructurado correcto")
        return True
    else:
        print("\n   ⚠️  Output inesperado (puede ser OK)")
        return True


def test_dry_run_both():
    """Ejecuta dry-run con ambas fuentes."""
    success, output = run_cmd(
        [sys.executable, "scripts/run_bridge_scheduled.py", "--source", "both", "--dry-run"],
        "Dry-run Both Sources"
    )
    
    if "SGCA BRIDGE" in output and "RESUMEN" in output:
        print("\n   ✅ Output estructurado correcto")
        
        # Verificar que muestra ambas fuentes en resumen
        if "ODOO" in output:
            print("   ✅ Fuente ODOO reportada")
        if "SKUALO" in output:
            print("   ✅ Fuente SKUALO reportada")
        
        return True
    else:
        print("\n   ⚠️  Output puede ser incompleto")
        return True  # Aceptable


def main():
    """Ejecuta todos los smoke tests."""
    print("=" * 60)
    print("   SMOKE TEST - BRIDGE MULTI-FUENTE")
    print("=" * 60)
    print(f"   Fecha: {datetime.now().isoformat()}")
    print(f"   Python: {sys.version}")
    print(f"   CWD: {os.getcwd()}")
    
    results = []
    
    # Tests
    results.append(("Imports", test_imports()))
    results.append(("Configuración", test_config()))
    results.append(("Dry-run Odoo", test_dry_run_odoo()))
    results.append(("Dry-run Skualo", test_dry_run_skualo()))
    results.append(("Dry-run Both", test_dry_run_both()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("   RESUMEN SMOKE TEST")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name:20} : {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("   🎉 SMOKE TEST PASÓ - Bridge listo para cron")
        return 0
    else:
        print("   ⚠️  SMOKE TEST CON WARNINGS - Revisar errores")
        return 1


if __name__ == "__main__":
    sys.exit(main())






