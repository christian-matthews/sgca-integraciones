# SGCA Integraciones

Sistema modular para integración con APIs de ERPs (Skualo, Odoo/FactorIT, Clay).

## 🏗️ Arquitectura

Los **artefactos** (definiciones de reportes) viven en `sgca-core/artefactos/`.
Las **implementaciones** por ERP viven aquí en `{erp}/reports/`.

```
sgca-core/artefactos/           ← CONTRATOS (Qué debe contener)
    └── balance_analisis/SPEC.md

sgca-integraciones/             ← IMPLEMENTACIONES (Cómo obtener datos)
    ├── skualo/reports/
    ├── odoo/reports/
    └── clay/reports/           (futuro)
```

## 📁 Estructura

```
sgca-integraciones/
├── skualo/                    # API Skualo ERP
│   ├── __init__.py           # Módulo principal
│   ├── cli.py                # CLI de comandos
│   ├── config.py             # Gestión de configuración
│   ├── control.py            # Clase SkualoControl
│   ├── pendientes.py         # Pendientes para Bridge
│   ├── config/               # Configuraciones
│   │   └── tenants.json      # Empresas disponibles
│   ├── reports/              # 📊 IMPLEMENTACIÓN DE ARTEFACTOS
│   │   ├── balance_excel.py  # ART-001: Balance + Análisis
│   │   └── generados/        # Archivos Excel generados
│   ├── scripts/              # Scripts auxiliares
│   └── docs/                 # Documentación técnica
│
├── odoo/                      # PostgreSQL Odoo (FactorIT)
│   ├── __init__.py           # Módulo principal
│   ├── pendientes.py         # Pendientes para Bridge
│   ├── reports/              # 📊 IMPLEMENTACIÓN DE ARTEFACTOS (TODO)
│   └── README.md
│
├── bridge/                    # Sincronización → Supabase
├── common/                    # Código compartido
├── docs/                      # Documentación consolidada
├── .env                       # Variables de entorno
└── requirements.txt
```

## 🚀 Instalación

```bash
# Clonar
git clone https://github.com/christian-matthews/SGCA-SKUALOAPI.git
cd SGCA-SKUALOAPI

# Dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cat > .env << EOF
# Skualo
SKUALO_API_TOKEN=tu-token-skualo

# Odoo/FactorIT (PostgreSQL)
SERVER=18.223.205.221
PORT=5432
DB_USER=tu-usuario
PASSWORD=tu-password
EOF
```

---

## 📋 Reportes de Pendientes (JSON)

Genera JSON con todos los pendientes para inyectar en otros sistemas.

### Skualo

```bash
python -m skualo.scripts.pendientes           # Todas las empresas
python -m skualo.scripts.pendientes FIDI      # Solo FIDI
python -m skualo.scripts.pendientes CISI      # Solo CISI
```

### Odoo (FactorIT)

```bash
python -m odoo.pendientes                     # Todas las empresas
```

### Estructura JSON

```json
{
  "generado": "2025-12-22T00:25:39",
  "version": "1.0",
  "resumen": {
    "total_sii": 14,
    "total_sii_monto": 11959665,
    "total_contabilizar": 10,
    "total_conciliar": 698
  },
  "empresas": [
    {
      "empresa": "FactorIT SpA",
      "pendientes_sii": { "cantidad": 6, "total": 7083642, "documentos": [...] },
      "pendientes_contabilizar": { "cantidad": 0, "documentos": [...] },
      "pendientes_conciliar": { "cantidad": 683, "por_banco": [...], "movimientos": [...] }
    }
  ]
}
```

---

## 📊 Balance + Estado de Resultados (Excel)

> **Especificación:** [`sgca-core/artefactos/balance_analisis/SPEC.md`](../sgca-core/artefactos/balance_analisis/SPEC.md)

### Skualo

```bash
cd skualo/reports
python balance_excel.py
```

**Configuración:** Editar `tenant_key`, `id_periodo`, `fecha_corte` en el script.

### Odoo (FactorIT) - TODO

```bash
cd odoo/reports
python balance_excel.py  # Por implementar
```

### Características (ART-001)

- ✅ Balance Clasificado (Activos, Pasivos, Patrimonio)
- ✅ Estado de Resultados (Ingresos, Costos, Gastos, Resultado Neto)
- ✅ EEFF Comparativos (Trimestres: Mar/Jun/Sep/Dic)
- ✅ KPIs Financieros (Margen Bruto, ROA, ROE)
- ✅ Hojas de análisis por cuenta con hipervínculos
- ✅ Navegación: Cuentas → Balance Tributario

---

## 💻 Uso - Skualo

### CLI

```bash
# Setup empresa (primera vez)
python -m skualo.cli setup 77285542-7

# Controles de pendientes
python -m skualo.cli pendientes 77285542-7

# Generar balance Excel
python -m skualo.cli balance 77285542-7 202511

# Reporte completo
python -m skualo.cli reporte 77285542-7
```

### Como Módulo Python

```python
from skualo import SkualoControl

ctrl = SkualoControl()
ctrl.setup_empresa('77285542-7')

# Controles
ctrl.movimientos_bancarios_pendientes('77285542-7')
ctrl.documentos_por_aprobar_sii('77285542-7')
ctrl.documentos_por_contabilizar('77285542-7')

# Balance Excel
ctrl.generar_balance_excel('77285542-7', '202511')
```

---

## 💻 Uso - Odoo (FactorIT)

### CLI

```bash
# Test de conexión
python -m odoo.test_connection

# Pendientes (JSON)
python -m odoo.pendientes

# Balance Excel
python -m odoo.balance_excel FactorIT

# Movimientos bancarios
python -m odoo.bancos_pendientes
```

### Como Módulo Python

```python
from odoo import obtener_pendientes, generar_balance_excel

# Obtener pendientes de todas las empresas
data = obtener_pendientes()
print(f"SII: {data['resumen']['total_sii']}")
print(f"Contabilizar: {data['resumen']['total_contabilizar']}")
print(f"Conciliar: {data['resumen']['total_conciliar']}")

# Generar Balance Excel
generar_balance_excel('FactorIT')
```

---

## 📝 Empresas Configuradas

### Skualo ERP (API REST)

| Alias | RUT | Nombre |
|-------|-----|--------|
| FIDI | 77285542-7 | Fidi SpA |
| CISI | 77949039-4 | Constructora CISI |

### Odoo (PostgreSQL Directo)

| Alias | Base de Datos | Nombre |
|-------|---------------|--------|
| FactorIT | FactorIT | FactorIT SpA |
| FactorIT2 | FactorIT2 | FactorIT Ltda |

---

## 📊 Estado Actual de Pendientes (22-Dic-2025)

### Skualo

| Empresa | SII | Contabilizar | Conciliar |
|---------|-----|--------------|-----------|
| FIDI SpA | 0 | 0 | 1 mov |
| CISI SpA | 2 ($119K) | 7 ($10.8M) | 68 movs |

### Odoo (FactorIT)

| Empresa | SII | Contabilizar | Conciliar |
|---------|-----|--------------|-----------|
| FactorIT SpA | 6 ($7.1M) | 0 | 683 movs |
| FactorIT Ltda | 8 ($4.9M) | 10 | 15 movs |

---

## 📊 Endpoints Validados (Skualo)

| Módulo | Endpoint | Estado |
|--------|----------|--------|
| Empresa | `/empresa` | ✅ |
| Auxiliares | `/auxiliares` | ✅ |
| Productos | `/productos` | ✅ |
| Balance | `/contabilidad/reportes/balancetributario/{periodo}` | ✅ |
| Libro Mayor | `/contabilidad/reportes/libromayor` | ✅ |
| Libro Diario | `/contabilidad/reportes/librodiario` | ✅ |
| Análisis Cuenta | `/contabilidad/reportes/analisisporcuenta/{id}` | ✅ |
| Bancos | `/bancos/{cuenta}` | ✅ |
| DTEs Recibidos | `/sii/dte/recibidos` | ✅ |
| Webhooks | `/integraciones/webhooks` | ✅ |

---

## 📖 Documentación

### Skualo
- [API Summary](skualo/docs/api_summary.md)
- [Webhooks](skualo/docs/webhooks.md)
- [Control de Pendientes](skualo/docs/control_pendientes.md)
- [Sistema Balance](skualo/docs/SISTEMA_BALANCE_README.md)

### Odoo
- [README Odoo](odoo/README.md) - Conexión, queries y reportes

---

---

## 🔗 Bridge SGCA (Odoo → expected_item_checks)

Módulo para sincronizar pendientes Odoo hacia el core SGCA.

### Instalación

```bash
pip install -r requirements.txt
```

### Comandos

```bash
# Sync completo (ambas empresas)
python -m bridge.sync_odoo_to_checks --period 2025-12

# Solo una empresa
python -m bridge.sync_odoo_to_checks --period 2025-12 --only FactorIT

# Dry-run (no escribe)
python -m bridge.sync_odoo_to_checks --period 2025-12 --dry-run

# Solo SLA semanal o mensual
python -m bridge.sync_odoo_to_checks --period 2025-12 --sla-type weekly
python -m bridge.sync_odoo_to_checks --period 2025-12 --sla-type monthly
```

### SLA Implementados

| Tipo | Deadline | Autocierre |
|------|----------|------------|
| Semanal | Miércoles T+1 @ 18:00 (Chile) | Si backlog = 0 |
| Mensual | 3 días hábiles post-cierre @ 18:00 | Si backlog = 0 |

### Checks Creados

| Código | Descripción |
|--------|-------------|
| `REVISION_FACTURAS_PROVEEDOR` | Facturas pendientes SII |
| `DIGITACION_FACTURAS` | Facturas por contabilizar |
| `CONCILIACION_BANCARIA` | Movimientos por conciliar |
| `CIERRE_SEMANAL_CONTABILIZACION` | SLA semanal contabilización |
| `CIERRE_SEMANAL_CONCILIACION` | SLA semanal conciliación |
| `CIERRE_MENSUAL_CONTABILIZACION` | SLA mensual contabilización |
| `CIERRE_MENSUAL_CONCILIACION` | SLA mensual conciliación |

### Mapeo Empresas

El archivo `bridge/company_map.json` mapea alias Odoo → company_id SGCA:

```json
{
  "FactorIT": { "tenant_id": "...", "company_id": "..." },
  "FactorIT2": { "tenant_id": "...", "company_id": "..." }
}
```

Este archivo se genera desde `sgca-core/scripts/seed_factorit_two_companies.py`.

### Checkpoint

- **Tag:** `checkpoint/factorit-pipeline-v1-bridge`
- **Fecha:** 2025-12-23
- **Repo relacionado:** `sgca-core` tag `checkpoint/factorit-pipeline-v1-core`

---

*Última actualización: 23 Diciembre 2025*
