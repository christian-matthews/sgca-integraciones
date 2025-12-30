#!/usr/bin/env python3
"""
SGCA Bridge - Sync Manager
==========================

Orquestador para sincronizar pendientes desde múltiples fuentes (Odoo, Skualo)
hacia expected_item_checks en Supabase.

FUENTES SOPORTADAS:
- Odoo: Pendientes de ERP Odoo (PostgreSQL directo)
- Skualo: Pendientes de plataforma Skualo (API REST)

FLUJO:
1. Leer company_map.json para determinar qué fuentes están habilitadas por empresa
2. Ejecutar sync de cada fuente habilitada
3. Consolidar resultados

USO:
    from bridge.sync_manager import SyncManager
    
    manager = SyncManager()
    result = manager.sync_all(source="both")  # "odoo", "skualo", "both"

NO modifica sgca-core. Solo escribe a Supabase.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

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

class StructuredLogger:
    """Logger estructurado para sync manager."""
    
    def __init__(self, name: str = 'bridge.manager'):
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


logger = StructuredLogger('bridge.manager')


# ═══════════════════════════════════════════════════════════════════════════════
# SYNC MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class SyncManager:
    """
    Orquestador de sincronización multi-fuente.
    
    Coordina la ejecución de syncs desde Odoo y Skualo,
    consolidando resultados y manejando errores.
    """
    
    def __init__(self):
        """Inicializa el manager cargando configuración."""
        self.company_map = self._load_company_map()
        self._odoo_sync = None
        self._skualo_sync = None
    
    def _load_company_map(self) -> Dict[str, Dict]:
        """Carga company_map.json."""
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
    
    def _get_odoo_sync(self):
        """Lazy import de sync_odoo_to_checks."""
        if self._odoo_sync is None:
            try:
                from bridge.sync_odoo_to_checks import sync_all as odoo_sync_all
                self._odoo_sync = odoo_sync_all
            except ImportError as e:
                logger.error(f"Error importando sync_odoo_to_checks: {e}")
                self._odoo_sync = None
        return self._odoo_sync
    
    def _get_skualo_sync(self):
        """Lazy import de sync_skualo_to_checks."""
        if self._skualo_sync is None:
            try:
                from bridge.sync_skualo_to_checks import sync_all as skualo_sync_all
                self._skualo_sync = skualo_sync_all
            except ImportError as e:
                logger.warning(f"sync_skualo_to_checks no disponible: {e}")
                self._skualo_sync = None
        return self._skualo_sync
    
    def _now_chile(self) -> datetime:
        """Retorna datetime actual en zona Chile."""
        return datetime.now(TIMEZONE)
    
    def _get_current_period(self) -> tuple:
        """Retorna (year, month) del período actual."""
        now = self._now_chile()
        return now.year, now.month
    
    def _is_source_enabled(self, db_alias: str, source: str) -> bool:
        """
        Verifica si una fuente está habilitada para una empresa.
        
        Args:
            db_alias: Alias de empresa (FactorIT, FactorIT2)
            source: Fuente (odoo, skualo)
        
        Returns:
            True si está habilitada
        """
        company_config = self.company_map.get(db_alias, {})
        source_config = company_config.get(source, {})
        return source_config.get("enabled", False)
    
    def _is_source_enabled_env(self, source: str) -> bool:
        """
        Verifica si una fuente está habilitada por variable de entorno.
        
        Variables:
        - BRIDGE_ENABLE_ODOO (default: true)
        - BRIDGE_ENABLE_SKUALO (default: true)
        
        Args:
            source: Fuente (odoo, skualo)
        
        Returns:
            True si está habilitada
        """
        env_var = f"BRIDGE_ENABLE_{source.upper()}"
        value = os.getenv(env_var, "true").lower()
        return value in ("true", "1", "yes")
    
    def sync_odoo(
        self,
        year: int,
        month: int,
        only: Optional[str] = None,
        dry_run: bool = False,
        sla_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Sincroniza desde Odoo.
        
        Args:
            year: Año
            month: Mes
            only: Empresa específica o None para todas
            dry_run: No escribir si True
            sla_type: Tipo de SLA
        
        Returns:
            Resultado del sync
        """
        sync_fn = self._get_odoo_sync()
        if not sync_fn:
            return {
                "source": "odoo",
                "success": False,
                "error": "sync_odoo_to_checks no disponible",
                "empresas": []
            }
        
        # Verificar habilitación por env
        if not self._is_source_enabled_env("odoo"):
            logger.info("Odoo deshabilitado por BRIDGE_ENABLE_ODOO=false")
            return {
                "source": "odoo",
                "success": True,
                "skipped": True,
                "reason": "disabled_by_env",
                "empresas": []
            }
        
        # Filtrar empresas con Odoo habilitado
        empresas_odoo = []
        for db_alias in self.company_map.keys():
            if only and db_alias != only:
                continue
            if self._is_source_enabled(db_alias, "odoo"):
                empresas_odoo.append(db_alias)
        
        if not empresas_odoo:
            return {
                "source": "odoo",
                "success": True,
                "skipped": True,
                "reason": "no_companies_enabled",
                "empresas": []
            }
        
        result = {
            "source": "odoo",
            "success": True,
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
        
        for db_alias in empresas_odoo:
            try:
                logger.info(f"SYNC_ODOO", empresa=db_alias, period=f"{year}-{month:02d}")
                empresa_result = sync_fn(
                    year=year,
                    month=month,
                    only=db_alias,
                    dry_run=dry_run,
                    sla_type=sla_type
                )
                
                # Acumular resultados
                for emp in empresa_result.get("empresas", []):
                    result["empresas"].append({**emp, "source": "odoo"})
                    if emp.get("errors"):
                        result["success"] = False
                
                totales = empresa_result.get("totales", {})
                for key in result["totales"]:
                    result["totales"][key] += totales.get(key, 0)
                    
            except Exception as e:
                logger.error(f"Error sync Odoo {db_alias}: {e}")
                result["success"] = False
                result["empresas"].append({
                    "empresa": db_alias,
                    "source": "odoo",
                    "errors": [str(e)]
                })
        
        return result
    
    def sync_skualo(
        self,
        year: int,
        month: int,
        only: Optional[str] = None,
        dry_run: bool = False,
        sla_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Sincroniza desde Skualo.
        
        Args:
            year: Año
            month: Mes
            only: Empresa específica o None para todas
            dry_run: No escribir si True
            sla_type: Tipo de SLA
        
        Returns:
            Resultado del sync
        """
        sync_fn = self._get_skualo_sync()
        if not sync_fn:
            return {
                "source": "skualo",
                "success": True,
                "skipped": True,
                "reason": "sync_skualo_to_checks no disponible",
                "empresas": []
            }
        
        # Verificar habilitación por env
        if not self._is_source_enabled_env("skualo"):
            logger.info("Skualo deshabilitado por BRIDGE_ENABLE_SKUALO=false")
            return {
                "source": "skualo",
                "success": True,
                "skipped": True,
                "reason": "disabled_by_env",
                "empresas": []
            }
        
        # Filtrar empresas con Skualo habilitado
        empresas_skualo = []
        for db_alias in self.company_map.keys():
            if only and db_alias != only:
                continue
            if self._is_source_enabled(db_alias, "skualo"):
                empresas_skualo.append(db_alias)
        
        if not empresas_skualo:
            return {
                "source": "skualo",
                "success": True,
                "skipped": True,
                "reason": "no_companies_enabled",
                "empresas": []
            }
        
        result = {
            "source": "skualo",
            "success": True,
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
        
        for db_alias in empresas_skualo:
            try:
                logger.info(f"SYNC_SKUALO", empresa=db_alias, period=f"{year}-{month:02d}")
                empresa_result = sync_fn(
                    year=year,
                    month=month,
                    only=db_alias,
                    dry_run=dry_run,
                    sla_type=sla_type
                )
                
                # Acumular resultados
                for emp in empresa_result.get("empresas", []):
                    result["empresas"].append({**emp, "source": "skualo"})
                    if emp.get("errors"):
                        result["success"] = False
                
                totales = empresa_result.get("totales", {})
                for key in result["totales"]:
                    result["totales"][key] += totales.get(key, 0)
                    
            except Exception as e:
                logger.error(f"Error sync Skualo {db_alias}: {e}")
                result["success"] = False
                result["empresas"].append({
                    "empresa": db_alias,
                    "source": "skualo",
                    "errors": [str(e)]
                })
        
        return result
    
    def sync_all(
        self,
        source: str = "both",
        year: Optional[int] = None,
        month: Optional[int] = None,
        only: Optional[str] = None,
        dry_run: bool = False,
        sla_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Sincroniza desde todas las fuentes habilitadas.
        
        Args:
            source: "odoo", "skualo", o "both"
            year: Año (default: actual)
            month: Mes (default: actual)
            only: Empresa específica o None para todas
            dry_run: No escribir si True
            sla_type: Tipo de SLA
        
        Returns:
            Resultado consolidado
        """
        start_time = self._now_chile()
        
        if year is None or month is None:
            year, month = self._get_current_period()
        
        period = f"{year}-{month:02d}"
        
        logger.info("=" * 70)
        logger.info("SYNC_MANAGER - INICIO")
        logger.info("=" * 70)
        logger.info(f"  Start time : {start_time.isoformat()}")
        logger.info(f"  Period     : {period}")
        logger.info(f"  Source     : {source}")
        logger.info(f"  Empresas   : {only or 'todas'}")
        logger.info(f"  Dry Run    : {dry_run}")
        logger.info("=" * 70)
        
        global_result = {
            "fecha_sync": start_time.isoformat(),
            "periodo": period,
            "source_requested": source,
            "dry_run": dry_run,
            "success": True,
            "sources": {},
            "totales": {
                "backlog_sii": 0,
                "backlog_contabilizar": 0,
                "backlog_conciliar": 0,
                "checks_creados": 0,
                "checks_actualizados": 0,
                "checks_autocerrados": 0,
                "checks_reabiertos": 0,
            },
            "empresas_procesadas": 0,
            "empresas_con_error": 0,
        }
        
        # Ejecutar syncs según source
        if source in ("odoo", "both"):
            logger.info("\n>>> FUENTE: ODOO")
            odoo_result = self.sync_odoo(year, month, only, dry_run, sla_type)
            global_result["sources"]["odoo"] = odoo_result
            
            if not odoo_result.get("success", True):
                global_result["success"] = False
            
            # Acumular totales
            odoo_totales = odoo_result.get("totales", {})
            for key in global_result["totales"]:
                global_result["totales"][key] += odoo_totales.get(key, 0)
            
            # Contar empresas
            for emp in odoo_result.get("empresas", []):
                global_result["empresas_procesadas"] += 1
                if emp.get("errors"):
                    global_result["empresas_con_error"] += 1
        
        if source in ("skualo", "both"):
            logger.info("\n>>> FUENTE: SKUALO")
            skualo_result = self.sync_skualo(year, month, only, dry_run, sla_type)
            global_result["sources"]["skualo"] = skualo_result
            
            if not skualo_result.get("success", True):
                global_result["success"] = False
            
            # Acumular totales
            skualo_totales = skualo_result.get("totales", {})
            for key in global_result["totales"]:
                global_result["totales"][key] += skualo_totales.get(key, 0)
            
            # Contar empresas
            for emp in skualo_result.get("empresas", []):
                global_result["empresas_procesadas"] += 1
                if emp.get("errors"):
                    global_result["empresas_con_error"] += 1
        
        # Resumen final
        end_time = self._now_chile()
        duration = (end_time - start_time).total_seconds()
        global_result["duration_seconds"] = duration
        
        logger.info("\n" + "=" * 70)
        logger.info("SYNC_MANAGER - RESUMEN")
        logger.info("=" * 70)
        logger.info(f"  Empresas procesadas : {global_result['empresas_procesadas']}")
        logger.info(f"  Empresas con error  : {global_result['empresas_con_error']}")
        logger.info(f"  Checks creados      : {global_result['totales']['checks_creados']}")
        logger.info(f"  Checks actualizados : {global_result['totales']['checks_actualizados']}")
        logger.info(f"  Checks autocerrados : {global_result['totales']['checks_autocerrados']}")
        logger.info(f"  Duración            : {duration:.2f}s")
        logger.info(f"  Éxito               : {'✅' if global_result['success'] else '❌'}")
        logger.info("=" * 70)
        
        return global_result


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_manager: Optional[SyncManager] = None

def get_sync_manager() -> SyncManager:
    """Retorna instancia singleton del SyncManager."""
    global _manager
    if _manager is None:
        _manager = SyncManager()
    return _manager


def sync_all(
    source: str = "both",
    year: Optional[int] = None,
    month: Optional[int] = None,
    only: Optional[str] = None,
    dry_run: bool = False,
    sla_type: str = "all"
) -> Dict[str, Any]:
    """
    Función de conveniencia para sync_all.
    
    Equivalente a: get_sync_manager().sync_all(...)
    """
    return get_sync_manager().sync_all(
        source=source,
        year=year,
        month=month,
        only=only,
        dry_run=dry_run,
        sla_type=sla_type
    )






