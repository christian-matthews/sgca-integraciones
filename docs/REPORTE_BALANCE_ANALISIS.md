# Reporte Balance + Análisis por Cuenta

> **Versión:** 2.0  
> **Última actualización:** 2 Enero 2026

---

## Descripción

Genera un reporte Excel completo con:
- **Resumen**: Balance Clasificado + Estado de Resultados + KPIs
- **EEFF Comparativos**: Trimestres (Mar/Jun/Sep/Dic) del año
- **Documentación**: Agrupaciones y fórmulas utilizadas
- **Balance Tributario**: Todas las cuentas con saldos
- **Análisis por Cuenta**: Una hoja por cada cuenta con movimientos

---

## Ejecución Rápida

### Skualo

```bash
cd sgca-integraciones/skualo/scripts
python3 balance_excel.py
```

**Configuración en el script:**
```python
tenant_key = "FIDI"          # Cambiar por: FIDI, CISI, WINGMAN
id_periodo = "202512"        # Período YYYYMM
fecha_corte = "2025-12-31"   # Fecha de corte YYYY-MM-DD
```

### Odoo

```bash
cd sgca-integraciones/odoo/scripts
python3 balance_excel_odoo.py  # TODO: Implementar
```

---

## Requisitos

### Variables de Entorno

```bash
# .env en sgca-integraciones/
SKUALO_API_TOKEN=xxx         # Token de API Skualo
ODOO_HOST=xxx                # Host PostgreSQL Odoo
ODOO_USER=xxx                # Usuario Odoo
ODOO_PASSWORD=xxx            # Password Odoo
```

### Dependencias Python

```bash
pip install requests pandas openpyxl python-dotenv
```

---

## Estructura del Reporte

### 1. Hoja "Resumen"

| Sección | Contenido |
|---------|-----------|
| Balance Clasificado | Activos, Pasivos, Patrimonio agrupados |
| Estado de Resultados | Ingresos, Costos, Gastos, EBIT, Utilidad Neta |
| KPIs | Margen Bruto, Margen Neto, ROA, ROE, Ratio Endeudamiento |

### 2. Hoja "EEFF Comparativos"

| Período | Descripción |
|---------|-------------|
| Mar YYYY | Cierre Q1 |
| Jun YYYY | Cierre Q2 |
| Sep YYYY | Cierre Q3 |
| Dic YYYY | Cierre Q4 |

**Nota:** Si el período actual no es fin de trimestre, se agrega el mes actual.

### 3. Hoja "Documentación"

- Definición de grupos del Balance Clasificado
- Fórmulas del Estado de Resultados
- Cálculo de KPIs

### 4. Hoja "Balance Tributario"

Todas las cuentas con:
- Código, Nombre
- Débitos, Créditos
- Saldo Deudor, Saldo Acreedor
- Activos, Pasivos
- Pérdidas, Ganancias
- Hipervínculo "→ Ver" a hoja de análisis

### 5. Hojas de Análisis por Cuenta

Una hoja por cada cuenta con saldo ≠ 0:
- Fecha, Comprobante, Tipo
- Auxiliar (si aplica)
- Glosa
- Debe, Haber, Saldo
- Hipervínculo "← Volver al Balance Tributario"

---

## Navegación en Excel

```
┌─────────────────────────────────────────────────────────────┐
│  RESUMEN                                                    │
│  ├── Balance Clasificado                                    │
│  ├── Estado de Resultados                                   │
│  └── KPIs                                                   │
│       ↓ (hipervínculo "Ver comparativos")                   │
├─────────────────────────────────────────────────────────────┤
│  EEFF COMPARATIVOS                                          │
│  ← Volver al Resumen                                        │
├─────────────────────────────────────────────────────────────┤
│  DOCUMENTACIÓN                                              │
│  ← Volver al Resumen                                        │
├─────────────────────────────────────────────────────────────┤
│  BALANCE TRIBUTARIO                                         │
│  ← Volver al Resumen                                        │
│  │                                                          │
│  │  Cuenta 1107001  → Ver  ─────┐                          │
│  │  Cuenta 2110001  → Ver  ─────┼───────────────────┐       │
│  │  ...                         │                   │       │
├─────────────────────────────────────────────────────────────┤
│  1107001 Deudores Comerc...     ◄───────────────────┘       │
│  ← Volver al Balance Tributario                             │
│  (movimientos detallados)                                   │
├─────────────────────────────────────────────────────────────┤
│  2110001 Proveedores            ◄───────────────────────────┘
│  ← Volver al Balance Tributario                             │
│  (movimientos detallados)                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Empresas Configuradas

### Skualo

| Alias | RUT | Nombre | Archivo Config |
|-------|-----|--------|----------------|
| FIDI | 77285542-7 | Fidi SpA | `config/tenants.json` |
| CISI | 77949039-4 | CISITEL SpA | `config/tenants.json` |
| WINGMAN | 77285645-8 | The Wingman SpA | `config/tenants.json` |

### Odoo (TODO)

| Database | Empresa | Conexión |
|----------|---------|----------|
| factorit_ltda | FactorIT Ltda | PostgreSQL directo |
| factorit_spa | FactorIT SpA | PostgreSQL directo |

---

## Archivos Generados

```
sgca-integraciones/skualo/scripts/generados/
└── Balance_PorCuenta_{EMPRESA}_{PERIODO}_{TIMESTAMP}.xlsx
```

Ejemplo:
```
Balance_PorCuenta_FIDI_202512_20260102_144255.xlsx
```

---

## Próximos Pasos

### Skualo ✅
- [x] Períodos trimestrales dinámicos (Mar/Jun/Sep/Dic)
- [x] Hipervínculos corregidos (cuentas → Balance Tributario)
- [x] Documentación

### Odoo 🔜
- [ ] Crear `odoo/scripts/balance_excel_odoo.py`
- [ ] Mapear queries equivalentes a Skualo
- [ ] Generar Excel con misma estructura

---

## Código Fuente

| Sistema | Archivo |
|---------|---------|
| Skualo | `skualo/scripts/balance_excel.py` |
| Odoo | `odoo/scripts/balance_excel_odoo.py` (TODO) |

---

*Documento generado para SGCA - Sistema de Gestión y Control Automatizado*
