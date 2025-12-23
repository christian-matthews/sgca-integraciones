# Release Notes: FactorIT Pipeline v1 (Bridge)

**Fecha**: 2025-12-23  
**Tag**: `checkpoint/factorit-pipeline-v1-bridge`  
**Branch**: `release/factorit-pipeline-v1`

---

## Qué se agregó

### 1. Bridge Odoo → SGCA (`bridge/`)

Módulo completo para sincronizar pendientes desde Odoo hacia `expected_item_checks` en SGCA Core.

#### Archivos:
- `bridge/__init__.py` - Inicialización del módulo
- `bridge/config.py` - Configuración centralizada (timezone, SLA, códigos)
- `bridge/sla_calculator.py` - Cálculo de deadlines SLA (semanal/mensual)
- `bridge/sync_odoo_to_checks.py` - Script principal de sincronización
- `bridge/company_map.json` - Mapeo Odoo alias → company_id SGCA

### 2. Migración para Snapshots (`migrations/001_erp_backlog_snapshots.sql`)

Tabla para registrar métricas continuas del backlog ERP.

---

## Comandos del Bridge

```bash
cd sgca-integraciones

# Sync completo (ambas empresas)
python -m bridge.sync_odoo_to_checks --period 2025-12

# Solo una empresa
python -m bridge.sync_odoo_to_checks --period 2025-12 --only FactorIT

# Dry-run (no escribe a Supabase)
python -m bridge.sync_odoo_to_checks --period 2025-12 --dry-run

# Solo SLA semanal
python -m bridge.sync_odoo_to_checks --period 2025-12 --sla-type weekly

# Solo SLA mensual
python -m bridge.sync_odoo_to_checks --period 2025-12 --sla-type monthly
```

---

## SLA Implementados

### SLA Semanal
- **Semana operacional**: Lunes 00:00 → Viernes 18:00
- **Deadline**: Miércoles de la semana siguiente a las 18:00
- **Checks**: `CIERRE_SEMANAL_CONTABILIZACION`, `CIERRE_SEMANAL_CONCILIACION`
- **Autocierre**: Si backlog = 0, el check se marca completado automáticamente

### SLA Mensual
- **Deadline**: 3 días hábiles después del último día del mes, a las 18:00
- **Checks**: `CIERRE_MENSUAL_CONTABILIZACION`, `CIERRE_MENSUAL_CONCILIACION`
- **Autocierre**: Si backlog = 0

### Checks Agregados (diarios)
- `REVISION_FACTURAS_PROVEEDOR` - Facturas pendientes en SII
- `DIGITACION_FACTURAS` - Facturas por contabilizar
- `CONCILIACION_BANCARIA` - Movimientos por conciliar

---

## Mapeo de Empresas (`company_map.json`)

```json
{
  "FactorIT": {
    "tenant_id": "6cf187d9-33a3-43d0-86f7-98801561dd50",
    "company_id": "b414a16f-c0ea-405f-b17e-d7f09aa1562a"
  },
  "FactorIT2": {
    "tenant_id": "6cf187d9-33a3-43d0-86f7-98801561dd50",
    "company_id": "e98f87ea-6c5f-4e92-b466-87b9ff806c2c"
  }
}
```

Este archivo se genera automáticamente desde `sgca-core/scripts/seed_factorit_two_companies.py`.

---

## Flujo Operativo Diario

```
1. Bridge sync (desde Odoo)
   python -m bridge.sync_odoo_to_checks --period 2025-12

2. Motor SGCA (desde core)
   python -m jobs.daily_run

3. Validación SQL:
   SELECT c.name, count(*) as open_findings
   FROM findings f
   JOIN companies c ON c.company_id = f.company_id
   WHERE c.name ILIKE 'FactorIT%' AND f.status = 'OPEN'
   GROUP BY c.name;
```

---

## Dependencias

- Supabase: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- Odoo DBs: `FACTORIT_DB_*`, `FACTORIT2_DB_*` en `.env`
- Python 3.9+
- `pytz`, `supabase`, `psycopg2-binary`

---

## Restricciones

- ❌ NO se modificó `sgca-core/src/engine/*`
- ✅ Bridge es 100% satélite, escribe solo a `expected_item_checks`
- ✅ Autocierre es seguro (reabre si backlog > 0)
