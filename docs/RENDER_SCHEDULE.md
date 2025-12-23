# SGCA - Horarios de Ejecución (Render)

> **Última actualización:** 2025-12-23
> **Timezone:** America/Santiago (Chile Continental)

## Secuencia de Ejecución

| Sistema | Horario AM | Horario PM | Descripción |
|---------|------------|------------|-------------|
| **Odoo** | 07:00 | 19:00 | Actualiza pendientes (job interno) |
| **Bridge SGCA** | 07:30 | 19:30 | Sincroniza Odoo → Supabase |
| **Core SGCA** | 07:40 | 19:40 | Detecta atrasos, escala findings |

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
    name: sgca-bridge-am
    schedule: "30 10 * * 1-5"  # 07:30 Chile = 10:30 UTC (días hábiles)
    buildCommand: pip install -r requirements.txt
    startCommand: python scripts/run_bridge_scheduled.py
    envVars:
      - key: TZ
        value: America/Santiago

  - type: cron
    name: sgca-bridge-pm
    schedule: "30 22 * * 1-5"  # 19:30 Chile = 22:30 UTC (días hábiles)
    buildCommand: pip install -r requirements.txt
    startCommand: python scripts/run_bridge_scheduled.py
    envVars:
      - key: TZ
        value: America/Santiago
```

### Variables de Entorno Requeridas

```env
SUPABASE_URL=https://uwpnfdmirqwmuuzjwlzo.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
ODOO_URL=https://odoo.factorit.cl
ODOO_DB_FACTORIT=FactorIT
ODOO_DB_FACTORIT2=FactorIT2
ODOO_USERNAME=api_user
ODOO_PASSWORD=***
TZ=America/Santiago
```

---

## Core SGCA (sgca-core)

### Comando Render

```bash
python jobs/daily_run.py
```

### Configuración Cron en Render

```yaml
services:
  - type: cron
    name: sgca-core-am
    schedule: "40 10 * * 1-5"  # 07:40 Chile = 10:40 UTC
    buildCommand: pip install -r requirements.txt
    startCommand: python jobs/daily_run.py
    envVars:
      - key: TZ
        value: America/Santiago

  - type: cron
    name: sgca-core-pm
    schedule: "40 22 * * 1-5"  # 19:40 Chile = 22:40 UTC
    buildCommand: pip install -r requirements.txt
    startCommand: python jobs/daily_run.py
    envVars:
      - key: TZ
        value: America/Santiago
```

---

## Conversión de Timezone

| Chile (America/Santiago) | UTC |
|--------------------------|-----|
| 07:30 | 10:30 (verano) / 11:30 (invierno) |
| 19:30 | 22:30 (verano) / 23:30 (invierno) |

**Nota:** Chile usa horario de verano (DST). Render ejecuta en UTC, así que los horarios deben ajustarse según la época del año, o usar la variable `TZ=America/Santiago`.

---

## Verificación Manual

### Bridge

```bash
cd sgca-integraciones

# Ver qué haría sin escribir
python scripts/run_bridge_scheduled.py --dry-run

# Ejecutar solo FactorIT
python scripts/run_bridge_scheduled.py --only FactorIT

# Ejecutar ambas empresas
python scripts/run_bridge_scheduled.py
```

### Core

```bash
cd sgca-core

# Ejecutar job diario
python jobs/daily_run.py
```

---

## Monitoreo

### Logs esperados del Bridge

```
2025-01-15 07:30:05 [INFO] ============================================================
2025-01-15 07:30:05 [INFO] SGCA BRIDGE - EJECUCIÓN PROGRAMADA
2025-01-15 07:30:05 [INFO] ============================================================
2025-01-15 07:30:05 [INFO]   Start time : 2025-01-15T07:30:05-03:00
2025-01-15 07:30:05 [INFO]   Timezone   : America/Santiago
2025-01-15 07:30:05 [INFO]   Period     : 2025-01
2025-01-15 07:30:05 [INFO]   Empresas   : FactorIT, FactorIT2
...
2025-01-15 07:30:12 [INFO]   Duración     : 7.23s
2025-01-15 07:30:12 [INFO]   Exit code    : 0
```

### Alertas

- **Exit code 1**: Revisar logs, puede haber error de conexión a Odoo o Supabase
- **Sin snapshots**: Verificar que `erp_backlog_snapshots` tenga registros recientes
- **Checks no actualizados**: Verificar `expected_item_checks` con la fecha de hoy

---

## Troubleshooting

### Bridge no conecta a Odoo

```bash
# Verificar conectividad
curl -I https://odoo.factorit.cl

# Verificar credenciales
python -c "from odoo.pendientes import obtener_pendientes_empresa; print(obtener_pendientes_empresa('FactorIT'))"
```

### Bridge no conecta a Supabase

```bash
# Verificar variables
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY | head -c 20

# Test rápido
python -c "from supabase import create_client; c = create_client('$SUPABASE_URL', '$SUPABASE_SERVICE_ROLE_KEY'); print(c.table('companies').select('name').limit(1).execute())"
```

### Timezone incorrecto

```bash
# Verificar timezone en el container
date
echo $TZ

# Forzar timezone
export TZ=America/Santiago
date
```

