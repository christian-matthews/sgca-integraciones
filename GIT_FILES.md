# Archivos para Git

## ✅ Archivos que SÍ deben subirse

### Core del Sistema
```
skualo_control.py           # CLI principal
skualo/
├── __init__.py             # Módulo Python
├── config.py               # Gestión de configuración
└── control.py              # Clase SkualoControl (CORE)
```

### Configuración y Documentación
```
README.md                   # Documentación principal
requirements.txt            # Dependencias Python
.gitignore                  # Archivos a ignorar
tenants.json                # Lista de empresas (RUTs)
```

### Documentación Adicional (opcional)
```
docs/
└── control_pendientes.md   # Documentación técnica
skualo_api_summary.md       # Resumen de endpoints API
config/
└── ids_referencia_FIDI.md  # Referencia de IDs
```

---

## ❌ Archivos que NO deben subirse

### Sensibles
```
.env                        # Token de API (NUNCA subir)
config/empresas/*.json      # Configuraciones con datos de empresas
```

### Generados
```
generados/                  # Excel generados
*.xlsx                      # Archivos Excel
*.xml                       # Documentos XML
```

### Datos descargados
```
balance_*.json              # Balances descargados
response_*.json             # Respuestas de API
analisis_*.json             # Análisis descargados
cisi_*.json                 # Datos de CISI
cuentas_*.json              # Datos de cuentas
comprobantes_*.json         # Comprobantes
bancos_*.json               # Movimientos bancarios
```

### Scripts de prueba/exploración
```
explore-*.py                # Scripts de exploración
balance_excel.py            # Versión anterior
balance_excel_v2.py         # Versión anterior
control_pendientes.py       # Versión anterior (reemplazado por skualo_control.py)
crear_config_excel.py       # Script auxiliar
```

### Node.js (si no lo usas)
```
node_modules/
package.json
package-lock.json
*.js
```

---

## Comando para Git

```bash
# Inicializar repo
git init

# Agregar archivos principales
git add README.md
git add requirements.txt
git add .gitignore
git add tenants.json
git add skualo_control.py
git add skualo/

# Agregar documentación
git add docs/
git add skualo_api_summary.md

# Verificar
git status

# Commit inicial
git commit -m "Initial commit: Skualo Control v1.0"

# Agregar remoto
git remote add origin <tu-url-git>

# Push
git push -u origin main
```

---

## Clonar en otra carpeta

```bash
# Clonar
git clone <tu-url-git> skualo-control

# Entrar
cd skualo-control

# Instalar dependencias
pip install -r requirements.txt

# Crear .env
echo "SKUALO_API_TOKEN=tu-token-aqui" > .env

# Configurar empresa
python skualo_control.py setup 77285542-7

# ¡Listo para usar!
python skualo_control.py reporte 77285542-7
```

---

## Integrar con tu Bot

En tu proyecto del bot:

```python
# Opción 1: Clonar como submódulo
# git submodule add <url> skualo-control

# Opción 2: Copiar el módulo skualo/
# cp -r skualo-control/skualo ./

# Opción 3: Agregar al path
import sys
sys.path.append('/ruta/a/skualo-control')

# Usar
from skualo import SkualoControl
ctrl = SkualoControl()
```

