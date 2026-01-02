# TRANSTECNIA API - Documentación SGCA

> **Estado:** ✅ Documentado  
> **Fuente original:** `APIs/TRANSTECNIA_API_BIBLIA_SGCA.md`  
> **Última actualización:** 2 Enero 2026

---

## 1. Introducción

**Transtecnia** provee el **Ecosistema Fintech Contable (EFC)** con API REST para:
- Lectura de datos base (Plan de cuentas, Centros de costo, Terceros)
- Generación de reportes (Libro Diario, Mayor, Balance)
- Carga de comprobantes contables (Vouchers)

### Ambientes

| Ambiente | URL |
|----------|-----|
| **QA** | `https://conta-qa.transtecniasa.cl` |
| **Producción** | `https://contabilidad-digital.transtecnia.cl` |

---

## 2. Autenticación

Sistema de Tokens basado en credenciales de usuario.

### Obtener Token

```http
POST /api/token/
Content-Type: application/json

{
  "username": "11111111-1",  // RUT Usuario
  "password": "tu_password"
}
```

**Respuesta:**
```json
{
  "token": "a1b2c3d4e5...",
  "email": "usuario@empresa.cl",
  "client_id": 123,
  "client_rut": "77123456-8"
}
```

**Uso en requests:**
```http
Authorization: Token a1b2c3d4e5...
```

---

## 3. API de Lectura (Datos Base)

### 3.1 Plan de Cuentas

```http
GET /api/integration/plan_list/
?company_code={code}
&company_rut={rut}
&year={año}
```

**Respuesta:** Lista de cuentas con `code`, `name`, `accounting_type`

| accounting_type | Significado |
|-----------------|-------------|
| 1 | Activo |
| 2 | Pasivo |
| 3 | Patrimonio |
| 4 | Resultado |

### 3.2 Centros de Resultado

```http
GET /api/integration/result_list/
?company_code={code}
&company_rut={rut}
&year={año}
```

### 3.3 Clientes y Proveedores

```http
GET /api/integration/client_list/
?company_code={code}
&company_rut={rut}
&page={num}
```

---

## 4. API de Reportes

### 4.1 Libro Diario

```http
GET /api/reports/daily_book/
?date_from=01/01/2025
&date_to=31/12/2025
&company_code={code}
&company_rut={rut}
```

**Respuesta:**
```json
{
  "all_voucher": [
    {
      "number": 1,
      "date": "02/01/2025",
      "voucher_type": "Ingreso",
      "movements": [
        { "account": "110101", "debit": 1000, "assets": 0, "gloss": "Pago Fac..." }
      ]
    }
  ]
}
```

### 4.2 Libro Mayor

```http
GET /api/reports/ledger_book/
?month_from=1
&month_to=12
&accounting_plan_from=1000000
&accounting_plan_to=9999999
&type=cuenta/mes
```

### 4.3 Balance de Comprobación

```http
GET /api/reports/balance_check_samples/
?month_from=1
&month_to=12
&current_year=2025
```

---

## 5. API de Escritura (Carga de Vouchers)

### Carga Masiva CSV

```http
POST /api/vouchers/add
Authorization: Token {token}
Content-Type: multipart/form-data

vod_file: archivo.csv
rut: 76123456-K
code: EMPRESA01
year: 2025
month: 12
```

### Formato CSV

Separador: `;` | Encoding: `UTF-8`

| Columna | Descripción |
|---------|-------------|
| CodEmpresa | Código interno |
| RutEmpresa | RUT empresa |
| Año, Mes, Dia | Fecha del voucher |
| Tipo | I=Ingreso, E=Egreso, T=Traspaso |
| Numero | Número correlativo |
| TipoGeneracion | Tipo generación |
| EvouID | ID único del voucher |
| GlosaGeneral | Descripción general |
| Cuenta | Código plan de cuentas |
| Glosa | Detalle de la línea |
| CentroResultado | Código centro costo |
| Debe | Monto debe |
| Haber | Monto haber |
| DocTipo | Tipo documento |
| DocNumero | Número documento |
| DocVencimiento | Fecha vencimiento |
| Rut | RUT tercero |
| Extranjero | Flag extranjero |
| Nombre | Nombre tercero |
| Direccion | Dirección |
| Comuna | Comuna |
| TipoTrib | Tipo tributario |

**Validaciones:**
- ✅ Suma Debe = Suma Haber por cada `EvouID`
- ✅ Cuentas y Centros de Costo deben existir

---

## 6. Errores Comunes

| Código | Error | Solución |
|--------|-------|----------|
| 401 | Unauthorized | Token vencido, renovar |
| 404 | Not Found | Empresa no existe |
| 400 | INVALID_YEAR | Año cerrado o no existe |
| 400 | COMPANY_NOT_FOUND | RUT/Código no coinciden |
| 400 | CSV inválido | Verificar UTF-8 y columnas |

---

## 7. Implementación SGCA

### Endpoints Útiles para Control

| Control | Endpoint | Uso |
|---------|----------|-----|
| **Balance** | `/api/reports/balance_check_samples/` | Estado financiero |
| **Libro Mayor** | `/api/reports/ledger_book/` | Detalle por cuenta |
| **Libro Diario** | `/api/reports/daily_book/` | Movimientos cronológicos |

### Estructura Propuesta

```
sgca-integraciones/transtecnia/
├── __init__.py
├── auth.py          # Manejo de tokens
├── client.py        # Cliente API
├── pendientes.py    # Lógica de pendientes
└── reports/
    └── balance_excel.py
```

---

## 8. Comparación con Otros ERPs

| Aspecto | Skualo | Odoo | Transtecnia |
|---------|--------|------|-------------|
| API REST | ✅ | ❌ | ✅ |
| Autenticación | Bearer Token | PostgreSQL | Token usuario |
| Webhooks | ✅ | ❌ | ❌ |
| Carga de datos | ❌ | ✅ SQL | ✅ CSV |
| Libro Mayor | ✅ | ✅ | ✅ |
| Balance | ✅ | ✅ | ✅ |

---

## 9. Próximos Pasos

1. [ ] Identificar empresas SGCA con Transtecnia
2. [ ] Obtener credenciales de sandbox
3. [ ] Crear módulo `transtecnia/`
4. [ ] Implementar `pendientes.py`
5. [ ] Integrar con bridge

---

*Documento consolidado desde `APIs/TRANSTECNIA_API_BIBLIA_SGCA.md`*
