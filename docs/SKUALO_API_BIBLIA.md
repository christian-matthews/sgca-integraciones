# Skualo API - Biblia SGCA

> **Versión:** 2.0  
> **Actualizado:** 2 Enero 2026  
> **Documentación oficial:** [docs.skualo.cl](https://docs.skualo.cl/reference/intro)

---

## Índice

1. [Autenticación](#1-autenticación)
2. [Endpoints Validados](#2-endpoints-validados)
3. [Control de Pendientes](#3-control-de-pendientes)
4. [Webhooks](#4-webhooks)
5. [Estados Financieros](#5-estados-financieros)
6. [Implementación SGCA](#6-implementación-sgca)
7. [Tenants Configurados](#7-tenants-configurados)

---

## 1. Autenticación

| Aspecto | Detalle |
|---------|---------|
| **URL Base** | `https://api.skualo.cl/{RUT_EMPRESA}` |
| **Protocolo** | Solo HTTPS |
| **Formato** | JSON |
| **Tenant ID** | RUT con guión (ej: `77285542-7`) |

### Headers Requeridos

```http
Authorization: Bearer TU-TOKEN
Accept: application/json
```

### Obtención de Token

Solicitar a: **soporte@skualo.cl**

---

## 2. Endpoints Validados

### 2.1 Empresa y Maestros

| Endpoint | Descripción |
|----------|-------------|
| `GET /{RUT}/empresa` | Datos de la empresa |
| `GET /{RUT}/empresa/sucursales` | Lista de sucursales |
| `GET /{RUT}/auxiliares` | Clientes/Proveedores (paginado) |
| `GET /{RUT}/productos` | Catálogo de productos |

### 2.2 Contabilidad - Reportes

| Endpoint | Parámetros | Uso |
|----------|------------|-----|
| `GET /{RUT}/contabilidad/reportes/balancetributario/{periodo}` | `periodo`: yyyyMM | Balance mensual |
| `GET /{RUT}/contabilidad/reportes/librodiario` | `Desde`, `Hasta`: yyyy-mm-dd | Libro diario |
| `GET /{RUT}/contabilidad/reportes/libromayor` | Ver abajo | Libro mayor |
| `GET /{RUT}/contabilidad/reportes/librocompras/{periodo}` | `periodo`, `IdSucursal` | Libro de compras |
| `GET /{RUT}/contabilidad/reportes/resultados` | `fechaCorte` (obligatorio) | Estado de resultados |
| `GET /{RUT}/contabilidad/reportes/analisisporauxiliar/{rut}` | RUT auxiliar | Cartera por cliente/proveedor |
| `GET /{RUT}/contabilidad/reportes/analisisporcuenta/{cuenta}` | Código cuenta | Movimientos de cuenta |

**Libro Mayor - Parámetros:**
```
?IdCuentaInicio={codigo}
&IdCuentaFin={codigo}
&desde=2025-01-01
&hasta=2025-12-31
&IdSucursal=0
&IncluyeAjusteTributario=false
```

### 2.3 Bancos

| Endpoint | Descripción |
|----------|-------------|
| `GET /{RUT}/bancos/{idCuenta}` | Movimientos bancarios |
| `GET /{RUT}/bancos/{idCuenta}/{id}` | Movimiento específico |

**Campo clave:** `conciliado: true/false`

**Paginación:** `?PageSize=100&Page=1`

### 2.4 Documentos (DTE)

| Endpoint | Descripción |
|----------|-------------|
| `GET /{RUT}/documentos/{GUID}` | Documento por ID interno |
| `GET /{RUT}/documentos/{tipoInterno}/{folio}` | Por tipo + folio |
| `GET /{RUT}/documentos/{id}/xml` | XML del documento |

**Tipos internos:** FAVE (Venta), FACE (Compra), NCVE, NCCE, etc.

### 2.5 SII - DTEs

| Endpoint | Descripción |
|----------|-------------|
| `GET /{RUT}/sii/dte` | DTEs emitidos (ventas) |
| `GET /{RUT}/sii/dte/recibidos` | **DTEs recibidos (compras)** |

**Campos clave DTE recibido:**
```json
{
  "idDocumento": "uuid",
  "rutEmisor": "12345678-9",
  "emisor": "Proveedor SPA",
  "idTipoDocumento": 33,
  "folio": 12345,
  "fechaEmision": "2025-12-15",
  "montoTotal": 1000000,
  "creadoEl": "2025-12-16T10:30:00",
  "fechaRespuesta": null,
  "conAcuseRecibo": false
}
```

### 2.6 Tablas de Referencia

| Endpoint | Descripción |
|----------|-------------|
| `GET /{RUT}/tablas/sii/tiposdocs` | 65 tipos DTE del SII |
| `GET /{RUT}/tablas/tiposdocumentos` | 27 tipos internos |
| `GET /{RUT}/tablas/centroscostos` | Centros de costo |
| `GET /{RUT}/tablas/bancos` | Catálogo de bancos (43) |

**Tipos DTE principales:**

| ID | Documento |
|----|-----------|
| 33 | Factura Electrónica |
| 34 | Factura No Afecta/Exenta |
| 39 | Boleta Electrónica |
| 46 | Factura de Compra |
| 61 | Nota Crédito Electrónica |
| 56 | Nota Débito Electrónica |

---

## 3. Control de Pendientes

### 3.1 Pendientes por Aceptar en SII

**Regla de negocio:** DTE tiene **8 días naturales** para aceptar/rechazar. Después = aceptación tácita.

```python
from datetime import datetime

# Obtener DTEs recibidos
GET /{RUT}/sii/dte/recibidos?PageSize=100

hoy = datetime.now()
pendientes = []

for dte in items:
    if dte['fechaRespuesta']:
        continue  # Ya respondido
    
    fecha_recep = datetime.fromisoformat(dte['creadoEl'].split('.')[0])
    dias = (hoy - fecha_recep).days
    
    if dias <= 8:
        pendientes.append(dte)  # Pendiente de aceptar
```

### 3.2 Pendientes de Contabilizar

**Lógica:** DTEs aceptados que NO están en el libro de compras.

```python
# 1. Obtener DTEs aceptados (> 8 días o con fechaRespuesta)
aceptados = [d for d in dtes if d['fechaRespuesta'] or dias > 8]

# 2. Obtener folios del libro de compras
libro = GET /{RUT}/contabilidad/reportes/librocompras/202512
folios_contabilizados = {item['NumDoc'] for item in libro}

# 3. Cruzar
pendientes = [d for d in aceptados if str(d['folio']) not in folios_contabilizados]
```

**Mapeo de tipos:**

| Tipo DTE | Tipo Interno |
|----------|--------------|
| 33 | FACE |
| 34 | FXCE |
| 61 | NCCE |
| 56 | NDCE |

### 3.3 Pendientes de Conciliar

**Proceso:**

1. Obtener cuentas bancarias del balance (códigos `1102xxx`)
2. Para cada cuenta, obtener movimientos
3. Filtrar donde `conciliado = false`

```python
# Identificar cuentas de banco
balance = GET /{RUT}/contabilidad/reportes/balancetributario/{periodo}
cuentas_banco = [c for c in balance if c['idCuenta'].startswith('1102')]

# Obtener movimientos no conciliados
for cuenta in cuentas_banco:
    movimientos = GET /{RUT}/bancos/{cuenta['idCuenta']}?PageSize=100
    sin_conciliar = [m for m in movimientos if not m['conciliado']]
```

### Resumen de Endpoints para Pendientes

| Control | Endpoint Principal | Campo Clave |
|---------|-------------------|-------------|
| Aceptar SII | `/sii/dte/recibidos` | `fechaRespuesta = null` + días ≤ 8 |
| Contabilizar | `/sii/dte/recibidos` + `/contabilidad/reportes/librocompras/{periodo}` | Cruce de folios |
| Conciliar | `/bancos/{idCuenta}` | `conciliado = false` |

---

## 4. Webhooks

### Tipos de Eventos

| Objeto | Eventos |
|--------|---------|
| **Documentos** | `DOCUMENTO_CREATED`, `DOCUMENTO_UPDATED`, `DOCUMENTO_DELETED` |
| **Comprobantes** | `COMPROBANTE_CREATED`, `COMPROBANTE_UPDATED`, `COMPROBANTE_DELETED` |
| **Auxiliares** | `AUXILIAR_CREATED`, `AUXILIAR_UPDATED` |
| **Ficha Trabajador** | `FICHA_CREATED`, `FICHA_UPDATED` |

### API de Webhooks

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/{RUT}/integraciones/webhooks` | Listar webhooks |
| `POST` | `/{RUT}/integraciones/webhooks` | Crear webhook |
| `DELETE` | `/{RUT}/integraciones/webhooks/{id}` | Eliminar webhook |

### Crear Webhook

```python
import requests

url = f"https://api.skualo.cl/{RUT}/integraciones/webhooks"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "url": "https://tu-servidor.com/webhook/skualo",
    "eventos": ["DOCUMENTO_CREATED", "COMPROBANTE_CREATED"]
}

response = requests.post(url, headers=headers, json=payload)
# {"id": "uuid-del-webhook", "href": "..."}
```

### Formato de Notificación

```json
{
    "tipoEvento": "DOCUMENTO_CREATED",
    "identificador": "9f077032-f346-495d-8008-005a9449950c"
}
```

**Requisitos del endpoint receptor:**
- Recibir POST con JSON
- Responder 2xx rápidamente
- Procesar de forma asíncrona
- Skualo reintenta hasta 10 veces si falla

---

## 5. Estados Financieros

### Scripts Disponibles

| Script | Uso |
|--------|-----|
| `balance_excel_v2.py` | Genera Excel con Balance + EERR + KPIs |
| `balance_excel.py` | Versión original FIDI |

### Ejecución

```bash
cd sgca-integraciones/skualo
python3 scripts/balance_excel_v2.py FIDI
```

### Contenido del Excel Generado

| Hoja | Contenido |
|------|-----------|
| **Resumen** | Balance Clasificado + Estado de Resultados + KPIs |
| **EEFF Comparativos** | Balance y EERR comparativo |
| **Documentación** | Agrupaciones y fórmulas |
| **Balance Tributario** | Todas las cuentas con saldos |
| **{Código} {Cuenta}** | Análisis detallado por cuenta |

### KPIs Calculados

| KPI | Fórmula |
|-----|---------|
| Margen Bruto | (Utilidad Bruta / Ingresos) × 100 |
| Margen Operacional | (EBIT / Ingresos) × 100 |
| Margen Neto | (Resultado Neto / Ingresos) × 100 |
| ROA | (Resultado Neto / Total Activos) × 100 |
| ROE | (Resultado Neto / Patrimonio) × 100 |

---

## 6. Implementación SGCA

### Archivo Principal

```
sgca-integraciones/skualo/pendientes.py
```

### Uso

```python
from skualo.pendientes import obtener_pendientes_empresa

# Por RUT
data = obtener_pendientes_empresa("77285542-7")

# Por alias
data = obtener_pendientes_empresa("FIDI")
```

### Estructura de Salida (normalizada para bridge)

```json
{
    "empresa": "Fidi SpA",
    "rut": "77285542-7",
    "fecha_consulta": "2025-01-02T10:30:00",
    "pendientes_sii": {
        "cantidad": 5,
        "total": 1500000,
        "documentos": [...]
    },
    "pendientes_contabilizar": {
        "cantidad": 3,
        "documentos": [...]
    },
    "pendientes_conciliar": {
        "cantidad": 14,
        "total_abonos": 15000000,
        "total_cargos": 30000000,
        "movimientos": [...]
    }
}
```

### CLI

```bash
cd sgca-integraciones
python3 -m skualo.pendientes FIDI
```

---

## 7. Tenants Configurados

```json
{
  "FIDI": {
    "rut": "77285542-7",
    "nombre": "Fidi SpA",
    "activo": true
  },
  "CISI": {
    "rut": "77949039-4",
    "nombre": "Constructora, Inmobiliaria, Servicios e Ingenieria SpA",
    "activo": true
  },
  "WINGMAN": {
    "rut": "77285645-8",
    "nombre": "The Wingman SpA",
    "activo": true
  }
}
```

### Agregar Nueva Empresa

1. Editar `skualo/config/tenants.json`
2. Agregar entrada con RUT y nombre
3. Si usa balance Excel: agregar hoja en `config/empresas_config.xlsx`

---

## Apéndice: Matriz de Endpoints

### Validados ✅ (25 endpoints)

| Módulo | Endpoint | Estado |
|--------|----------|--------|
| Empresa | `/empresa` | ✅ |
| Empresa | `/empresa/sucursales` | ✅ |
| Auxiliares | `/auxiliares` | ✅ |
| Productos | `/productos` | ✅ |
| Contabilidad | `/contabilidad/comprobantes/{numero}` | ✅ |
| Contabilidad | `/contabilidad/reportes/balancetributario/{periodo}` | ✅ |
| Contabilidad | `/contabilidad/reportes/librodiario` | ✅ |
| Contabilidad | `/contabilidad/reportes/libromayor` | ✅ |
| Contabilidad | `/contabilidad/reportes/librocompras/{periodo}` | ✅ |
| Contabilidad | `/contabilidad/reportes/resultados` | ✅ |
| Contabilidad | `/contabilidad/reportes/analisisporauxiliar/{rut}` | ✅ |
| Contabilidad | `/contabilidad/reportes/analisisporcuenta/{cuenta}` | ✅ |
| Bancos | `/bancos/{idCuenta}` | ✅ |
| Bancos | `/bancos/{idCuenta}/{id}` | ✅ |
| Documentos | `/documentos/{GUID}` | ✅ |
| Documentos | `/documentos/{tipo}/{folio}` | ✅ |
| Documentos | `/documentos/{id}/xml` | ✅ |
| SII | `/sii/dte` | ✅ |
| SII | `/sii/dte/recibidos` | ✅ |
| Tablas | `/tablas/sii/tiposdocs` | ✅ |
| Tablas | `/tablas/tiposdocumentos` | ✅ |
| Tablas | `/tablas/centroscostos` | ✅ |
| Tablas | `/tablas/bancos` | ✅ |
| Webhooks | `/integraciones/webhooks` (GET/POST) | ✅ |
| Webhooks | `/integraciones/webhooks/{id}` (DELETE) | ✅ |

### Pendientes ⚠️

| Endpoint | Nota |
|----------|------|
| `/documentos?{filtros}` | Filtros no funcionan correctamente |
| `/documentos/{tipo}/pendientes` | Solo pendientes de pago, no de contabilizar |

---

## Preguntas Pendientes para Soporte

1. ¿Hay evento webhook para DTEs recibidos del SII? (ej: `SII_DTE_CREATED`)
2. ¿Hay evento para movimientos bancarios nuevos?
3. ¿Se puede filtrar documentos por fecha de manera efectiva?

---

*Documento consolidado desde múltiples fuentes. Última actualización: 2 Enero 2026*
