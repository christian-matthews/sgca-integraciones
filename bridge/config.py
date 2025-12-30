"""
Bridge Configuration
====================

Mapeo de empresas Odoo ↔ SGCA Core
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN SUPABASE (CORE)
# ═══════════════════════════════════════════════════════════════════════════════

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# ═══════════════════════════════════════════════════════════════════════════════
# MAPEO EMPRESAS ODOO ↔ SGCA
# ═══════════════════════════════════════════════════════════════════════════════

# Mapeo: db_odoo → company_id en SGCA (actualizar con IDs reales)
EMPRESA_MAPPING = {
    "FactorIT": {
        "nombre": "FactorIT SpA",
        "company_id": None,  # Se busca dinámicamente por nombre
        "tenant_id": None,
    },
    "FactorIT2": {
        "nombre": "FactorIT Ltda", 
        "company_id": None,
        "tenant_id": None,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# TIMEZONE
# ═══════════════════════════════════════════════════════════════════════════════

TIMEZONE = "America/Santiago"

# ═══════════════════════════════════════════════════════════════════════════════
# SLA CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Hora límite para SLA (18:00)
SLA_DEADLINE_HOUR = 18
SLA_DEADLINE_MINUTE = 0

# Días hábiles para SLA mensual
SLA_MENSUAL_BUSINESS_DAYS = 3

# Sin gracia
GRACE_DAYS = 0

# ═══════════════════════════════════════════════════════════════════════════════
# EXPECTED ITEM CODES
# ═══════════════════════════════════════════════════════════════════════════════

# Checks SLA Semanal
CHECK_SEMANAL_CONTABILIZACION = "CIERRE_SEMANAL_CONTABILIZACION"
CHECK_SEMANAL_CONCILIACION = "CIERRE_SEMANAL_CONCILIACION"

# Checks SLA Mensual
CHECK_MENSUAL_CONTABILIZACION = "CIERRE_MENSUAL_CONTABILIZACION"
CHECK_MENSUAL_CONCILIACION = "CIERRE_MENSUAL_CONCILIACION"

# Checks detallados (por tipo de pendiente)
CHECK_REVISION_FACTURAS = "REVISION_FACTURAS_PROVEEDOR"
CHECK_DIGITACION_FACTURAS = "DIGITACION_FACTURAS"
CHECK_CONCILIACION_BANCARIA = "CONCILIACION_BANCARIA"





