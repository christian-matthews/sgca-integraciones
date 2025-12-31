#!/usr/bin/env python3
"""
SGCA Bridge - Sync Skualo to Checks
===================================

Sincroniza pendientes de Skualo hacia expected_item_checks en Supabase.
Equivalente a sync_odoo_to_checks.py pero para la fuente Skualo.

MAPEO DE PENDIENTES → CHECKS:
- pendientes_sii → REVISION_FACTURAS_PROVEEDOR
- pendientes_contabilizar → DIGITACION_FACTURAS
- pendientes_conciliar → CONCILIACION_BANCARIA

AUTOCIERRE:
- Si backlog == 0 → cierra check (is_completed=true)
- Si backlog > 0 → reabre (is_completed=false)

Uso:
    python -m bridge.sync_skualo_to_checks --period 2025-01 --dry-run
    python -m bridge.sync_skualo_to_checks

NO modifica sgca-core. Solo escribe a Supabase.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import uuid

# Agregar paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Imports locales
from skualo.pendientes import obtener_pendientes_empresa
from bridge.config import (
    SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY,
    CHECK_SEMANAL_CONTABILIZACION, CHECK_SEMANAL_CONCILIACION,
    CHECK_MENSUAL_CONTABILIZACION, CHECK_MENSUAL_CONCILIACION,
    CHECK_REVISION_FACTURAS, CHECK_DIGITACION_FACTURAS, CHECK_CONCILIACION_BANCARIA,
)
from bridge.sla_calculator import (
    today_chile, now_chile,
    get_week_bounds, get_sla_semanal_deadline,
    get_sla_mensual_deadline, get_last_day_of_month,
)

# Supabase
from supabase import create_client, Client


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

class StructuredLogger:
    """Logger estructurado para sync operations."""
    
    def __init__(self, name: str = 'bridge.skualo'):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.handlers = [handler]
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
    
    def info(self, msg: str, **kwargs):
        if kwargs:
            extra = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
            self.logger.info(f"{msg} | {extra}")
        else:
            self.logger.info(msg)
    
    def warning(self, msg: str, **kwargs):
        if kwargs:
            extra = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
            self.logger.warning(f"{msg} | {extra}")
        else:
            self.logger.warning(msg)
    
    def error(self, msg: str, **kwargs):
        if kwargs:
            extra = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
            self.logger.error(f"{msg} | {extra}")
        else:
            self.logger.error(msg)


logger = StructuredLogger('bridge.skualo')


# ═══════════════════════════════════════════════════════════════════════════════
# COMPANY MAP
# ═══════════════════════════════════════════════════════════════════════════════

def load_company_map() -> Dict[str, Dict]:
    """Carga company_map.json."""
    map_path = os.path.join(os.path.dirname(__file__), 'company_map.json')
    try:
        with open(map_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# SUPABASE CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

_sb_client: Optional[Client] = None

def get_supabase() -> Client:
    """Retorna cliente Supabase singleton."""
    global _sb_client
    if _sb_client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY requeridos")
        _sb_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _sb_client


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS (reutilizados de sync_odoo_to_checks)
# ═══════════════════════════════════════════════════════════════════════════════

def get_company_by_id(sb: Client, company_id: str) -> Optional[Dict]:
    """Busca empresa por ID."""
    try:
        result = sb.table("companies").select("*").eq("company_id", company_id).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception:
        return None


def get_or_create_period(sb: Client, company_id: str, year: int, month: int) -> Optional[str]:
    """Obtiene o crea período mensual."""
    period_start = date(year, month, 1)
    period_end = get_last_day_of_month(year, month)
    
    try:
        result = sb.table("periods").select("period_id").eq(
            "company_id", company_id
        ).eq("period_start", period_start.isoformat()).limit(1).execute()
        
        if result.data:
            return result.data[0]["period_id"]
        
        new_period = {
            "period_id": str(uuid.uuid4()),
            "company_id": company_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "is_closed": False,
        }
        
        insert_result = sb.table("periods").insert(new_period).execute()
        return insert_result.data[0]["period_id"] if insert_result.data else None
        
    except Exception as e:
        logger.error(f"Error con período: {e}")
        return None


def get_business_calendar(sb: Client, year: int, month: int) -> List[Dict]:
    """Obtiene calendario de días hábiles."""
    try:
        start = date(year, month, 1)
        end = get_last_day_of_month(year, month) + timedelta(days=10)
        
        result = sb.table("business_calendar_cl").select("day, is_business_day").gte(
            "day", start.isoformat()
        ).lte("day", end.isoformat()).execute()
        
        return result.data or []
    except Exception:
        return []


def ensure_expected_item(sb: Client, code: str, name: str, role: str = "CONTADOR") -> bool:
    """Asegura que existe el expected_item."""
    try:
        existing = sb.table("expected_items").select("expected_item_code").eq(
            "expected_item_code", code
        ).limit(1).execute()
        
        if existing.data:
            return True
        
        sb.table("expected_items").insert({
            "expected_item_code": code,
            "name": name,
            "weight": "MEDIUM",
            "default_responsible_role": role,
            "active": True,
        }).execute()
        return True
    except Exception:
        return False


def upsert_check(
    sb: Client,
    company_id: str,
    period_id: str,
    expected_item_code: str,
    due_at: datetime,
    is_completed: bool = False,
    review_status: str = "PENDING",
    responsible_role: str = "CONTADOR",
    dry_run: bool = False
) -> Dict[str, Any]:
    """UPSERT de expected_item_check con autocierre/reapertura."""
    try:
        existing = sb.table("expected_item_checks").select("*").eq(
            "company_id", company_id
        ).eq("period_id", period_id).eq(
            "expected_item_code", expected_item_code
        ).limit(1).execute()
        
        grace_until = due_at
        
        if existing.data:
            check = existing.data[0]
            check_id = check["expected_item_check_id"]
            old_completed = check.get("is_completed", False)
            
            if old_completed and not is_completed:
                action = "reopened"
                update_data = {"is_completed": False, "review_status": "PENDING", "completed_at": None}
            elif not old_completed and is_completed:
                action = "closed"
                update_data = {"is_completed": True, "review_status": "APPROVED", "completed_at": now_chile().isoformat()}
            elif check.get("review_status") != review_status or check.get("is_completed") != is_completed:
                action = "updated"
                update_data = {"is_completed": is_completed, "review_status": review_status}
                if is_completed:
                    update_data["completed_at"] = now_chile().isoformat()
            else:
                return {"action": "unchanged", "check_id": check_id}
            
            if dry_run:
                return {"action": f"would_{action}", "check_id": check_id}
            
            sb.table("expected_item_checks").update(update_data).eq(
                "expected_item_check_id", check_id
            ).execute()
            
            return {"action": action, "check_id": check_id}
        
        # Crear nuevo
        if dry_run:
            return {"action": "would_create", "check_id": None}
        
        new_check = {
            "expected_item_check_id": str(uuid.uuid4()),
            "company_id": company_id,
            "period_id": period_id,
            "expected_item_code": expected_item_code,
            "stage_code": "OPERATING",
            "responsible_role": responsible_role,
            "due_at": due_at.isoformat(),
            "grace_until": grace_until.isoformat(),
            "is_completed": is_completed,
            "review_status": review_status,
            "item_weight": "MEDIUM",
        }
        
        if is_completed:
            new_check["completed_at"] = now_chile().isoformat()
        
        result = sb.table("expected_item_checks").insert(new_check).execute()
        
        if result.data:
            return {"action": "created", "check_id": result.data[0]["expected_item_check_id"]}
        
        return {"action": "error", "check_id": None}
        
    except Exception as e:
        return {"action": "error", "error": str(e)}


def insert_backlog_snapshot(
    sb: Client,
    company_id: str,
    db_alias: str,
    period: str,
    sii_count: int,
    contabilizar_count: int,
    conciliar_count: int,
    dry_run: bool = False
) -> bool:
    """Inserta snapshot de backlog."""
    snapshot = {
        "company_id": company_id,
        "period": period,
        "captured_at": now_chile().isoformat(),
        "sii_count": sii_count,
        "contabilizar_count": contabilizar_count,
        "conciliar_count": conciliar_count,
        "source": "skualo",
        "db_alias": db_alias,
    }
    
    if dry_run:
        return True
    
    try:
        sb.table("erp_backlog_snapshots").insert(snapshot).execute()
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# SYNC LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def _update_summary(summary: Dict, result: Dict):
    """Actualiza contadores del resumen."""
    action = result.get("action", "")
    if action == "created":
        summary["checks_creados"] += 1
    elif action == "updated":
        summary["checks_actualizados"] += 1
    elif action == "closed":
        summary["checks_autocerrados"] += 1
    elif action == "reopened":
        summary["checks_reabiertos"] += 1


def sync_empresa(
    sb: Client,
    db_alias: str,
    year: int,
    month: int,
    company_map: Dict,
    dry_run: bool = False,
    sla_type: str = "all"
) -> Dict[str, Any]:
    """
    Sincroniza una empresa desde Skualo hacia SGCA.
    
    Args:
        sb: Cliente Supabase
        db_alias: Alias de empresa
        year: Año
        month: Mes
        company_map: Mapeo de empresas
        dry_run: Si True, no escribe
        sla_type: Tipo de SLA
    
    Returns:
        Resumen de la sincronización
    """
    period_str = f"{year}-{month:02d}"
    
    logger.info(f"\n{'='*60}")
    logger.info(f"SYNC_SKUALO_START", db_alias=db_alias, period=period_str)
    logger.info(f"{'='*60}")
    
    summary = {
        "empresa": db_alias,
        "source": "skualo",
        "company_id": None,
        "periodo": period_str,
        "backlog_sii": 0,
        "backlog_contabilizar": 0,
        "backlog_conciliar": 0,
        "checks_creados": 0,
        "checks_actualizados": 0,
        "checks_autocerrados": 0,
        "checks_reabiertos": 0,
        "snapshot_insertado": False,
        "errors": [],
    }
    
    # Obtener config de Skualo para esta empresa
    empresa_config = company_map.get(db_alias, {})
    skualo_config = empresa_config.get("skualo", {})
    
    if not skualo_config.get("enabled"):
        logger.info(f"  Skualo no habilitado para {db_alias}")
        return summary
    
    skualo_rut = skualo_config.get("rut")
    if not skualo_rut:
        summary["errors"].append(f"RUT de Skualo no configurado para {db_alias}")
        return summary
    
    # 1. Obtener pendientes de Skualo
    try:
        pendientes = obtener_pendientes_empresa(skualo_rut)
    except Exception as e:
        summary["errors"].append(f"Error Skualo: {e}")
        logger.error(f"Error obteniendo pendientes de Skualo: {e}")
        return summary
    
    summary["backlog_sii"] = pendientes["pendientes_sii"]["cantidad"]
    summary["backlog_contabilizar"] = pendientes["pendientes_contabilizar"]["cantidad"]
    summary["backlog_conciliar"] = pendientes["pendientes_conciliar"]["cantidad"]
    
    logger.info(
        f"  📊 Backlog Skualo",
        sii=summary["backlog_sii"],
        contabilizar=summary["backlog_contabilizar"],
        conciliar=summary["backlog_conciliar"]
    )
    
    # 2. Obtener empresa en SGCA
    company_id = empresa_config.get("company_id")
    if not company_id:
        summary["errors"].append(f"company_id no configurado para {db_alias}")
        return summary
    
    company = get_company_by_id(sb, company_id)
    if not company:
        summary["errors"].append(f"Empresa no encontrada en SGCA: {company_id}")
        return summary
    
    summary["company_id"] = company_id
    
    # 3. Obtener/crear período
    period_id = get_or_create_period(sb, company_id, year, month)
    if not period_id:
        summary["errors"].append("No se pudo crear período")
        return summary
    
    # 4. Calcular deadline mensual
    calendar_data = get_business_calendar(sb, year, month)
    due_at_mensual = get_sla_mensual_deadline(year, month, calendar_data)
    
    # 5. Determinar estados de autocierre
    is_completed_cont = summary["backlog_contabilizar"] == 0
    is_completed_conc = summary["backlog_conciliar"] == 0
    review_status_cont = "APPROVED" if is_completed_cont else "PENDING"
    review_status_conc = "APPROVED" if is_completed_conc else "PENDING"
    
    # 6. Asegurar expected_items
    ensure_expected_item(sb, CHECK_REVISION_FACTURAS, "Revisión Facturas Proveedor")
    ensure_expected_item(sb, CHECK_DIGITACION_FACTURAS, "Digitación Facturas")
    ensure_expected_item(sb, CHECK_CONCILIACION_BANCARIA, "Conciliación Bancaria")
    ensure_expected_item(sb, CHECK_MENSUAL_CONTABILIZACION, "Cierre Mensual Contabilización")
    ensure_expected_item(sb, CHECK_MENSUAL_CONCILIACION, "Cierre Mensual Conciliación")
    
    # 7. UPSERT checks agregados
    logger.info("\n  📋 CHECKS:")
    
    result = upsert_check(
        sb, company_id, period_id,
        CHECK_REVISION_FACTURAS,
        due_at_mensual,
        is_completed=summary["backlog_sii"] == 0,
        review_status="APPROVED" if summary["backlog_sii"] == 0 else "PENDING",
        dry_run=dry_run
    )
    _update_summary(summary, result)
    
    result = upsert_check(
        sb, company_id, period_id,
        CHECK_DIGITACION_FACTURAS,
        due_at_mensual,
        is_completed=is_completed_cont,
        review_status=review_status_cont,
        dry_run=dry_run
    )
    _update_summary(summary, result)
    
    result = upsert_check(
        sb, company_id, period_id,
        CHECK_CONCILIACION_BANCARIA,
        due_at_mensual,
        is_completed=is_completed_conc,
        review_status=review_status_conc,
        dry_run=dry_run
    )
    _update_summary(summary, result)
    
    # 8. SLA Mensual
    if sla_type in ("all", "monthly"):
        result = upsert_check(
            sb, company_id, period_id,
            CHECK_MENSUAL_CONTABILIZACION,
            due_at_mensual,
            is_completed=is_completed_cont,
            review_status=review_status_cont,
            dry_run=dry_run
        )
        _update_summary(summary, result)
        
        result = upsert_check(
            sb, company_id, period_id,
            CHECK_MENSUAL_CONCILIACION,
            due_at_mensual,
            is_completed=is_completed_conc,
            review_status=review_status_conc,
            dry_run=dry_run
        )
        _update_summary(summary, result)
    
    # 9. Snapshot
    summary["snapshot_insertado"] = insert_backlog_snapshot(
        sb, company_id, db_alias, period_str,
        summary["backlog_sii"],
        summary["backlog_contabilizar"],
        summary["backlog_conciliar"],
        dry_run=dry_run
    )
    
    logger.info(
        f"SYNC_SKUALO_COMPLETE",
        created=summary["checks_creados"],
        updated=summary["checks_actualizados"],
        closed=summary["checks_autocerrados"]
    )
    
    return summary


def sync_all(
    year: int,
    month: int,
    only: Optional[str] = None,
    dry_run: bool = False,
    sla_type: str = "all"
) -> Dict[str, Any]:
    """
    Sincroniza todas las empresas con Skualo habilitado.
    
    Args:
        year: Año
        month: Mes
        only: Empresa específica
        dry_run: Si True, no escribe
        sla_type: Tipo de SLA
    
    Returns:
        Resumen global
    """
    sb = get_supabase()
    company_map = load_company_map()
    
    # Filtrar empresas con Skualo habilitado
    if only:
        empresas = [only]
    else:
        empresas = [
            alias for alias, config in company_map.items()
            if config.get("skualo", {}).get("enabled")
        ]
    
    global_summary = {
        "fecha_sync": now_chile().isoformat(),
        "periodo": f"{year}-{month:02d}",
        "source": "skualo",
        "dry_run": dry_run,
        "empresas": [],
        "totales": {
            "backlog_sii": 0,
            "backlog_contabilizar": 0,
            "backlog_conciliar": 0,
            "checks_creados": 0,
            "checks_actualizados": 0,
            "checks_autocerrados": 0,
            "checks_reabiertos": 0,
        }
    }
    
    for db_alias in empresas:
        summary = sync_empresa(sb, db_alias, year, month, company_map, dry_run, sla_type)
        global_summary["empresas"].append(summary)
        
        for key in global_summary["totales"]:
            global_summary["totales"][key] += summary.get(key, 0)
    
    return global_summary


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Sincroniza Skualo → SGCA')
    parser.add_argument('--period', type=str, help='Período YYYY-MM')
    parser.add_argument('--only', type=str, help='Solo esta empresa')
    parser.add_argument('--dry-run', action='store_true', help='No escribir')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    if args.period:
        parts = args.period.split('-')
        year, month = int(parts[0]), int(parts[1])
    else:
        today = today_chile()
        year, month = today.year, today.month
    
    result = sync_all(year, month, args.only, args.dry_run)
    
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    
    total_errors = sum(len(e.get("errors", [])) for e in result["empresas"])
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == '__main__':
    main()







