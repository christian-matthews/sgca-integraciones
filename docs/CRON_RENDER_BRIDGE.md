# SGCA Bridge - Cron Multi-Fuente en Render

> **Última actualización:** 2025-12-23

---

## ¿Qué hace el cron del bridge?

El bridge sincroniza pendientes desde **múltiples fuentes** hacia **Supabase** (SGCA).

### Fuentes soportadas

| Fuente | Descripción | Datos sincronizados |
|--------|-------------|---------------------|
| **Odoo** | ERP PostgreSQL | SII, contabilizar, conciliar |
| **Skualo** | Plataforma API REST | SII, contabilizar, conciliar |

### Proceso

1. Lee pendientes de la fuente (Odoo y/o Skualo)
2. Crea/actualiza `expected_item_checks` en Supabase
3. Inserta snapshot de backlog en `erp_backlog_snapshots`
4. Autocierra checks si el backlog llega a 0
5. Reabre checks si el backlog vuelve a subir

**Empresas procesadas:** FactorIT, FactorIT2 (configurable en `company_map.json`)

---

## Comando exacto para Render

```bash
python scripts/run_bridge_scheduled.py
```

**No requiere parámetros.** El script:
- Detecta automáticamente el período actual (YYYY-MM)
- Usa timezone America/Santiago
- Procesa ambas fuentes (Odoo + Skualo) según configuración

---

## Variables de entorno

### Supabase (requeridas)

```env
SUPABASE_URL=https://uwpnfdmirqwmuuzjwlzo.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

### Odoo (si Odoo habilitado)

```env
SERVER=odoo-db.factorit.cl
PORT=5432
DB_USER=api_user
PASSWORD=***
```

### Skualo (si Skualo habilitado)

```env
SKUALO_API_TOKEN=sk_live_...
SKUALO_BASE_URL=https://api.skualo.cl
```

### Control de fuentes

```env
# Habilitar/deshabilitar fuentes por entorno
BRIDGE_ENABLE_ODOO=true     # default: true
BRIDGE_ENABLE_SKUALO=true   # default: true

# Timezone (recomendado)
TZ=America/Santiago
```

---

## Horario del cron

| Sistema | Horario | Función |
|---------|---------|---------|
| **Bridge** | 05:00 AM | Sincroniza Odoo → Supabase |

**Timezone:** America/Santiago (Chile Continental)

**Frecuencia:** Una vez al día, de lunes a viernes.

---

## Configuración en Render

### render.yaml

```yaml
services:
  - type: cron
    name: sgca-bridge
    schedule: "0 8 * * 1-5"  # 05:00 Chile = 08:00 UTC
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

**Nota:** 
- Horarios en cron de Render son UTC
- 05:00 Chile = 08:00 UTC (en verano, ajustar en invierno a 09:00 UTC)

---

## Ejecución manual

```bash
cd sgca-integraciones

# Ver qué haría (ambas fuentes)
python scripts/run_bridge_scheduled.py --dry-run

# Solo Odoo
python scripts/run_bridge_scheduled.py --source odoo

# Solo Skualo
python scripts/run_bridge_scheduled.py --source skualo

# Ambas fuentes
python scripts/run_bridge_scheduled.py --source both

# Solo una empresa
python scripts/run_bridge_scheduled.py --only FactorIT

# Combinado
python scripts/run_bridge_scheduled.py --source odoo --only FactorIT --dry-run
```

---

## Configuración de empresas

El archivo `bridge/company_map.json` controla qué fuentes están habilitadas por empresa:

```json
{
  "FactorIT": {
    "tenant_id": "6cf187d9-...",
    "company_id": "b414a16f-...",
    "nombre": "FactorIT SpA",
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
    "tenant_id": "6cf187d9-...",
    "company_id": "e98f87ea-...",
    "nombre": "FactorIT Ltda",
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

Para habilitar Skualo para una empresa:
1. Cambiar `skualo.enabled` a `true`
2. Agregar el RUT de Skualo en `skualo.rut`

---

## Logs esperados

```
2025-01-15 07:30:05 [INFO] ======================================================================
2025-01-15 07:30:05 [INFO] SGCA BRIDGE - EJECUCIÓN PROGRAMADA MULTI-FUENTE
2025-01-15 07:30:05 [INFO] ======================================================================
2025-01-15 07:30:05 [INFO]   Start time : 2025-01-15T07:30:05-03:00
2025-01-15 07:30:05 [INFO]   Timezone   : America/Santiago
2025-01-15 07:30:05 [INFO]   Period     : 2025-01
2025-01-15 07:30:05 [INFO]   Source     : both
2025-01-15 07:30:05 [INFO]   Empresas   : todas
2025-01-15 07:30:05 [INFO]   Odoo enabled (env)   : True
2025-01-15 07:30:05 [INFO]   Skualo enabled (env) : True
...
2025-01-15 07:30:12 [INFO] RESUMEN FINAL
2025-01-15 07:30:12 [INFO]   ODOO       : ✅ (2 empresas)
2025-01-15 07:30:12 [INFO]   SKUALO     : SKIPPED (no_companies_enabled)
2025-01-15 07:30:12 [INFO]   Empresas       : 2
2025-01-15 07:30:12 [INFO]   Checks creados      : 4
2025-01-15 07:30:12 [INFO]   Checks actualizados : 2
2025-01-15 07:30:12 [INFO]   Duración       : 7.23s
2025-01-15 07:30:12 [INFO]   Exit code      : 0
```

---

## Códigos de salida

| Código | Significado |
|--------|-------------|
| `0` | Éxito - todas las fuentes/empresas sincronizadas |
| `1` | Error - al menos una fuente/empresa falló |

---

## Arquitectura

```
scripts/run_bridge_scheduled.py
    │
    └── bridge/sync_manager.py (orquestador)
            │
            ├── bridge/sync_odoo_to_checks.py
            │       └── odoo/pendientes.py (cliente Odoo)
            │
            └── bridge/sync_skualo_to_checks.py
                    └── skualo/pendientes.py (cliente Skualo)
```

---

## Troubleshooting

### Error de Odoo

```
Error obteniendo pendientes de Odoo: ...
```

**Verificar:**
- Variables `SERVER`, `PORT`, `DB_USER`, `PASSWORD`
- Conectividad a la BD Odoo
- `BRIDGE_ENABLE_ODOO=true`

### Error de Skualo

```
Error obteniendo pendientes de Skualo: ...
```

**Verificar:**
- Variable `SKUALO_API_TOKEN`
- Conectividad a `api.skualo.cl`
- `BRIDGE_ENABLE_SKUALO=true`
- RUT configurado en `company_map.json`

### Fuente skipped

```
SKUALO     : SKIPPED (no_companies_enabled)
```

**Significado:** Ninguna empresa tiene esa fuente habilitada en `company_map.json`.

### Timezone incorrecto

```bash
# Verificar en container
date
echo $TZ
# Debe mostrar hora de Chile
```

---

## Idempotencia

El bridge es **idempotente**:
- Puede ejecutarse múltiples veces sin duplicar datos
- Usa UPSERT para checks (clave: company_id + period_id + expected_item_code)
- Los snapshots se insertan siempre (histórico)
- Es seguro re-ejecutar manualmente si falla

---

## Verificar versión desplegada

### Script de verificación local

Antes de deployar, ejecuta el script de verificación:

```bash
cd sgca-integraciones
chmod +x scripts/git_release_verify.sh
./scripts/git_release_verify.sh
```

Este script:
1. Verifica que estás en un repo git válido
2. Muestra branch y último commit
3. Ofrece commitear cambios pendientes
4. Hace push al remoto
5. Muestra el hash que debe estar en Render

### Ver branch configurada en Render

1. Ir a [Render Dashboard](https://dashboard.render.com)
2. Seleccionar el servicio `sgca-bridge-am` o `sgca-bridge-pm`
3. En **Settings** → **Build & Deploy**:
   - Verificar **Branch**: debe coincidir con tu branch local
   - Verificar **Auto-Deploy**: activado para deploys automáticos

### Validar hash en Render

En los logs de Render (después de un deploy), ejecutar en el shell:

```bash
git rev-parse HEAD
```

Debe coincidir con el hash que muestra `git_release_verify.sh` localmente.

### Qué hacer si el hash no coincide

| Situación | Acción |
|-----------|--------|
| Branch incorrecta en Render | Cambiar en Settings → Build & Deploy → Branch |
| Código no pusheado | Ejecutar `./scripts/git_release_verify.sh` y confirmar push |
| Deploy pendiente | Ir a Render → Manual Deploy → Deploy latest commit |
| Cache de Render | Clear build cache y re-deploy |

### Checklist pre-deploy

```
□ Ejecutar: ./scripts/git_release_verify.sh
□ Confirmar que working tree está limpio
□ Verificar que push fue exitoso
□ Anotar hash local: git rev-parse HEAD
□ Verificar branch en Render dashboard
□ Trigger manual deploy si es necesario
□ Verificar hash en logs de Render
```
