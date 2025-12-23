#!/usr/bin/env python3
"""
SGCA Bridge - Ejecución Programada Multi-Fuente
================================================

Wrapper para ejecutar el bridge en horarios programados.
Soporta múltiples fuentes: Odoo y Skualo.
Diseñado para correr como cron job en Render.

HORARIOS:
- Odoo/Skualo actualizan pendientes: 07:00 / 19:00 (America/Santiago)
- Bridge SGCA debe correr: 07:30 / 19:30 (America/Santiago)

FUNCIÓN:
- Determina período automáticamente (YYYY-MM actual)
- Ejecuta sync para fuentes habilitadas (Odoo, Skualo o ambas)
- Logging estructurado con duración
- Exit code != 0 si falla

VARIABLES DE ENTORNO:
- BRIDGE_ENABLE_ODOO=true/false (default: true)
- BRIDGE_ENABLE_SKUALO=true/false (default: true)

USO:
    python scripts/run_bridge_scheduled.py
    python scripts/run_bridge_scheduled.py --source both
    python scripts/run_bridge_scheduled.py --source odoo --only FactorIT
    python scripts/run_bridge_scheduled.py --source skualo --dry-run

RENDER CRON:
    Comando: python scripts/run_bridge_scheduled.py
    Horarios: 07:30 / 19:30 America/Santiago
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Optional

# Agregar paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Timezone
try:
    import zoneinfo
    TIMEZONE = zoneinfo.ZoneInfo("America/Santiago")
except ImportError:
    import pytz
    TIMEZONE = pytz.timezone("America/Santiago")


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('bridge.scheduled')


def now_chile() -> datetime:
    """Retorna datetime actual en zona horaria Chile."""
    return datetime.now(TIMEZONE)


def get_current_period() -> tuple:
    """Retorna (year, month) del período actual."""
    now = now_chile()
    return now.year, now.month


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def run_bridge(
    source: str = "both",
    only: Optional[str] = None,
    dry_run: bool = False,
    sla_type: str = "all"
) -> int:
    """
    Ejecuta el bridge para sincronizar pendientes → SGCA.
    
    Args:
        source: Fuente de datos ("odoo", "skualo", "both")
        only: Si se especifica, solo esa empresa ('FactorIT' o 'FactorIT2')
        dry_run: Si True, no escribe a Supabase
        sla_type: Tipo de SLA ("all", "weekly", "monthly")
    
    Returns:
        Exit code (0 = éxito, 1 = error)
    """
    start_time = now_chile()
    year, month = get_current_period()
    period = f"{year}-{month:02d}"
    
    # Verificar habilitación por variables de entorno
    odoo_enabled = os.getenv("BRIDGE_ENABLE_ODOO", "true").lower() in ("true", "1", "yes")
    skualo_enabled = os.getenv("BRIDGE_ENABLE_SKUALO", "true").lower() in ("true", "1", "yes")
    
    logger.info("=" * 70)
    logger.info("SGCA BRIDGE - EJECUCIÓN PROGRAMADA MULTI-FUENTE")
    logger.info("=" * 70)
    logger.info(f"  Start time : {start_time.isoformat()}")
    logger.info(f"  Timezone   : America/Santiago")
    logger.info(f"  Period     : {period}")
    logger.info(f"  Source     : {source}")
    logger.info(f"  Empresas   : {only or 'todas'}")
    logger.info(f"  SLA Type   : {sla_type}")
    logger.info(f"  Dry Run    : {dry_run}")
    logger.info(f"  Odoo enabled (env)   : {odoo_enabled}")
    logger.info(f"  Skualo enabled (env) : {skualo_enabled}")
    logger.info("=" * 70)
    
    # Import sync manager
    try:
        from bridge.sync_manager import get_sync_manager
    except ImportError as e:
        logger.error(f"Error importando sync_manager: {e}")
        logger.error("Asegúrate de ejecutar desde el directorio sgca-integraciones")
        return 1
    
    # Ejecutar sync
    try:
        manager = get_sync_manager()
        result = manager.sync_all(
            source=source,
            year=year,
            month=month,
            only=only,
            dry_run=dry_run,
            sla_type=sla_type
        )
    except Exception as e:
        logger.error(f"Error fatal en sync: {e}")
        return 1
    
    # Resumen final
    end_time = now_chile()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("\n" + "=" * 70)
    logger.info("RESUMEN FINAL")
    logger.info("=" * 70)
    
    totales = result.get("totales", {})
    
    # Resumen por fuente
    sources_result = result.get("sources", {})
    for src_name, src_data in sources_result.items():
        if src_data.get("skipped"):
            logger.info(f"  {src_name.upper():10} : SKIPPED ({src_data.get('reason', 'unknown')})")
        else:
            src_empresas = len(src_data.get("empresas", []))
            src_success = "✅" if src_data.get("success") else "❌"
            logger.info(f"  {src_name.upper():10} : {src_success} ({src_empresas} empresas)")
    
    logger.info("-" * 40)
    logger.info(f"  Período        : {period}")
    logger.info(f"  Empresas       : {result.get('empresas_procesadas', 0)}")
    logger.info(f"  Con error      : {result.get('empresas_con_error', 0)}")
    logger.info(f"  Checks creados      : {totales.get('checks_creados', 0)}")
    logger.info(f"  Checks actualizados : {totales.get('checks_actualizados', 0)}")
    logger.info(f"  Checks autocerrados : {totales.get('checks_autocerrados', 0)}")
    logger.info(f"  Checks reabiertos   : {totales.get('checks_reabiertos', 0)}")
    logger.info(f"  Duración       : {duration:.2f}s")
    
    exit_code = 0 if result.get("success", False) else 1
    logger.info(f"  Exit code      : {exit_code}")
    logger.info("=" * 70)
    
    if dry_run:
        logger.info("⚠️  DRY-RUN: No se escribió nada a Supabase")
    
    return exit_code


def main():
    parser = argparse.ArgumentParser(
        description='SGCA Bridge - Ejecución Programada Multi-Fuente',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/run_bridge_scheduled.py                         # Sync ambas fuentes
  python scripts/run_bridge_scheduled.py --source odoo           # Solo Odoo
  python scripts/run_bridge_scheduled.py --source skualo         # Solo Skualo
  python scripts/run_bridge_scheduled.py --source both --dry-run # Ambas, sin escribir
  python scripts/run_bridge_scheduled.py --only FactorIT         # Solo una empresa

Variables de entorno:
  BRIDGE_ENABLE_ODOO=true/false   (default: true)
  BRIDGE_ENABLE_SKUALO=true/false (default: true)
        """
    )
    parser.add_argument(
        '--source',
        type=str,
        choices=['odoo', 'skualo', 'both'],
        help='Fuente de datos (default: both)',
        default='both'
    )
    parser.add_argument(
        '--only',
        type=str,
        choices=['FactorIT', 'FactorIT2'],
        help='Solo sincronizar esta empresa',
        default=None
    )
    parser.add_argument(
        '--sla-type',
        type=str,
        choices=['all', 'weekly', 'monthly'],
        help='Tipo de SLA a procesar (default: all)',
        default='all'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='No escribir a Supabase, solo mostrar qué haría'
    )
    
    args = parser.parse_args()
    
    exit_code = run_bridge(
        source=args.source,
        only=args.only,
        dry_run=args.dry_run,
        sla_type=args.sla_type
    )
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
