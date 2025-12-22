# Sistema de Generación de Estados Financieros

Sistema parametrizable para generar reportes financieros desde Skualo ERP.

---

## 📁 Estructura de Archivos

```
SGCA/
├── balance_excel_v2.py          # Script principal (parametrizable)
├── balance_excel.py             # Script original FIDI (no modificar)
├── config/
│   ├── empresas_config.xlsx     # ⭐ CONFIGURACIÓN (una hoja por empresa)
│   └── documentacion.json       # Documentación compartida (fórmulas, KPIs)
├── generados/                   # Carpeta de salida (auto-creada)
│   └── Balance_PorCuenta_{EMPRESA}_{PERIODO}_{TIMESTAMP}.xlsx
└── .env                         # Token API (SKUALO_API_TOKEN)
```

---

## 🚀 Uso

```bash
# Generar reporte para FIDI
python3 balance_excel_v2.py FIDI

# Generar reporte para CISI
python3 balance_excel_v2.py CISI
```

---

## 📊 Qué Genera

Cada archivo Excel contiene:

| Hoja | Contenido |
|------|-----------|
| **Resumen** | Balance Clasificado + Estado de Resultados + KPIs |
| **EEFF Comparativos** | Balance y EERR comparativo (múltiples períodos) |
| **Documentación** | Agrupaciones de cuentas y fórmulas usadas |
| **Balance Tributario** | Todas las cuentas con saldos |
| **{Código} {Cuenta}** | Análisis detallado por cuenta (movimientos) |

---

## ⚙️ Configuración por Empresa

### Archivo: `config/empresas_config.xlsx`

Cada **hoja** del Excel es una empresa diferente (FIDI, CISI, etc.)

### Secciones en cada hoja:

| Sección | Campos |
|---------|--------|
| **TENANT** | key, rut, nombre |
| **PERIODOS** | actual, fecha_corte, tasa_impuesto |
| **PERIODOS_COMPARATIVOS** | ID Periodo, Nombre |
| **BALANCE_CLASIFICADO** | Categoría, Nombre, Prefijos, Excluir, Específicas |
| **ESTADO_RESULTADOS** | Tipo, Key, Nombre, Cuentas, Descripción |
| **OUTPUT** | carpeta, prefijo_archivo |

### Ejemplo visual de la hoja FIDI:

```
┌─────────────────────────────────────────────────────────────────┐
│ TENANT                                                          │
├─────────────┬──────────────────────────────────────────────────┤
│ Campo       │ Valor                                             │
├─────────────┼──────────────────────────────────────────────────┤
│ key         │ FIDI                                              │
│ rut         │ 77285542-7                                        │
│ nombre      │ Fidi SpA                                          │
├─────────────┴──────────────────────────────────────────────────┤
│ PERIODOS                                                        │
├─────────────┬──────────────────────────────────────────────────┤
│ actual      │ 202511                                            │
│ fecha_corte │ 2025-11-30                                        │
│ tasa_impuesto│ 0.27                                             │
├─────────────┴──────────────────────────────────────────────────┤
│ BALANCE_CLASIFICADO                                             │
├──────────────────┬─────────────┬─────────┬──────────┬──────────┤
│ Categoría        │ Nombre      │ Prefijos│ Excluir  │ Específ. │
├──────────────────┼─────────────┼─────────┼──────────┼──────────┤
│ activo_corriente │ Act.Corr.   │ 11      │ 1109009  │          │
│ intangibles      │ Intangibles │         │          │ 1109009  │
└──────────────────┴─────────────┴─────────┴──────────┴──────────┘
```

---

## 📐 Reglas de Clasificación

### Balance Clasificado

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `prefijos` | Códigos que empiezan con... | `["11"]` = cuentas 11xxxxx |
| `excluir_cuentas` | Cuentas a excluir del grupo | `["1109009"]` |
| `cuentas_especificas` | Cuentas exactas (prioridad) | `["1109009", "1301001"]` |

**Orden de prioridad:**
1. `cuentas_especificas` (primero)
2. `prefijos` con `excluir_cuentas`

### Estado de Resultados

Cada grupo define:
- `nombre`: Nombre a mostrar
- `cuentas`: Array de códigos de cuenta
- `descripcion`: Para documentación

---

## 📈 KPIs Calculados

| KPI | Fórmula |
|-----|---------|
| Margen Bruto | (Utilidad Bruta / Ingresos) × 100 |
| Margen Operacional | (EBIT / Ingresos) × 100 |
| Margen Neto | (Resultado Neto / Ingresos) × 100 |
| ROA | (Resultado Neto / Total Activos) × 100 |
| ROE | (Resultado Neto / Patrimonio) × 100 |
| Ratio Endeudamiento | (Total Pasivos / Total Activos) × 100 |

---

## 📝 Documentación Compartida

El archivo `config/documentacion.json` contiene:
- Definiciones de KPIs
- Fórmulas del Estado de Resultados
- Notas generales

Este archivo es **compartido** entre todas las empresas. Las secciones de agrupación de cuentas se generan dinámicamente desde el config de cada empresa.

---

## 🔧 Agregar Nueva Empresa

1. **Abrir** `config/empresas_config.xlsx`

2. **Copiar hoja FIDI:**
   - Clic derecho en pestaña FIDI → "Mover o copiar"
   - Marcar "Crear una copia"
   - Renombrar la hoja con el KEY (ej: CISI)

3. **Editar la nueva hoja:**
   - Cambiar TENANT (key, rut, nombre)
   - Ajustar BALANCE_CLASIFICADO según plan de cuentas
   - Ajustar ESTADO_RESULTADOS según cuentas
   - Definir PERIODOS_COMPARATIVOS

4. **Guardar y ejecutar:**
   ```bash
   python3 balance_excel_v2.py CISI
   ```

---

## 🔑 Requisitos

### Dependencias Python
```bash
pip3 install requests pandas openpyxl python-dotenv
```

### Variables de Entorno
Archivo `.env`:
```
SKUALO_API_TOKEN=tu_token_aqui
```

---

## 📡 API Skualo

El sistema consume estos endpoints:

| Endpoint | Uso |
|----------|-----|
| `/contabilidad/reportes/balancetributario/{periodo}` | Balance Tributario |
| `/contabilidad/reportes/analisisporcuenta/{cuenta}` | Movimientos por cuenta |

---

## 📂 Archivos Generados

Formato del nombre:
```
Balance_PorCuenta_{EMPRESA}_{PERIODO}_{YYYYMMDD_HHMMSS}.xlsx
```

Ejemplo:
```
generados/Balance_PorCuenta_FIDI_202511_20251220_225012.xlsx
```

---

## 🏷️ Versiones

| Archivo | Descripción |
|---------|-------------|
| `balance_excel.py` | Original (hardcoded para FIDI) |
| `balance_excel_v2.py` | Parametrizable (usa config JSON) |

---

*Última actualización: Diciembre 2024*

