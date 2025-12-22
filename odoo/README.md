# Módulo Odoo - Integración PostgreSQL

Módulo para conectar directamente a bases de datos Odoo (PostgreSQL) y extraer información contable.

---

## 🏢 Empresas Configuradas

| Alias | Base de Datos | Empresa |
|-------|---------------|---------|
| FactorIT | FactorIT | FactorIT SpA |
| FactorIT2 | FactorIT2 | FactorIT Ltda |

---

## ⚙️ Configuración

### Variables de Entorno (`.env`)

```bash
# PostgreSQL FactorIT/Odoo
SERVER=18.223.205.221
PORT=5432
DB_USER=Hector
PASSWORD=tu_password
```

> ⚠️ **Importante:** Usar `DB_USER` en lugar de `USER` para evitar conflicto con la variable del sistema operativo.

### Dependencias

```bash
pip install psycopg2-binary
```

---

## 🚀 Uso

### Test de Conexión

```bash
python -m odoo.test_connection
```

**Salida esperada:**
```
============================================================
   TEST DE CONEXIÓN - FACTORIT (ODOO/POSTGRESQL)
============================================================

📋 Verificando configuración...
   ✅ HOST: 18.223.205.221
   ✅ USER: Hector
   ✅ PASSWORD: **************
   ✅ PORT: 5432

🔌 Probando conexión: FactorIT SpA (DB: FactorIT)
   ✅ Conexión exitosa
   📊 PostgreSQL: PostgreSQL 10.23
   ✅ 6 documentos pendientes encontrados

🔌 Probando conexión: FactorIT Ltda (DB: FactorIT2)
   ✅ Conexión exitosa
   ✅ 8 documentos pendientes encontrados

============================================================
   RESUMEN DE CONEXIONES
============================================================
   ✅ FactorIT SpA (FactorIT): 6 docs pendientes
   ✅ FactorIT Ltda (FactorIT2): 8 docs pendientes
============================================================
```

### Como Módulo Python

```python
from odoo.test_connection import test_connection, DATABASES

# Probar una base de datos específica
resultado = test_connection('FactorIT', DATABASES['FactorIT'])

if resultado['success']:
    print(f"Pendientes: {resultado['pendientes']}")
    for doc in resultado['datos']:
        print(doc)
```

---

## 📄 Query: Documentos Pendientes SII

```sql
SELECT 
    a.date,              -- Fecha del documento
    b.doc_code_prefix,   -- Tipo (FAC, FNA, etc.)
    a.number,            -- Número/Folio
    a.new_partner,       -- RUT + Nombre proveedor
    a.amount             -- Monto
FROM mail_message_dte_document a,
     sii_document_class b
WHERE a.state = 'draft'          -- Solo pendientes (draft)
  AND a.document_class_id = b.id
ORDER BY a.date DESC
```

### Tipos de Documentos

| Prefijo | Descripción |
|---------|-------------|
| FAC | Factura Electrónica |
| FNA | Factura No Afecta o Exenta |
| NCE | Nota de Crédito Electrónica |
| NDE | Nota de Débito Electrónica |

---

## 📊 Resultados Test (21-Dic-2025)

### FactorIT SpA (DB: FactorIT)

| Fecha | Tipo | Número | Proveedor | Monto |
|-------|------|--------|-----------|-------|
| 2025-12-18 | FAC | 67082 | CONVERGIA TELECOM S.A. | $64,807 |
| 2025-12-17 | FAC | 1699 | SCHWENCKE SPA | $2,975,722 |
| 2025-12-17 | FAC | 8380 | Operadora Inmobiliaria Versalles | $234,263 |
| 2025-12-14 | FAC | 857926 | BICE VIDA COMPAÑÍA DE SEGUROS | $769,868 |
| 2025-09-08 | FAC | 3314 | JORGE MEZA Z. Y COMPANIA | $96,490 |
| 2025-07-17 | FAC | 22195 | TD SYNNEX CHILE LIMITADA | $2,942,492 |

**Total:** 6 documentos, **$7,083,642**

### FactorIT Ltda (DB: FactorIT2)

| Fecha | Tipo | Número | Proveedor | Monto |
|-------|------|--------|-----------|-------|
| 2025-12-17 | FNA | 1417 | ASESORIA MERCURIO LIMITADA | $2,252,575 |
| 2025-12-17 | FNA | 117184 | Adm. Serv. Cencosud Ltda. | $118,800 |
| 2025-12-14 | FAC | 859927 | BICE VIDA COMPAÑÍA DE SEGUROS | $2,427,358 |
| 2025-12-02 | FAC | 7617 | SERVICIOS PROFESIONALES IBC | $15,458 |
| 2025-11-04 | FAC | 7498 | SERVICIOS PROFESIONALES IBC | $15,458 |
| 2025-10-03 | FAC | 7412 | SERVICIOS PROFESIONALES IBC | $15,458 |
| 2025-09-03 | FAC | 7284 | SERVICIOS PROFESIONALES IBC | $15,458 |
| 2025-08-05 | FAC | 7150 | SERVICIOS PROFESIONALES IBC | $15,458 |

**Total:** 8 documentos, **$4,876,023**

---

## 🔧 Troubleshooting

### Error: `no pg_hba.conf entry for host`

El servidor PostgreSQL no permite conexiones desde tu IP. Solución:
1. Contactar al administrador del servidor
2. Agregar tu IP al archivo `/etc/postgresql/10/main/pg_hba.conf`
3. Reiniciar PostgreSQL: `sudo systemctl restart postgresql`

### Error: `USER` toma el valor incorrecto

La variable `USER` del sistema operativo tiene prioridad. Usar `DB_USER` en el `.env`.

### Error: `psycopg2 not installed`

```bash
pip install psycopg2-binary
```

---

---

## 🏦 Movimientos Bancarios Pendientes de Conciliar

### Uso

```bash
python -m odoo.bancos_pendientes
```

### Query utilizada

```sql
SELECT 
    bsl.date as fecha,
    aj.name as banco,
    bsl.name as descripcion,
    bsl.amount as monto
FROM account_bank_statement_line bsl
LEFT JOIN account_journal aj ON bsl.journal_id = aj.id
WHERE bsl.move_name IS NULL OR bsl.move_name = ''
ORDER BY aj.name, bsl.date DESC
```

**Criterio:** Un movimiento está **sin conciliar** cuando `move_name IS NULL` (no tiene asiento contable asociado).

### Resultados (21-Dic-2025)

| Empresa | Movimientos | Total Abonos | Total Cargos | Neto |
|---------|-------------|--------------|--------------|------|
| FactorIT SpA | 3,935 | $37,918M | -$37,983M | -$65.5M |
| FactorIT Ltda | 990 | $8,244M | -$8,220M | $23M |

---

## 📊 Balance General + Estado de Resultados

### Uso

```bash
# Generar balance para FactorIT SpA
python -m odoo.balance_excel FactorIT

# Generar balance para FactorIT Ltda
python -m odoo.balance_excel FactorIT2

# Con fecha de corte específica
python -m odoo.balance_excel FactorIT 2025-11-30
```

### Características

- **Balance Clasificado**: Activos, Pasivos, Patrimonio
- **Estado de Resultados**: Ingresos, Costos, Gastos, Resultado Neto
- **KPIs Financieros**: Margen Bruto, ROA, ROE, etc.
- **Hojas de Detalle**: Movimientos por cuenta con hipervínculos
- **Verificación de Cuadratura**: Activos = Pasivos + Patrimonio

### Clasificación de Cuentas

| Prefijo | Clasificación |
|---------|---------------|
| 11xx | Activo Corriente |
| 12xx, 13xx, 14xx | Activo No Corriente |
| 21xx | Pasivo Corriente |
| 22xx, 23xx | Pasivo No Corriente |
| 3xxx | Patrimonio |
| 4xxx | Ingresos Operacionales |
| 51xx | Costos de Venta |
| 52xx-55xx | Gastos Operacionales |
| 6xxx | Otros Ingresos (No Operacionales) |
| 7xxx | Otros Gastos (No Operacionales) |
| 8xxx | Saldos de Apertura |

### Resultado Ejemplo

```
======================================================================
   GENERANDO BALANCE - FactorIT SpA
======================================================================
   Fecha de corte: 2025-12-22

📊 Obteniendo balance...
   146 cuentas con movimientos

📋 Resumen:
   Total Activos:      $     3,347,939,674
   Total Pasivos:      $     1,500,319,072
   Patrimonio base:    $      -126,297,842
   Resultado Período:  $     1,957,463,010
   Ajustes Apertura:   $        16,455,434
   Total Patrimonio:   $     1,847,620,602
   Pasivos+Patrimonio: $     3,347,939,674
   ✅ CUADRA

📝 Generando Excel...
   Generando hojas de detalle...
   115 cuentas con detalle

✅ Archivo generado: Balance_Odoo_FactorIT_202512_20251222.xlsx
======================================================================
```

---

## 📁 Estructura

```
odoo/
├── __init__.py           # Módulo principal
├── test_connection.py    # Test de conexión + query pendientes SII
├── bancos_pendientes.py  # Movimientos bancarios sin conciliar
├── balance_excel.py      # Generador de Balance + Estado de Resultados
├── explore_db.py         # Explorador de tablas
└── README.md             # Esta documentación
```

---

*Última actualización: 22 Diciembre 2025*

