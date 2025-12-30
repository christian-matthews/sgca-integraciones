# Resumen de Documentación API Skualo ERP

> 📖 Documentación oficial: https://docs.skualo.cl/reference/intro

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

### Obtener Token

Solicitar a: **soporte@skualo.cl**

---

## 2. Empresa y Maestros ✅

### 2.1 Empresa

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/empresa` | ✅ | Datos de la empresa |
| `GET /{RUT}/empresa/sucursales` | ✅ | Lista de sucursales |

### 2.2 Auxiliares (Clientes/Proveedores)

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/auxiliares` | ✅ | Lista paginada |
| `GET /{RUT}/auxiliares?PageSize=500` | ✅ | Con paginación |

**Respuesta paginada:**
```json
{
  "page": 1,
  "pageSize": 100,
  "size": 55,
  "items": [...]
}
```

### 2.3 Productos

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/productos` | ✅ | Lista de productos/servicios |

---

## 3. Contabilidad ✅

### 3.1 Comprobantes

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/contabilidad/comprobantes/{numero}` | ✅ | Obtener comprobante por número |

### 3.2 Reportes

| Endpoint | Parámetros | Estado |
|----------|------------|--------|
| `GET /{RUT}/contabilidad/reportes/balancetributario/{idPeriodo}` | PATH: `idPeriodo` (yyyyMM) | ✅ |
| `GET /{RUT}/contabilidad/reportes/librodiario` | QUERY: `Desde`, `Hasta` | ✅ |
| `GET /{RUT}/contabilidad/reportes/analisisporauxiliar/{idAuxiliar}` | PATH: `idAuxiliar` (RUT) | ✅ |
| `GET /{RUT}/contabilidad/reportes/analisisporcuenta/{idCuenta}` | PATH: `idCuenta`, QUERY: `fechaCorte` | ✅ |
| `GET /{RUT}/contabilidad/reportes/libromayor` | QUERY: ver abajo | ✅ |
| `GET /{RUT}/contabilidad/reportes/resultados` | QUERY: `fechaCorte` (obligatorio) | ✅ |
| `GET /{RUT}/contabilidad/reportes/librocompras/{idPeriodo}` | PATH: `idPeriodo`, QUERY: `IdSucursal` | ✅ |

**Formatos de parámetros:**

| Parámetro | Formato | Ejemplo |
|-----------|---------|---------|
| `idPeriodo` | `yyyyMM` | `202511` |
| `fechaCorte` | `yyyy-mm-dd` | `2025-11-30` |
| `Desde` / `Hasta` | `yyyy-mm-dd` | `2025-01-01` |

**Ejemplos:**
```
GET /{RUT}/contabilidad/reportes/balancetributario/202511
GET /{RUT}/contabilidad/reportes/librodiario?Desde=2024-10-01&Hasta=2024-12-31
GET /{RUT}/contabilidad/reportes/analisisporauxiliar/76965744-4
GET /{RUT}/contabilidad/reportes/analisisporcuenta/1109003?fechaCorte=2025-11-30&soloPendientes=false
```

### 3.3 Estado de Resultados ✅

```
GET /{RUT}/contabilidad/reportes/resultados
    ?fechaCorte=2025-12-31
    &agrupadoPor=0
    &incluyeAjusteTributario=false
```

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `fechaCorte` | ✅ **Obligatorio** | Fecha de corte (yyyy-mm-dd) |
| `agrupadoPor` | ❌ | 0 = Sin agrupar |
| `incluyeAjusteTributario` | ❌ | true/false |

**Estructura respuesta (por cuenta y mes):**
```json
{
  "IDCuenta": "4101001",
  "Cuenta": "Ventas Del Giro",
  "Enero": 19743604.0,
  "Febrero": 12050378.0,
  ...
  "Diciembre": 156653044.0,
  "TOTAL": 1452124383.0
}
```

**Nota:** Sin `fechaCorte` retorna 400 "No hay información a listar".

---

### 3.4 Libro de Compras ✅

```
GET /{RUT}/contabilidad/reportes/librocompras/{idPeriodo}?IdSucursal=0
```

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `idPeriodo` | ✅ PATH | Período (yyyyMM), ej: `202512` |
| `IdSucursal` | ✅ QUERY | 0 = Todas las sucursales |

**Estructura respuesta:**
```json
{
  "IDSucursal": 1,
  "Sucursal": "Casa Matriz",
  "Fecha": "2025-09-11T00:00:00-03:00",
  "Numero": 97,
  "IDTipoDT": 33,
  "TipoDoc": "Factura Compra Electrónica",
  "NumDoc": 5396263,
  "Emision": "2025-08-28T00:00:00-04:00",
  "IDAuxiliar": "77261280-K",
  "Auxiliar": "FALABELLA RETAIL S.A.",
  "Neto": 50336.0,
  "Exento": 0.0,
  "IVACD": 9564.0,
  "Total": 59900.0
}
```

**Uso:** Cruzar con DTEs recibidos para detectar pendientes de contabilizar.

---

### 3.5 Libro Mayor ✅

```
GET /{RUT}/contabilidad/reportes/libromayor
  ?IdCuentaInicio=1101001
  &IdCuentaFin=5999999
  &desde=2025-01-01
  &hasta=2025-06-30
  &IdSucursal=0
  &IncluyeAjusteTributario=false
```

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `IdCuentaInicio` | ✅ | Código cuenta inicio |
| `IdCuentaFin` | ✅ | Código cuenta fin |
| `desde` | ✅ | Fecha inicio (yyyy-mm-dd) |
| `hasta` | ✅ | Fecha fin (yyyy-mm-dd) |
| `IdSucursal` | ✅ | 0 = Todas |
| `IncluyeAjusteTributario` | ✅ | true/false |

**Campos respuesta:**
```
idDetalle, comprobante, fecha, idCuenta, cuenta, montoDebe, montoHaber,
glosa, idCentroCosto, centroCosto, idProyecto, proyecto, idTipoDoc,
numDoc, emision, vencimiento, idAuxiliar, auxiliar
```

---

## 4. Bancos y Tesorería ✅

### 4.1 Movimientos Bancarios

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/bancos/{idCuenta}` | ✅ | Listar movimientos de cuenta |
| `GET /{RUT}/bancos/{idCuenta}/{id}` | ✅ | Obtener movimiento específico |

**Parámetros:**
- `idCuenta`: Código contable de la cuenta banco (ej: `1102002`)
- `id`: GUID del movimiento

**Paginación:** `?PageSize=100&Page=1`

**Estructura movimiento:**
```json
{
  "id": "b10793d0-a769-478e-...",
  "idCuenta": "1102002",
  "cuenta": "Banco Santander",
  "fecha": "2025-04-29",
  "numDoc": "...",
  "glosa": "...",
  "montoCargo": 0,
  "montoAbono": 0,
  "conciliado": true,
  "fechaConciliacion": "..."
}
```

**Cuentas bancarias FIDI:**

| Código | Cuenta | Estado |
|--------|--------|--------|
| 1102002 | Banco Santander | ✅ 470 movimientos |
| 1103002 | Banco Santander USD | ❌ Sin acceso API |

---

## 5. Tablas de Referencia ✅

### 5.1 Tipos de Documentos SII

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/tablas/sii/tiposdocs` | ✅ | Lista 65 tipos DTE |
| `GET /{RUT}/tablas/sii/tiposdocs/{Id}` | ✅ | Detalle de un tipo |

**Tipos principales:**

| ID | Documento |
|----|-----------|
| 33 | Factura Electrónica |
| 34 | Factura No Afecta o Exenta Electrónica |
| 39 | Boleta Electrónica |
| 41 | Boleta Exenta Electrónica |
| 46 | Factura de Compra Electrónica |
| 52 | Guía de Despacho Electrónica |
| 56 | Nota Débito Electrónica |
| 61 | Nota Crédito Electrónica |

**Estructura respuesta:**
```json
{
  "id": 33,
  "nombre": "Factura Electrónica",
  "esTributario": true,
  "esElectronico": true,
  "vigente": true
}
```

### 5.2 Tipos de Documentos Internos

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/tablas/tiposdocumentos` | ✅ | 27 tipos internos |

**Filtros disponibles:** `Nombre`, `UsaDetalle`, `IDLibroFiscal`, `AfectaConciliacion`, `DocPropio`, `IDModulo`, `IDTipoDT`, `Vigente`

**Tipos principales:**

| ID | Documento |
|----|-----------|
| ABO | Abono |
| FAVE | Factura Venta Electrónica |
| FACE | Factura Compra Electrónica |
| BOLE | Boleta De Venta Electrónica |
| CHQ | Cheque |
| DEP | Depósito |

### 5.3 Centros de Costo

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/tablas/centroscostos` | ✅ | Lista centros de costo |

**Estructura respuesta:**
```json
{
  "id": 1,
  "nombre": "Administración General",
  "idAreaNegocio": 1,
  "areaNegocio": { "nombre": "..." },
  "vigente": true
}
```

### 5.4 Bancos (Catálogo)

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/tablas/bancos` | ✅ | Lista 43 bancos del sistema |

---

## 6. Documentos (DTE) ✅

### 6.1 Obtener Documento

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/documentos/{GUID}` | ✅ | Por ID interno (idDocumento) |
| `GET /{RUT}/documentos/{tipoInterno}/{folio}` | ✅ | Por tipo FAVE/FACE + folio |

**Importante:** El tipo debe ser el **interno** (FAVE, FACE, NCVE, etc.), NO el DTE (33, 34, 61).

**Estructura respuesta:**
```json
{
  "idDocumento": "6bc15489-11ac-46db-8bf1-98304e16f4d3",
  "idTipoDocumento": "FAVE",
  "tipoDocumento": "Factura Venta Electrónica",
  "idTipoDT": 33,
  "tipoDT": "Factura Electrónica",
  "folio": 337,
  "fecha": "2025-12-09",
  "idAuxiliar": "76965744-4",
  "auxiliar": "LOS ANDES TARJETAS DE PREPAGO S.A.",
  "neto": ...,
  "iva": ...,
  "total": ...,
  "detalles": [...],
  "xmlsii": "...",
  "estado": "..."
}
```

### 6.2 Obtener XML

| Endpoint | Estado | Descripción |
|----------|--------|-------------|
| `GET /{RUT}/documentos/{id}/xml` | ✅ | XML del documento |
| `GET /{RUT}/documentos/{id}/xml?destino=SII` | ✅ | XML formato SII |

**Headers:** `Accept: text/xml`

### 6.3 Cómo obtener el ID del documento

1. Usar **Análisis por Auxiliar** → campo `idDetalle` es el GUID del documento
2. Usar **tipo interno + folio** → `GET /documentos/FAVE/337`

### 6.4 Documentos Pendientes

| Endpoint | Estado | Nota |
|----------|--------|------|
| `GET /{RUT}/documentos/{IdTipoDocumento}/pendientes` | ⚠️ | Sin datos actualmente |

### 6.5 Listar Documentos (pendiente)

| Endpoint | Estado | Nota |
|----------|--------|------|
| `GET /{RUT}/documentos?{filtros}` | ⚠️ | Filtros no funcionan aún |

**Filtros documentados:**
```
IDTipoDocumento, IDTipoDT, Folio, FolioHasta, IDSucursal, Fecha,
IDAuxiliar, Auxiliar, IDDivision, IDCentroCosto, IDProyecto, 
Vencimiento, IDVendedor, IDEstado
```

---

## 7. Tenants Configurados

Ver archivo `tenants.json`:

```json
{
  "FIDI": { "rut": "77285542-7", "nombre": "Fidi SpA", "activo": true },
  "CISI": { "rut": "77949039-4", "nombre": "Constructora...", "activo": true }
}
```

---

## 8. Scripts Disponibles

| Script | Lenguaje | Descripción |
|--------|----------|-------------|
| `balance_excel.py` | Python | Genera Excel con Balance + EERR + KPIs |
| `explore-documentos.py` | Python | Explora endpoints de documentos |
| `test-connection.js` | Node.js | Verificar conexión básica |
| `get-reportes.js` | Node.js | Obtener reportes contables |

---

## 9. Archivos Generados

| Carpeta/Archivo | Descripción |
|-----------------|-------------|
| `generados/` | Excel generados con Balance y análisis |
| `config/` | Configuraciones de empresas |
| `config/ids_referencia_FIDI.md` | **IDs de referencia FIDI** (Plan Cuentas, Tipos Doc, etc.) |
| `*.json` | Respuestas de API guardadas |

---

## 10. Control de Pendientes (Nuevo) ✅

### 10.1 Movimientos Bancarios Sin Conciliar

```
GET /{RUT}/bancos/{idCuenta}?PageSize=100
```

**Campo clave:** `conciliado: false`

**Proceso:**
1. Obtener cuentas bancarias del Balance Tributario (códigos `1102xxx`)
2. Para cada cuenta, obtener movimientos
3. Filtrar donde `conciliado = false`

### 10.2 Documentos Pendientes de Aceptar en SII

```
GET /{RUT}/sii/dte/recibidos?PageSize=100
```

**Regla:** DTE recibido tiene **8 días** para aceptar/rechazar. Después = aceptación tácita.

**Campo clave:** `fechaRespuesta: null` + días desde `creadoEl` ≤ 8

### 10.3 Documentos Pendientes de Contabilizar

**Lógica de cruce:**
1. Obtener DTEs de `/sii/dte/recibidos`
2. Filtrar solo los aceptados (> 8 días o con `fechaRespuesta`)
3. Verificar si existen en `/documentos/{tipo}/{folio}`
4. Los que retornan 404 = pendientes de contabilizar

**Mapeo de tipos:**
| Tipo DTE | Tipo Interno |
|----------|--------------|
| 33 | FACE |
| 34 | FXCE |
| 61 | NCCE |
| 56 | NDCE |

📄 Ver documentación completa: `docs/control_pendientes.md`

---

## 11. Resumen de Endpoints

### Validados ✅ (23 endpoints)

| Módulo | Endpoint | Estado | Uso |
|--------|----------|--------|-----|
| Empresa | `/empresa` | ✅ | Info empresa |
| Empresa | `/empresa/sucursales` | ✅ | Sucursales |
| Auxiliares | `/auxiliares` | ✅ | Clientes/Proveedores |
| Productos | `/productos` | ✅ | Catálogo |
| Contabilidad | `/contabilidad/comprobantes/{numero}` | ✅ | Comprobante específico |
| Contabilidad | `/contabilidad/reportes/balancetributario/{idPeriodo}` | ✅ | Balance mensual |
| Contabilidad | `/contabilidad/reportes/librodiario` | ✅ | Libro diario |
| Contabilidad | `/contabilidad/reportes/analisisporauxiliar/{idAuxiliar}` | ✅ | Cartera por RUT |
| Contabilidad | `/contabilidad/reportes/analisisporcuenta/{idCuenta}` | ✅ | Detalle cuenta |
| **Bancos** | `/bancos/{idCuenta}` | ✅ | **Movimientos bancarios** |
| **Bancos** | `/bancos/{idCuenta}/{id}` | ✅ | Movimiento específico |
| Documentos | `/documentos/{GUID}` | ✅ | Documento por ID |
| Documentos | `/documentos/{tipoInterno}/{folio}` | ✅ | Documento por tipo+folio |
| Documentos | `/documentos/{id}/xml` | ✅ | XML del DTE |
| **SII** | `/sii/dte` | ✅ | **DTEs emitidos (ventas)** |
| **SII** | `/sii/dte/recibidos` | ✅ | **DTEs recibidos (compras)** |
| Tablas | `/tablas/sii/tiposdocs` | ✅ | Tipos DTE (SII) |
| Tablas | `/tablas/sii/tiposdocs/{Id}` | ✅ | Tipo DTE específico |
| Tablas | `/tablas/tiposdocumentos` | ✅ | Tipos internos |
| Tablas | `/tablas/centroscostos` | ✅ | Centros de costo |
| Tablas | `/tablas/bancos` | ✅ | Catálogo bancos |
| **Webhooks** | `/integraciones/webhooks` | ✅ | **Listar webhooks** |
| **Webhooks** | `/integraciones/webhooks` POST | ✅ | **Crear webhook** |
| **Webhooks** | `/integraciones/webhooks/{id}` DELETE | ✅ | **Eliminar webhook** |
| Contabilidad | `/contabilidad/reportes/libromayor` | ✅ | Libro mayor |
| **Contabilidad** | `/contabilidad/reportes/resultados` | ✅ | **Estado de Resultados** (requiere fechaCorte) |
| **Contabilidad** | `/contabilidad/reportes/librocompras/{periodo}` | ✅ | **Libro de Compras** |

### Pendientes ⚠️

| Módulo | Endpoint | Estado | Nota |
|--------|----------|--------|------|
| Documentos | `/documentos?{filtros}` | ⚠️ | Filtros no funcionan |
| Documentos | `/documentos/{tipo}/pendientes` | ⚠️ | Pendientes de pago, no de contabilizar |

---

## 11. Próximos Pasos

### Alta Prioridad - Documentos
1. ✉️ Contactar soporte@skualo.cl para:
   - Permisos de documentos en token
   - Ejemplo funcional de filtros
   - Endpoint para XML de documentos recibidos

### Media Prioridad - Reportes
2. Validar endpoints pendientes:
   - `/contabilidad/reportes/libromayor`
   - `/contabilidad/reportes/libroventas`
   - `/contabilidad/reportes/librocompras`

### Completado ✅
- Balance Tributario → Excel
- Análisis por Cuenta → Excel
- Análisis por Auxiliar → Excel
- Estado de Resultados (calculado desde Balance)
- KPIs financieros
- Estados Financieros Comparativos
- Movimientos Bancarios → JSON
- Libro Mayor → JSON
- Webhooks → CRUD completo
