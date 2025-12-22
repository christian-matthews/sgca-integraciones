# SGCA - Sistema de Gestión y Control Administrativo

Sistema modular para integración con APIs de ERPs (Skualo, Odoo, etc.)

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
│   │   ├── api_summary.md    # Resumen API
│   │   ├── consultas_soporte.md
│   │   ├── webhooks.md
│   │   └── control_pendientes.md
│   └── scripts/              # Scripts de desarrollo
│       ├── balance_excel.py
│       ├── test-connection.js
│       └── ...
│
├── odoo/                      # (Futuro) API Odoo
├── common/                    # Código compartido
│
├── generados/                 # Archivos generados (ignorados)
├── temp/                      # Archivos temporales (ignorados)
│
├── .env                       # Variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Instalación

```bash
# Clonar
git clone https://github.com/christian-matthews/SGCA-SKUALOAPI.git
cd SGCA-SKUALOAPI

# Dependencias
pip install -r requirements.txt

# Configurar token
echo "SKUALO_API_TOKEN=tu-token" > .env
```

## 💻 Uso - Skualo

### CLI Directo

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

# Setup empresa
ctrl.setup_empresa('77285542-7')

# Controles
ctrl.movimientos_bancarios_pendientes('77285542-7')
ctrl.documentos_por_aprobar_sii('77285542-7')
ctrl.documentos_por_contabilizar('77285542-7')

# Balance Excel
ctrl.generar_balance_excel('77285542-7', '202511')
```

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

## 📝 Empresas Configuradas

| Alias | RUT | Nombre |
|-------|-----|--------|
| FIDI | 77285542-7 | Fidi SpA |
| CISI | 77949039-4 | Constructora CISI |

## 🔗 Integración con Bot Telegram

Ver [GIT_FILES.md](GIT_FILES.md) para detalles de integración.

## 📖 Documentación

- [API Summary](skualo/docs/api_summary.md)
- [Webhooks](skualo/docs/webhooks.md)
- [Control de Pendientes](skualo/docs/control_pendientes.md)
- [Consultas Soporte](skualo/docs/consultas_soporte.md)
