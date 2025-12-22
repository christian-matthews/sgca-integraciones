# SGCA - Sistema de Gestión y Control Administrativo

Sistema modular para integración con APIs de ERPs (Skualo, Odoo/FactorIT).

## 📁 Estructura

```
SGCA/
├── skualo/                    # API Skualo ERP
│   ├── __init__.py           # Módulo principal
│   ├── cli.py                # CLI de comandos
│   ├── config.py             # Gestión de configuración
│   ├── control.py            # Clase SkualoControl
│   ├── config/               # Configuraciones
│   │   ├── tenants.json      # Empresas disponibles
│   │   └── empresas/         # Config por empresa (*.json)
│   ├── docs/                 # Documentación
│   └── scripts/
│       ├── balance_excel_v2.py  # Balance + EERR Excel
│       ├── pendientes.py        # Reporte pendientes JSON
│       └── control_pendientes.py
│
├── odoo/                      # PostgreSQL Odoo (FactorIT)
│   ├── __init__.py           # Módulo principal
│   ├── test_connection.py    # Test de conexión
│   ├── pendientes.py         # Reporte pendientes JSON
│   ├── balance_excel.py      # Balance + EERR Excel
│   ├── bancos_pendientes.py  # Movimientos bancarios
│   └── README.md
│
├── common/                    # Código compartido
├── generados/                 # Archivos Excel (ignorados)
├── temp/                      # Archivos JSON temporales
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

### Skualo

```bash
python -m skualo.scripts.balance_excel_v2
```

### Odoo (FactorIT)

```bash
python -m odoo.balance_excel FactorIT         # FactorIT SpA
python -m odoo.balance_excel FactorIT2        # FactorIT Ltda
python -m odoo.balance_excel FactorIT 2025-11-30  # Con fecha corte
```

### Características

- ✅ Balance Clasificado (Activos, Pasivos, Patrimonio)
- ✅ Estado de Resultados (Ingresos, Costos, Gastos, Resultado Neto)
- ✅ **Resultado del Período incluido en Patrimonio**
- ✅ Verificación de Cuadratura: Activos = Pasivos + Patrimonio
- ✅ KPIs Financieros (Margen Bruto, ROA, ROE)
- ✅ Hojas de detalle por cuenta con hipervínculos

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

*Última actualización: 22 Diciembre 2025*
