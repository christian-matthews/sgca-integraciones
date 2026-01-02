#!/usr/bin/env python3
"""
SGCA Bridge - Sync Odoo to Checks
=================================

Sincroniza pendientes de Odoo hacia expected_item_checks en Supabase.

CHECKS CREADOS:
A) Checks agregados por categorías (siempre upsert, aunque count=0):
   - pendientes_sii → REVISION_FACTURAS_PROVEEDOR (responsible_role=CONTADOR)
   - pendientes_contabilizar → DIGITACION_FACTURAS (responsible_role=CONTADOR)
   - pendientes_conciliar → CONCILIACION_BANCARIA (responsible_role=CONTADOR)

B) SLA Semanal:
   - CIERRE_SEMANAL_CONTABILIZACION
   - CIERRE_SEMANAL_CONCILIACION
   - due_at = miércoles T+1 a las 18:00

C) SLA Mensual:
   - CIERRE_MENSUAL_CONTABILIZACION
   - CIERRE_MENSUAL_CONCILIACION
   - due_at = add_business_days(last_day_of_month, 3) a las 18:00

Sin gracia: grace_until = due_at

AUTOCIERRE:
- Si backlog contabilizar == 0 → cierra checks de contabilización (is_completed=true)
- Si backlog conciliar == 0 → cierra checks de conciliación (is_completed=true)
- Si backlog vuelve > 0 → reabre (is_completed=false)

MÉTRICA CONTINUA:
- Inserta snapshot en tabla erp_backlog_snapshots

Uso:
    python -m bridge.sync_odoo_to_checks --period 2025-01 --only FactorIT --dry-run
    python -m bridge.sync_odoo_to_checks --period 2025-01
    python -m bridge.sync_odoo_to_checks  # Usa mes actual

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
from odoo.pendientes import obtener_pendientes_empresa, DATABASES
from bridge.config import (
    SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY,
    GRACE_DAYS,
    CHECK_SEMANAL_CONTABILIZACION, CHECK_SEMANAL_CONCILIACION,
    CHECK_MENSUAL_CONTABILIZACION, CHECK_MENSUAL_CONCILIACION,
    CHECK_REVISION_FACTURAS, CHECK_DIGITACION_FACTURAS, CHECK_CONCILIACION_BANCARIA,
)
from bridge.sla_calculator import (
    today_chile, now_chile,
    get_week_bounds, get_sla_semanal_deadline,
    get_sla_mensual_deadline, get_period_code_monthly,
    get_period_code_weekly, get_last_day_of_month,
)

# Supabase
from supabase import create_client, Client


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING ESTRUCTURADO
# ═══════════════════════════════════════════════════════════════════════════════

class StructuredLogger:
    """Logger estructurado para sync operations."""
    
    def __init__(self, name: str = 'bridge.sync'):
        self.logger = logging.getLogger(name)
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
    
    def log_empresa_summary(self, summary: Dict):
        """Log estructurado para resumen de empresa."""
        self.info(
            "EMPRESA_SYNC_COMPLETE",
            db_alias=summary.get('empresa'),
            company_id=summary.get('company_id', '')[:8] + '...' if summary.get('company_id') else 'N/A',
            period=summary.get('periodo'),
            sii=summary.get('backlog_sii', 0),
            contabilizar=summary.get('backlog_contabilizar', 0),
            conciliar=summary.get('backlog_conciliar', 0),
            created=summary.get('checks_creados', 0),
            updated=summary.get('checks_actualizados', 0),
            closed=summary.get('checks_autocerrados', 0),
            reopened=summary.get('checks_reabiertos', 0)
        )
    
    def log_global_summary(self, global_summary: Dict):
        """Log estructurado para resumen global."""
        totales = global_summary.get('totales', {})
        self.info(
            "GLOBAL_SYNC_COMPLETE",
            empresas=len(global_summary.get('empresas', [])),
            total_sii=totales.get('backlog_sii', 0),
            total_contabilizar=totales.get('backlog_contabilizar', 0),
            total_conciliar=totales.get('backlog_conciliar', 0),
            total_created=totales.get('checks_creados', 0),
            total_updated=totales.get('checks_actualizados', 0),
            total_closed=totales.get('checks_autocerrados', 0),
            total_reopened=totales.get('checks_reabiertos', 0)
        )


logger = StructuredLogger('bridge.sync')


# ═══════════════════════════════════════════════════════════════════════════════
# COMPANY MAP
# ═══════════════════════════════════════════════════════════════════════════════

def load_company_map() -> Dict[str, Dict]:
    """
    Carga company_map.json.
    
    Returns:
        Dict: {db_alias: {tenant_id, company_id, nombre}}
    """
    map_path = os.path.join(os.path.dirname(__file__), 'company_map.json')
    try:
        with open(map_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"company_map.json no encontrado en {map_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parseando company_map.json: {e}")
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
            raise ValueError("SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY requeridos en .env")
        _sb_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _sb_client


# ═══════════════════════════════════════════════════════════════════════════════
# LOOKUP FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_company_by_id(sb: Client, company_id: str) -> Optional[Dict]:
    """Busca empresa por ID."""
    try:
        result = sb.table("companies").select("*").eq("company_id", company_id).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error buscando empresa por ID: {e}")
        return None


def get_company_by_name(sb: Client, name: str) -> Optional[Dict]:
    """Busca empresa por nombre (fallback si no hay company_id en map)."""
    try:
        result = sb.table("companies").select("*").ilike("name", f"%{name}%").limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error buscando empresa {name}: {e}")
        return None


def resolve_company(sb: Client, db_alias: str, company_map: Dict) -> Optional[Dict]:
    """
    Resuelve empresa usando company_map o búsqueda por nombre.
    
    Args:
        sb: Cliente Supabase
        db_alias: 'FactorIT' o 'FactorIT2'
        company_map: Contenido de company_map.json
    
    Returns:
        Dict con datos de la empresa o None
    """
    mapping = company_map.get(db_alias, {})
    
    # Intentar por company_id primero
    if mapping.get('company_id'):
        company = get_company_by_id(sb, mapping['company_id'])
        if company:
            return company
    
    # Fallback a búsqueda por nombre
    nombre = mapping.get('nombre') or DATABASES.get(db_alias, db_alias)
    return get_company_by_name(sb, nombre)


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
        
        # Crear nuevo
        new_period = {
            "period_id": str(uuid.uuid4()),
            "company_id": company_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "is_closed": False,
        }
        
        insert_result = sb.table("periods").insert(new_period).execute()
        if insert_result.data:
            logger.info(f"Período creado: {year}-{month:02d}")
            return insert_result.data[0]["period_id"]
        
        return None
        
    except Exception as e:
        logger.error(f"Error con período: {e}")
        return None


def get_or_create_period_weekly(sb: Client, company_id: str, week_start: date, week_end: date) -> Optional[str]:
    """Obtiene o crea período semanal."""
    try:
        result = sb.table("periods").select("period_id").eq(
            "company_id", company_id
        ).eq("period_start", week_start.isoformat()).eq(
            "period_end", week_end.isoformat()
        ).limit(1).execute()
        
        if result.data:
            return result.data[0]["period_id"]
        
        # Crear nuevo
        new_period = {
            "period_id": str(uuid.uuid4()),
            "company_id": company_id,
            "period_start": week_start.isoformat(),
            "period_end": week_end.isoformat(),
            "is_closed": False,
        }
        
        insert_result = sb.table("periods").insert(new_period).execute()
        if insert_result.data:
            logger.info(f"Período semanal creado: {week_start} - {week_end}")
            return insert_result.data[0]["period_id"]
        
        return None
        
    except Exception as e:
        logger.error(f"Error con período semanal: {e}")
        return None


def get_business_calendar(sb: Client, year: int, month: int) -> List[Dict]:
    """
    Obtiene calendario de días hábiles del core.
    Schema: day (DATE), is_business_day (BOOLEAN), note (TEXT)
    """
    try:
        start = date(year, month, 1)
        end = get_last_day_of_month(year, month) + timedelta(days=10)
        
        result = sb.table("business_calendar_cl").select("day, is_business_day").gte(
            "day", start.isoformat()
        ).lte("day", end.isoformat()).execute()
        
        # Ya viene en formato correcto
        return result.data or []
        
    except Exception as e:
        logger.warning(f"No se pudo obtener calendario: {e}")
        return []


def ensure_expected_item(sb: Client, code: str, name: str, role: str = "CONTADOR") -> bool:
    """Asegura que existe el expected_item en el catálogo."""
    try:
        existing = sb.table("expected_items").select("expected_item_code").eq(
            "expected_item_code", code
        ).limit(1).execute()
        
        if existing.data:
            return True
        
        new_item = {
            "expected_item_code": code,
            "name": name,
            "weight": "MEDIUM",
            "default_responsible_role": role,
            "active": True,
        }
        
        sb.table("expected_items").insert(new_item).execute()
        logger.info(f"Expected item creado: {code}")
        return True
        
    except Exception as e:
        logger.error(f"Error con expected_item {code}: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# UPSERT CHECK (con autocierre/reapertura)
# ═══════════════════════════════════════════════════════════════════════════════

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
    """
    UPSERT de expected_item_check con autocierre/reapertura.
    
    Clave determinística: (company_id, period_id, expected_item_code)
    
    Returns:
        Dict con resultado: {action: 'created'|'updated'|'closed'|'reopened'|'unchanged', check_id: ...}
    """
    try:
        existing = sb.table("expected_item_checks").select("*").eq(
            "company_id", company_id
        ).eq("period_id", period_id).eq(
            "expected_item_code", expected_item_code
        ).limit(1).execute()
        
        grace_until = due_at  # Sin gracia
        
        if existing.data:
            check = existing.data[0]
            check_id = check["expected_item_check_id"]
            old_completed = check.get("is_completed", False)
            
            # Determinar tipo de cambio
            if old_completed and not is_completed:
                # REAPERTURA: estaba cerrado, vuelve a abrirse
                action = "reopened"
                update_data = {
                    "is_completed": False,
                    "review_status": "PENDING",
                    "completed_at": None,
                }
            elif not old_completed and is_completed:
                # AUTOCIERRE: estaba abierto, se cierra
                action = "closed"
                update_data = {
                    "is_completed": True,
                    "review_status": "APPROVED",
                    "completed_at": now_chile().isoformat(),
                }
            elif check.get("review_status") != review_status or check.get("is_completed") != is_completed:
                # Actualización general
                action = "updated"
                update_data = {
                    "is_completed": is_completed,
                    "review_status": review_status,
                }
                if is_completed:
                    update_data["completed_at"] = now_chile().isoformat()
            else:
                return {"action": "unchanged", "check_id": check_id}
            
            if dry_run:
                logger.info(f"  [DRY-RUN] {action.upper()} {expected_item_code}")
                return {"action": f"would_{action}", "check_id": check_id}
            
            sb.table("expected_item_checks").update(update_data).eq(
                "expected_item_check_id", check_id
            ).execute()
            
            logger.info(f"  ✓ Check {action}: {expected_item_code}")
            return {"action": action, "check_id": check_id}
        
        # Crear nuevo
        if dry_run:
            logger.info(f"  [DRY-RUN] CREATE {expected_item_code} due_at={due_at.isoformat()}")
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
            check_id = result.data[0]["expected_item_check_id"]
            logger.info(f"  ✓ Check creado: {expected_item_code}")
            return {"action": "created", "check_id": check_id}
        
        return {"action": "error", "check_id": None}
        
    except Exception as e:
        logger.error(f"Error en upsert {expected_item_code}: {e}")
        return {"action": "error", "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# MÉTRICA CONTINUA - SNAPSHOT
# ═══════════════════════════════════════════════════════════════════════════════

def insert_backlog_snapshot(
    sb: Client,
    company_id: str,
    db_alias: str,
    period: str,
    sii_count: int,
    contabilizar_count: int,
    conciliar_count: int,
    sii_tacitos_count: int = 0,
    sii_tacitos_total: float = 0,
    dry_run: bool = False
) -> bool:
    """
    Inserta snapshot de backlog en erp_backlog_snapshots.
    
    Args:
        sb: Cliente Supabase
        company_id: ID de la empresa
        db_alias: Alias de BD Odoo (FactorIT, FactorIT2)
        period: Período YYYY-MM
        sii_count: Pendientes SII ACCIONABLES (< 8 días) - activan SLA
        contabilizar_count: Pendientes por contabilizar
        conciliar_count: Pendientes por conciliar
        sii_tacitos_count: Pendientes SII TÁCITOS (>= 8 días) - solo auditoría
        sii_tacitos_total: Monto total de tácitos
        dry_run: Si True, no escribe
    
    Returns:
        True si exitoso
    """
    snapshot = {
        "company_id": company_id,
        "period": period,
        "captured_at": now_chile().isoformat(),
        "sii_count": sii_count,  # Solo accionables - esto activa el SLA
        "contabilizar_count": contabilizar_count,
        "conciliar_count": conciliar_count,
        "source": "odoo",
        "db_alias": db_alias,
        # Raw contiene información adicional para auditoría
        "raw": {
            "sii_accionables": sii_count,
            "sii_tacitos": sii_tacitos_count,
            "sii_tacitos_monto": sii_tacitos_total,
            "nota": "sii_count solo cuenta accionables (<8 días). Tácitos son aceptados automáticamente por SII.",
        },
    }
    
    if dry_run:
        logger.info(f"  [DRY-RUN] INSERT snapshot", **{k: v for k, v in snapshot.items() if k != 'raw'})
        return True
    
    try:
        sb.table("erp_backlog_snapshots").insert(snapshot).execute()
        logger.info(f"  ✓ Snapshot insertado para {db_alias}")
        return True
    except Exception as e:
        logger.error(f"Error insertando snapshot: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# RESOLUCIÓN POR TEMPORALIDAD
# ═══════════════════════════════════════════════════════════════════════════════
# Los findings de semanas pasadas se resuelven si no hay tx pendientes
# anteriores a su fecha de corte (viernes de esa semana).
# ═══════════════════════════════════════════════════════════════════════════════

def get_cutoff_friday(finding_created_at: date) -> date:
    """
    Calcula el viernes de corte para un finding.
    
    El finding se crea el miércoles después del cierre semanal.
    El corte es el viernes anterior (fin de la semana operacional).
    
    Args:
        finding_created_at: Fecha de creación del finding
    
    Returns:
        Fecha del viernes de corte
    """
    # weekday(): 0=Lunes, 4=Viernes, 6=Domingo
    weekday = finding_created_at.weekday()
    
    if weekday == 4:  # Es viernes
        return finding_created_at
    elif weekday < 4:  # Lun-Jue → viernes de la semana anterior
        days_back = weekday + 3  # Lun=4, Mar=5, Mie=6, Jue=7... wait
        # Lun(0) → viernes anterior = -3
        # Mar(1) → viernes anterior = -4
        # Mie(2) → viernes anterior = -5
        # Jue(3) → viernes anterior = -6
        days_back = (weekday - 4) % 7
        if days_back == 0:
            days_back = 7
        return finding_created_at - timedelta(days=days_back)
    else:  # Sáb-Dom → viernes de esa semana
        # Sab(5) → viernes = -1
        # Dom(6) → viernes = -2
        days_back = weekday - 4
        return finding_created_at - timedelta(days=days_back)


def resolve_findings_by_cutoff(
    sb,
    company_id: str,
    pending_dates_conciliar: List[date],
    pending_dates_contabilizar: List[date],
    pending_dates_sii: List[date],
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Resuelve findings de semanas pasadas si no hay tx pendientes
    anteriores a su fecha de corte.
    
    Args:
        sb: Cliente Supabase
        company_id: ID de la empresa
        pending_dates_*: Listas de fechas de tx pendientes por categoría
        dry_run: Si True, no escribe
    
    Returns:
        Dict con resumen de resoluciones
    """
    result = {
        "findings_checked": 0,
        "findings_resolved": 0,
        "findings_still_open": 0,
        "details": []
    }
    
    # Mapeo de códigos de finding a fechas pendientes
    code_to_dates = {
        "CIERRE_SEMANAL_CONCILIACION": pending_dates_conciliar,
        "CIERRE_SEMANAL_CONTABILIZACION": pending_dates_contabilizar,
        "CIERRE_MENSUAL_CONCILIACION": pending_dates_conciliar,
        "CIERRE_MENSUAL_CONTABILIZACION": pending_dates_contabilizar,
        "CONCILIACION_BANCARIA": pending_dates_conciliar,
        "DIGITACION_FACTURAS": pending_dates_contabilizar,
        "REVISION_FACTURAS_PROVEEDOR": pending_dates_sii,
        "SII_FACTURAS_POR_APROBAR": pending_dates_sii,
    }
    
    try:
        # 1. Obtener findings OPEN de esta empresa
        findings_resp = sb.table("findings").select(
            "finding_id, expected_item_code, created_at"
        ).eq("company_id", company_id).eq("status", "OPEN").execute()
        
        findings = findings_resp.data or []
        
        # 2. Filtrar solo findings de cierre semanal/mensual (los que tienen temporalidad)
        temporal_codes = list(code_to_dates.keys())
        findings = [f for f in findings if f["expected_item_code"] in temporal_codes]
        
        # 3. Ordenar de más antiguo a más nuevo
        findings.sort(key=lambda f: f["created_at"])
        
        hoy = date.today()
        
        for finding in findings:
            result["findings_checked"] += 1
            
            finding_id = finding["finding_id"]
            code = finding["expected_item_code"]
            created_at_str = finding["created_at"]
            
            # Parsear fecha de creación
            try:
                created_at = date.fromisoformat(created_at_str[:10])
            except:
                continue
            
            # Calcular fecha de corte
            cutoff = get_cutoff_friday(created_at)
            
            # Si el corte es hoy o futuro, no resolver (es de la semana actual)
            if cutoff >= hoy:
                result["findings_still_open"] += 1
                continue
            
            # Obtener fechas pendientes para este tipo
            pending_dates = code_to_dates.get(code, [])
            
            # ¿Hay tx pendientes con fecha <= cutoff?
            tx_before_cutoff = [d for d in pending_dates if d <= cutoff]
            
            if len(tx_before_cutoff) == 0:
                # No hay tx pendientes de esa semana → Resolver
                if not dry_run:
                    # Actualizar finding a RESOLVED
                    sb.table("findings").update({
                        "status": "RESOLVED",
                        "resolved_at": now_chile().isoformat(),
                    }).eq("finding_id", finding_id).execute()
                    
                    # Crear evento de resolución
                    sb.table("finding_events").insert({
                        "finding_id": finding_id,
                        "event_type": "RESOLVED_BY_CUTOFF",
                        "payload": {
                            "cutoff_date": cutoff.isoformat(),
                            "pending_before_cutoff": 0,
                            "resolved_by": "bridge_temporal_resolution",
                        }
                    }).execute()
                
                result["findings_resolved"] += 1
                result["details"].append({
                    "finding_id": finding_id[:8],
                    "code": code,
                    "cutoff": cutoff.isoformat(),
                    "action": "resolved"
                })
                
                logger.info(f"  ✓ Finding resuelto por temporalidad: {code} (corte: {cutoff})")
            else:
                result["findings_still_open"] += 1
                result["details"].append({
                    "finding_id": finding_id[:8],
                    "code": code,
                    "cutoff": cutoff.isoformat(),
                    "pending_count": len(tx_before_cutoff),
                    "action": "kept_open"
                })
        
        return result
        
    except Exception as e:
        logger.error(f"Error en resolución por temporalidad: {e}")
        result["error"] = str(e)
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# SYNC LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def _get_weeks_in_month(year: int, month: int) -> List[tuple]:
    """
    Obtiene las semanas operacionales de un mes.
    Semana operacional: Lunes 00:00 → Viernes 18:00
    
    Returns:
        Lista de tuplas (lunes, viernes) para cada semana
    """
    weeks = []
    first_day = date(year, month, 1)
    last_day = get_last_day_of_month(year, month)
    
    current = first_day
    if current.weekday() != 0:
        current = current - timedelta(days=current.weekday())
    
    while current <= last_day:
        week_start = current
        week_end = current + timedelta(days=4)
        
        if week_end >= first_day and week_start <= last_day:
            weeks.append((week_start, week_end))
        
        current += timedelta(days=7)
    
    return weeks


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
    elif action == "unchanged":
        summary["checks_sin_cambio"] += 1


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
    Sincroniza una empresa desde Odoo hacia SGCA.
    
    Args:
        sb: Cliente Supabase
        db_alias: 'FactorIT' o 'FactorIT2'
        year: Año del período
        month: Mes del período
        company_map: Mapeo de empresas
        dry_run: Si True, no escribe
        sla_type: Tipo de SLA ("all", "weekly", "monthly")
    
    Returns:
        Resumen de la sincronización
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"SYNC_START", db_alias=db_alias, period=f"{year}-{month:02d}", sla_type=sla_type)
    logger.info(f"{'='*60}")
    
    period_str = f"{year}-{month:02d}"
    
    summary = {
        "empresa": db_alias,
        "company_id": None,
        "periodo": period_str,
        "backlog_sii": 0,
        "backlog_contabilizar": 0,
        "backlog_conciliar": 0,
        "checks_creados": 0,
        "checks_actualizados": 0,
        "checks_autocerrados": 0,
        "checks_reabiertos": 0,
        "checks_sin_cambio": 0,
        "snapshot_insertado": False,
        "errors": [],
    }
    
    # 1. Obtener pendientes de Odoo
    try:
        pendientes = obtener_pendientes_empresa(db_alias)
    except Exception as e:
        summary["errors"].append(f"Error Odoo: {e}")
        logger.error(f"Error obteniendo pendientes de Odoo: {e}")
        return summary
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONTADORES DE BACKLOG
    # ═══════════════════════════════════════════════════════════════════════════
    # Para SII: solo contamos los ACCIONABLES (< 8 días)
    # Los tácitos (>= 8 días) se guardan en raw para auditoría pero NO activan SLA
    # ═══════════════════════════════════════════════════════════════════════════
    
    sii_data = pendientes["pendientes_sii"]
    accionables = sii_data.get("accionables", {})
    tacitos = sii_data.get("tacitos_sin_revisar", {})
    
    # SLA solo cuenta accionables
    summary["backlog_sii"] = accionables.get("cantidad", sii_data.get("cantidad", 0))
    summary["backlog_contabilizar"] = pendientes["pendientes_contabilizar"]["cantidad"]
    summary["backlog_conciliar"] = pendientes["pendientes_conciliar"]["cantidad"]
    
    # Guardar tácitos para auditoría (no activan SLA)
    summary["sii_tacitos_count"] = tacitos.get("cantidad", 0)
    summary["sii_tacitos_total"] = tacitos.get("total", 0)
    
    logger.info(
        f"  📊 Backlog Odoo",
        sii_accionables=summary["backlog_sii"],
        sii_tacitos=summary["sii_tacitos_count"],
        contabilizar=summary["backlog_contabilizar"],
        conciliar=summary["backlog_conciliar"]
    )
    
    # 2. Resolver empresa en SGCA
    company = resolve_company(sb, db_alias, company_map)
    
    if not company:
        summary["errors"].append(f"Empresa no encontrada en SGCA: {db_alias}")
        logger.error(f"  ❌ Empresa no encontrada: {db_alias}")
        return summary
    
    company_id = company["company_id"]
    summary["company_id"] = company_id
    logger.info(f"  ✓ Empresa encontrada: {company['name']}", company_id=company_id[:8] + "...")
    
    # 3. Obtener/crear período mensual
    period_id = get_or_create_period(sb, company_id, year, month)
    if not period_id:
        summary["errors"].append("No se pudo crear período")
        return summary
    
    logger.info(f"  ✓ Período mensual", period_id=period_id[:8] + "...")
    
    # 4. Obtener calendario para cálculos de SLA
    calendar_data = get_business_calendar(sb, year, month)
    
    # 5. Calcular deadline mensual
    due_at_mensual = get_sla_mensual_deadline(year, month, calendar_data)
    logger.info(f"  📅 SLA Mensual deadline: {due_at_mensual.isoformat()}")
    
    # 6. Determinar estados de autocierre
    is_completed_cont = summary["backlog_contabilizar"] == 0
    is_completed_conc = summary["backlog_conciliar"] == 0
    
    review_status_cont = "APPROVED" if is_completed_cont else "PENDING"
    review_status_conc = "APPROVED" if is_completed_conc else "PENDING"
    
    logger.info(
        f"  📊 Autocierre status",
        contabilizacion="CERRADO" if is_completed_cont else "PENDIENTE",
        conciliacion="CERRADO" if is_completed_conc else "PENDIENTE"
    )
    
    # 7. Asegurar expected_items existen
    ensure_expected_item(sb, CHECK_REVISION_FACTURAS, "Revisión Facturas Proveedor", "CONTADOR")
    ensure_expected_item(sb, CHECK_DIGITACION_FACTURAS, "Digitación Facturas", "CONTADOR")
    ensure_expected_item(sb, CHECK_CONCILIACION_BANCARIA, "Conciliación Bancaria", "CONTADOR")
    ensure_expected_item(sb, CHECK_MENSUAL_CONTABILIZACION, "Cierre Mensual Contabilización", "CONTADOR")
    ensure_expected_item(sb, CHECK_MENSUAL_CONCILIACION, "Cierre Mensual Conciliación", "CONTADOR")
    ensure_expected_item(sb, CHECK_SEMANAL_CONTABILIZACION, "Cierre Semanal Contabilización", "CONTADOR")
    ensure_expected_item(sb, CHECK_SEMANAL_CONCILIACION, "Cierre Semanal Conciliación", "CONTADOR")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # A) CHECKS AGREGADOS POR CATEGORÍAS (siempre upsert, aunque count=0)
    # ═══════════════════════════════════════════════════════════════════════════
    logger.info("\n  📋 CHECKS AGREGADOS:")
    
    # REVISION_FACTURAS_PROVEEDOR (pendientes_sii)
    result = upsert_check(
        sb, company_id, period_id,
        CHECK_REVISION_FACTURAS,
        due_at=due_at_mensual,  # Mismo deadline que mensual
        is_completed=summary["backlog_sii"] == 0,
        review_status="APPROVED" if summary["backlog_sii"] == 0 else "PENDING",
        responsible_role="CONTADOR",
        dry_run=dry_run
    )
    _update_summary(summary, result)
    
    # DIGITACION_FACTURAS (pendientes_contabilizar)
    result = upsert_check(
        sb, company_id, period_id,
        CHECK_DIGITACION_FACTURAS,
        due_at=due_at_mensual,
        is_completed=is_completed_cont,
        review_status=review_status_cont,
        responsible_role="CONTADOR",
        dry_run=dry_run
    )
    _update_summary(summary, result)
    
    # CONCILIACION_BANCARIA (pendientes_conciliar)
    result = upsert_check(
        sb, company_id, period_id,
        CHECK_CONCILIACION_BANCARIA,
        due_at=due_at_mensual,
        is_completed=is_completed_conc,
        review_status=review_status_conc,
        responsible_role="CONTADOR",
        dry_run=dry_run
    )
    _update_summary(summary, result)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # B) SLA MENSUAL
    # ═══════════════════════════════════════════════════════════════════════════
    if sla_type in ("all", "monthly"):
        logger.info("\n  📋 SLA MENSUAL:")
        
        # CIERRE_MENSUAL_CONTABILIZACION
        result = upsert_check(
            sb, company_id, period_id,
            CHECK_MENSUAL_CONTABILIZACION,
            due_at_mensual,
            is_completed=is_completed_cont,
            review_status=review_status_cont,
            dry_run=dry_run
        )
        _update_summary(summary, result)
        
        # CIERRE_MENSUAL_CONCILIACION
        result = upsert_check(
            sb, company_id, period_id,
            CHECK_MENSUAL_CONCILIACION,
            due_at_mensual,
            is_completed=is_completed_conc,
            review_status=review_status_conc,
            dry_run=dry_run
        )
        _update_summary(summary, result)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # C) SLA SEMANAL
    # ═══════════════════════════════════════════════════════════════════════════
    if sla_type in ("all", "weekly"):
        weeks_in_month = _get_weeks_in_month(year, month)
        logger.info(f"\n  📋 SLA SEMANAL ({len(weeks_in_month)} semanas):")
        
        for week_start, week_end in weeks_in_month:
            due_at_semanal = get_sla_semanal_deadline(week_end)
            period_code_week = get_period_code_weekly(week_end)
            
            period_id_week = get_or_create_period_weekly(sb, company_id, week_start, week_end)
            if not period_id_week:
                logger.warning(f"  ⚠️ No se pudo crear período semanal {period_code_week}")
                continue
            
            logger.info(
                f"    Semana {period_code_week}",
                start=str(week_start),
                end=str(week_end),
                deadline=due_at_semanal.isoformat()
            )
            
            # CIERRE_SEMANAL_CONTABILIZACION
            result = upsert_check(
                sb, company_id, period_id_week,
                CHECK_SEMANAL_CONTABILIZACION,
                due_at_semanal,
                is_completed=is_completed_cont,
                review_status=review_status_cont,
                dry_run=dry_run
            )
            _update_summary(summary, result)
            
            # CIERRE_SEMANAL_CONCILIACION
            result = upsert_check(
                sb, company_id, period_id_week,
                CHECK_SEMANAL_CONCILIACION,
                due_at_semanal,
                is_completed=is_completed_conc,
                review_status=review_status_conc,
                dry_run=dry_run
            )
            _update_summary(summary, result)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # D) MÉTRICA CONTINUA - SNAPSHOT
    # ═══════════════════════════════════════════════════════════════════════════
    summary["snapshot_insertado"] = insert_backlog_snapshot(
        sb,
        company_id,
        db_alias,
        period_str,
        summary["backlog_sii"],  # Solo accionables
        summary["backlog_contabilizar"],
        summary["backlog_conciliar"],
        sii_tacitos_count=summary.get("sii_tacitos_count", 0),
        sii_tacitos_total=summary.get("sii_tacitos_total", 0),
        dry_run=dry_run
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # E) RESOLUCIÓN POR TEMPORALIDAD
    # ═══════════════════════════════════════════════════════════════════════════
    # Resuelve findings de semanas pasadas si no hay tx pendientes
    # anteriores a su fecha de corte.
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Extraer fechas de los pendientes
    def extract_dates(items: List[Dict]) -> List[date]:
        """Extrae fechas de una lista de items."""
        dates = []
        for item in items:
            fecha = item.get("fecha")
            if fecha:
                try:
                    if isinstance(fecha, date):
                        dates.append(fecha)
                    else:
                        dates.append(date.fromisoformat(str(fecha)[:10]))
                except:
                    pass
        return dates
    
    pending_dates_conciliar = extract_dates(
        pendientes.get("pendientes_conciliar", {}).get("movimientos", [])
    )
    pending_dates_contabilizar = extract_dates(
        pendientes.get("pendientes_contabilizar", {}).get("asientos", [])
    )
    
    # Para SII, combinar accionables y tácitos (ambos tienen fecha)
    sii_docs = []
    sii_data = pendientes.get("pendientes_sii", {})
    sii_docs.extend(sii_data.get("accionables", {}).get("documentos", []))
    sii_docs.extend(sii_data.get("tacitos_sin_revisar", {}).get("documentos", []))
    pending_dates_sii = extract_dates(sii_docs)
    
    logger.info(f"\n  📅 RESOLUCIÓN POR TEMPORALIDAD:")
    logger.info(f"     Fechas pendientes: conciliar={len(pending_dates_conciliar)}, contabilizar={len(pending_dates_contabilizar)}, sii={len(pending_dates_sii)}")
    
    resolution_result = resolve_findings_by_cutoff(
        sb,
        company_id,
        pending_dates_conciliar,
        pending_dates_contabilizar,
        pending_dates_sii,
        dry_run=dry_run
    )
    
    summary["temporal_resolution"] = resolution_result
    logger.info(f"     Findings revisados: {resolution_result['findings_checked']}")
    logger.info(f"     Findings resueltos: {resolution_result['findings_resolved']}")
    
    # Log resumen estructurado
    logger.log_empresa_summary(summary)
    
    return summary


def sync_all(
    year: int,
    month: int,
    only: Optional[str] = None,
    dry_run: bool = False,
    sla_type: str = "all"
) -> Dict[str, Any]:
    """
    Sincroniza todas las empresas (o una específica).
    
    Args:
        year: Año
        month: Mes
        only: Si se especifica, solo esa empresa
        dry_run: Si True, no escribe
        sla_type: Tipo de SLA ("all", "weekly", "monthly")
    
    Returns:
        Resumen global
    """
    sb = get_supabase()
    company_map = load_company_map()
    
    empresas = [only] if only else list(DATABASES.keys())
    
    global_summary = {
        "fecha_sync": now_chile().isoformat(),
        "periodo": f"{year}-{month:02d}",
        "sla_type": sla_type,
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
        if db_alias not in DATABASES:
            logger.warning(f"Empresa no reconocida: {db_alias}")
            continue
        
        summary = sync_empresa(sb, db_alias, year, month, company_map, dry_run, sla_type)
        global_summary["empresas"].append(summary)
        
        # Acumular totales
        global_summary["totales"]["backlog_sii"] += summary["backlog_sii"]
        global_summary["totales"]["backlog_contabilizar"] += summary["backlog_contabilizar"]
        global_summary["totales"]["backlog_conciliar"] += summary["backlog_conciliar"]
        global_summary["totales"]["checks_creados"] += summary["checks_creados"]
        global_summary["totales"]["checks_actualizados"] += summary["checks_actualizados"]
        global_summary["totales"]["checks_autocerrados"] += summary["checks_autocerrados"]
        global_summary["totales"]["checks_reabiertos"] += summary["checks_reabiertos"]
    
    # Resumen final estructurado
    logger.info(f"\n{'='*60}")
    logger.log_global_summary(global_summary)
    logger.info(f"{'='*60}")
    
    if dry_run:
        logger.info("⚠️ DRY-RUN: No se escribió nada")
    
    return global_summary


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Sincroniza pendientes Odoo → SGCA expected_item_checks'
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
        help='No escribir, solo mostrar qué haría'
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
    
    # Ejecutar sync
    try:
        result = sync_all(year, month, args.only, args.dry_run, args.sla_type)
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        
        # Exit code basado en errores
        total_errors = sum(len(e.get("errors", [])) for e in result["empresas"])
        sys.exit(1 if total_errors > 0 else 0)
        
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
