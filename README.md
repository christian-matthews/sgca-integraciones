# Skualo Control

Sistema de control y reportes contables para Skualo ERP.

## Instalación

```bash
# Clonar repositorio
git clone <tu-repo>
cd skualo-control

# Instalar dependencias
pip install -r requirements.txt

# Configurar token
cp .env.example .env
# Editar .env y agregar SKUALO_API_TOKEN
```

## Configuración

### Variables de Entorno

Crear archivo `.env`:

```env
SKUALO_API_TOKEN=tu-token-aqui
```

### Setup de Empresa

Antes de usar los reportes, debes configurar cada empresa:

```bash
python skualo_control.py setup 77285542-7
```

El setup detecta automáticamente:
- Nombre de la empresa
- Cuentas bancarias
- Cuenta de clientes y proveedores
- Endpoints disponibles

## Uso por Línea de Comandos

```bash
# Configuración
python skualo_control.py setup <rut>      # Configura empresa
python skualo_control.py listar           # Lista empresas configuradas

# Controles de Pendientes
python skualo_control.py bancos <rut>     # Movimientos sin conciliar
python skualo_control.py aprobar <rut>    # Docs por aprobar en SII
python skualo_control.py contabilizar <rut>  # Docs por contabilizar
python skualo_control.py reporte <rut>    # Reporte completo

# Reportes Contables
python skualo_control.py balance <rut> [periodo]  # Balance en Excel
```

## Uso como Módulo Python

```python
from skualo import SkualoControl

# Inicializar
ctrl = SkualoControl()

# Setup de empresa (primera vez)
ctrl.setup_empresa('77285542-7')

# Controles de pendientes
resultado = ctrl.movimientos_bancarios_pendientes('77285542-7')
resultado = ctrl.documentos_por_aprobar_sii('77285542-7')
resultado = ctrl.documentos_por_contabilizar('77285542-7')

# Reporte completo
resultado = ctrl.reporte_completo('77285542-7')

# Generar balance Excel
archivo = ctrl.generar_balance_excel('77285542-7', '202511')

# Formato para Telegram
texto = ctrl.formato_reporte_telegram('77285542-7')
```

## Integración con Bot de Telegram

```python
from telegram import Update
from telegram.ext import ContextTypes
from skualo import SkualoControl

ctrl = SkualoControl()

async def reporte_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /reporte <rut>"""
    if not context.args:
        await update.message.reply_text("Uso: /reporte <RUT>")
        return
    
    rut = context.args[0]
    texto = ctrl.formato_reporte_telegram(rut)
    await update.message.reply_text(texto, parse_mode='Markdown')

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /balance <rut> [periodo]"""
    if not context.args:
        await update.message.reply_text("Uso: /balance <RUT> [YYYYMM]")
        return
    
    rut = context.args[0]
    periodo = context.args[1] if len(context.args) > 1 else None
    
    await update.message.reply_text("⏳ Generando balance...")
    archivo = ctrl.generar_balance_excel(rut, periodo)
    
    if archivo:
        await update.message.reply_document(
            document=open(archivo, 'rb'),
            filename=os.path.basename(archivo)
        )
    else:
        await update.message.reply_text("❌ Error al generar balance")
```

## Estructura de Archivos

```
skualo-control/
├── .env                    # Variables de entorno (NO subir a Git)
├── .env.example            # Ejemplo de variables
├── .gitignore              # Archivos a ignorar
├── README.md               # Esta documentación
├── requirements.txt        # Dependencias Python
├── skualo_control.py       # CLI principal
├── skualo/                 # Módulo Python
│   ├── __init__.py
│   ├── config.py           # Gestión de configuración
│   └── control.py          # Clase SkualoControl
├── config/
│   └── empresas/           # Configuraciones de empresas
│       ├── 77285542-7.json
│       └── 77949039-4.json
├── generados/              # Archivos Excel generados
└── docs/                   # Documentación adicional
    └── control_pendientes.md
```

## API de Funciones

### `SkualoControl.setup_empresa(rut)`

Configura una nueva empresa. Solo necesita el RUT.

**Parámetros:**
- `rut` (str): RUT de la empresa (ej: '77285542-7')

**Retorna:**
```python
{
    'rut': '77285542-7',
    'nombre': 'FIDI SPA',
    'cuentas_bancarias': [
        {'codigo': '1102002', 'nombre': 'Banco Santander', 'activa': True}
    ],
    'cuenta_clientes': '1107001',
    'cuenta_proveedores': '2110001',
    'endpoints_disponibles': {...}
}
```

### `SkualoControl.movimientos_bancarios_pendientes(rut)`

Obtiene movimientos bancarios sin conciliar.

**Retorna:**
```python
{
    'empresa': 'FIDI SPA',
    'rut': '77285542-7',
    'fecha': '2025-12-21T22:30:00',
    'cuentas': [
        {
            'codigo': '1102002',
            'nombre': 'Banco Santander',
            'total_movimientos': 470,
            'sin_conciliar': 1,
            'movimientos': [...]
        }
    ],
    'total_sin_conciliar': 1
}
```

### `SkualoControl.documentos_por_aprobar_sii(rut)`

Obtiene documentos pendientes de aprobar en el SII (< 8 días).

**Retorna:**
```python
{
    'empresa': 'CISI',
    'pendientes': [
        {
            'rut_emisor': '89605500-3',
            'emisor': 'Estacion De Servicio',
            'tipo_documento': 'Factura Electrónica',
            'folio': 132285,
            'monto': 60000,
            'dias_restantes': 2
        }
    ],
    'total_pendientes': 2,
    'monto_total': 119482
}
```

### `SkualoControl.documentos_por_contabilizar(rut)`

Obtiene documentos aceptados pero no ingresados al sistema.

**Retorna:**
```python
{
    'empresa': 'CISI',
    'pendientes': [
        {
            'emisor': 'D&J CONSTRUCCIONES SPA',
            'tipo_documento': 'Factura Electrónica',
            'folio': 335,
            'monto': 9639000
        }
    ],
    'ya_contabilizados': 29,
    'total_pendientes': 7,
    'monto_total': 10814071
}
```

### `SkualoControl.reporte_completo(rut)`

Genera reporte con los 3 controles.

**Retorna:**
```python
{
    'empresa': 'CISI',
    'fecha': '2025-12-21T22:30:00',
    'bancos': {...},
    'aprobar': {...},
    'contabilizar': {...},
    'resumen': {
        'movimientos_sin_conciliar': 68,
        'documentos_por_aprobar': 2,
        'documentos_por_contabilizar': 7,
        'documentos_contabilizados': 29
    }
}
```

### `SkualoControl.generar_balance_excel(rut, periodo)`

Genera Excel con Balance Tributario y análisis por cuenta.

**Parámetros:**
- `rut` (str): RUT de la empresa
- `periodo` (str, opcional): Período YYYYMM (default: mes actual)

**Retorna:**
- Ruta del archivo Excel generado

### `SkualoControl.formato_reporte_telegram(rut)`

Genera reporte formateado en Markdown para Telegram.

**Retorna:**
```
📊 *REPORTE DE CONTROL*
_CISI_
_21/12/2025 22:30_

🏦 *Movimientos sin conciliar:* 68
📄 *Docs por aprobar SII:* 2
📋 *Docs por contabilizar:* 7
✅ *Docs contabilizados:* 29
```

## Dependencias

```
requests>=2.28.0
python-dotenv>=1.0.0
pandas>=2.0.0
openpyxl>=3.1.0
```

## Licencia

MIT

