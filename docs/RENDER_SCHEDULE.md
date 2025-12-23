# SGCA - Horarios de Ejecución (Render)

> **Última actualización:** 2025-12-23
> **Timezone:** America/Santiago (Chile Continental)

## Horario de Ejecución

| Sistema | Horario | Frecuencia | Descripción |
|---------|---------|------------|-------------|
| **Bridge SGCA** | 05:00 AM | Diario (L-V) | Sincroniza Odoo → Supabase |

---

## Bridge SGCA (sgca-integraciones)

### Comando Render

```bash
python scripts/run_bridge_scheduled.py
```

### Configuración Cron en Render

```yaml
# render.yaml
services:
  - type: cron
    name: sgca-bridge
    schedule: "0 8 * * 1-5"  # 05:00 Chile = 08:00 UTC (días hábiles)
    buildCommand: pip install -r requirements.txt
    startCommand: python scripts/run_bridge_scheduled.py
    envVars:
      - key: TZ
        value: America/Santiago
      - key: BRIDGE_ENABLE_ODOO
        value: "true"
      - key: BRIDGE_ENABLE_SKUALO
        value: "true"
```

### Variables de Entorno Requeridas

```env
# Supabase
SUPABASE_URL=https://uwpnfdmirqwmuuzjwlzo.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Odoo
SERVER=odoo-db.factorit.cl
PORT=5432
DB_USER=api_user
PASSWORD=***

# Timezone
TZ=America/Santiago
```

---

## Conversión de Timezone

| Chile (America/Santiago) | UTC |
|--------------------------|-----|
| 05:00 | 08:00 (verano) / 09:00 (invierno) |

**Nota:** Chile usa horario de verano (DST). Actualmente estamos en verano, así que 05:00 Chile = 08:00 UTC.

---

## Verificación Manual

```bash
cd sgca-integraciones

# Ver qué haría sin escribir
python scripts/run_bridge_scheduled.py --dry-run

# Ejecutar solo FactorIT
python scripts/run_bridge_scheduled.py --only FactorIT

# Ejecutar ambas empresas (Odoo)
python scripts/run_bridge_scheduled.py --source odoo

# Ejecutar ambas fuentes
python scripts/run_bridge_scheduled.py --source both
```

---

## Monitoreo

### Logs esperados del Bridge

```
2025-01-15 05:00:05 [INFO] ======================================================================
2025-01-15 05:00:05 [INFO] SGCA BRIDGE - EJECUCIÓN PROGRAMADA MULTI-FUENTE
2025-01-15 05:00:05 [INFO] ======================================================================
2025-01-15 05:00:05 [INFO]   Start time : 2025-01-15T05:00:05-03:00
2025-01-15 05:00:05 [INFO]   Timezone   : America/Santiago
2025-01-15 05:00:05 [INFO]   Period     : 2025-01
2025-01-15 05:00:05 [INFO]   Source     : both
2025-01-15 05:00:05 [INFO]   Empresas   : todas
...
2025-01-15 05:00:12 [INFO] RESUMEN FINAL
2025-01-15 05:00:12 [INFO]   ODOO       : ✅ (2 empresas)
2025-01-15 05:00:12 [INFO]   SKUALO     : SKIPPED (no_companies_enabled)
2025-01-15 05:00:12 [INFO]   Duración   : 8.89s
2025-01-15 05:00:12 [INFO]   Exit code  : 0
```

### Alertas

| Exit Code | Significado | Acción |
|-----------|-------------|--------|
| `0` | Éxito | Nada |
| `1` | Error | Revisar logs de Render |

### Verificaciones post-ejecución

- **Snapshots:** `erp_backlog_snapshots` debe tener registros de hoy
- **Checks:** `expected_item_checks` debe tener el período actual

---

## Troubleshooting

### Bridge no conecta a Odoo

```bash
# Verificar conectividad
psql -h $SERVER -p $PORT -U $DB_USER -d FactorIT -c "SELECT 1"
```

### Bridge no conecta a Supabase

```bash
# Verificar variables
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY | head -c 20
```

### Timezone incorrecto

```bash
# Verificar timezone en el container
date
echo $TZ
# Debe mostrar hora de Chile
```

### company_map.json no encontrado

Este archivo debe estar en el repo. Verificar:
```bash
ls -la bridge/company_map.json
```
