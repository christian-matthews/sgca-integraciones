# FIT DEMO - Mapeo de Backlog Odoo → SGCA

**Fecha:** 2025-12-26  
**Propósito:** Documentar el mapeo entre empresas Odoo y company_id DEMO en SGCA.

---

## Llave de Mapeo

El bridge usa el archivo `bridge/company_map.json` para mapear:

| Campo | Descripción |
|-------|-------------|
| `db_alias` | Alias de base de datos Odoo (FactorIT, FactorIT2) |
| `company_id` | UUID de la empresa en SGCA Core (Supabase) |

---

## Empresas DEMO

| db_alias | Nombre SGCA | company_id DEMO |
|----------|-------------|-----------------|
| `FactorIT` | FactorIT SpA (DEMO) | `8c94de77-d40c-445b-84a8-80187c156624` |
| `FactorIT2` | FactorIT Ltda (DEMO) | `3e80e689-dfda-4aa0-a716-b6670ab826da` |

**Tenant compartido:** `6cf187d9-33a3-43d0-86f7-98801561dd50`

---

## company_map.json

```json
{
  "FactorIT": {
    "tenant_id": "6cf187d9-33a3-43d0-86f7-98801561dd50",
    "company_id": "8c94de77-d40c-445b-84a8-80187c156624",
    "nombre": "FactorIT SpA (DEMO)",
    "odoo": {
      "enabled": true,
      "db_name": "FactorIT"
    },
    "skualo": {
      "enabled": false,
      "rut": null
    }
  },
  "FactorIT2": {
    "tenant_id": "6cf187d9-33a3-43d0-86f7-98801561dd50",
    "company_id": "3e80e689-dfda-4aa0-a716-b6670ab826da",
    "nombre": "FactorIT Ltda (DEMO)",
    "odoo": {
      "enabled": true,
      "db_name": "FactorIT2"
    },
    "skualo": {
      "enabled": false,
      "rut": null
    }
  }
}
```

---

## Verificación SQL

### Snapshots recientes por empresa DEMO

```sql
SELECT 
    c.name,
    s.company_id,
    s.captured_at,
    s.sii_count,
    s.contabilizar_count,
    s.conciliar_count,
    s.db_alias
FROM public.erp_backlog_snapshots s
JOIN public.companies c ON c.company_id = s.company_id
WHERE s.company_id IN (
    '8c94de77-d40c-445b-84a8-80187c156624',  -- FactorIT SpA DEMO
    '3e80e689-dfda-4aa0-a716-b6670ab826da'   -- FactorIT Ltda DEMO
)
ORDER BY s.captured_at DESC
LIMIT 10;
```

### Vista v_company_backlog_now

```sql
SELECT *
FROM public.v_company_backlog_now
WHERE company_id IN (
    '8c94de77-d40c-445b-84a8-80187c156624',
    '3e80e689-dfda-4aa0-a716-b6670ab826da'
);
```

---

## Flujo de Datos

```
┌─────────────────┐     ┌───────────────────┐     ┌─────────────────────────┐
│   Odoo          │ --> │ bridge/sync_odoo  │ --> │ erp_backlog_snapshots   │
│  (FactorIT DB)  │     │  to_checks.py     │     │ (company_id DEMO)       │
└─────────────────┘     └───────────────────┘     └─────────────────────────┘
                              ↓
                        company_map.json
                        (db_alias → company_id)
```

---

## Cron Schedule

El bridge corre 2 veces al día en Render:
- 06:30 UTC (03:30 Chile)
- 18:30 UTC (15:30 Chile)

---

## Evidencia Post-Cambio

*(Agregar después de ejecutar el cron)*

```sql
-- Verificar últimos snapshots
SELECT captured_at, sii_count, contabilizar_count, conciliar_count
FROM public.erp_backlog_snapshots
WHERE company_id = '8c94de77-d40c-445b-84a8-80187c156624'
ORDER BY captured_at DESC
LIMIT 3;
```

---

## Cambio Realizado

**Archivo:** `bridge/company_map.json`

| Campo | Valor anterior | Valor nuevo |
|-------|----------------|-------------|
| FactorIT.company_id | `b414a16f-c0ea-405f-b17e-d7f09aa1562a` | `8c94de77-d40c-445b-84a8-80187c156624` |
| FactorIT2.company_id | `e98f87ea-6c5f-4e92-b466-87b9ff806c2c` | `3e80e689-dfda-4aa0-a716-b6670ab826da` |

---

*Última actualización: 2025-12-26*



