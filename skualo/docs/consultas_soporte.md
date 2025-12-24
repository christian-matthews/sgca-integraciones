# Consultas para Soporte Skualo (Chat)

> **⚠️ NOTA IMPORTANTE DEL SOPORTE (23/12/2025):**  
> "La API está pensada para consultar información de la base de datos, no para reemplazar la interfaz del sistema."

## Resumen de Respuestas

| Consulta | Estado |
|----------|--------|
| 1. Aprobar DTEs | ⚠️ Endpoint existe pero da error "Tenant Not Found" |
| 1b. Consultar pendientes | ✅ `?search=RutEmisor eq X` + filtrar `conAcuseRecibo=false` |
| 2. Contabilizar | ❌ No disponible vía API |
| 3. Conciliar bancos | ❌ No disponible vía API |
| 4. Evolutivo resultados | ⏳ Pendiente documentación |
| 5. Libro Mayor | ✅ Resuelto |
| 6. Listar documentos | ✅ Usar `?search=IDTipoDocumento eq FAVE` |
| 7. Permisos token | ✅ Acceso total sin restricciones |
| 8. Webhooks | ✅ Resuelto |
| 9. Eventos webhook | ⏳ Pendiente |

---

Copiar y pegar en el chat de soporte:

---

## CONSULTA 1: Aprobar DTEs ⚠️ PARCIALMENTE RESUELTO

```
Hola, estoy usando la API y necesito aprobar DTEs recibidos.

Puedo listar con: GET /{RUT}/sii/dte/recibidos ✅

Pero no encuentro cómo aprobarlos. ¿Existe un endpoint tipo POST para aceptar/rechazar?

Ejemplo de documento pendiente:
- Folio: 132285
- Emisor: Estacion De Servicio  
- ID: ca5ed4b2-c502-41b1-bea2-426a0bba76e2

Gracias.
```

**RESPUESTA SOPORTE:** El endpoint es `sii/dte/recibidos/{id}/aprobar`. El id se obtiene del listado de DTEs recibidos.

### ⚠️ PROBLEMA DETECTADO (23/12/2025)

Al intentar usar el endpoint en THE WINGMAN SPA (77285645-8), devuelve:
```json
{"isError":true,"type":"https://httpstatuses.com/404","title":"Tenant Not Found","status":404}
```

**Pendiente consultar a soporte:** ¿Por qué da "Tenant Not Found" si el tenant existe y funciona para otros endpoints?

### ✅ CÓMO CONSULTAR DTEs PENDIENTES DE APROBACIÓN

```python
# 1. Listar DTEs recibidos de un emisor específico (con filtro OData)
GET /{RUT}/sii/dte/recibidos?search=RutEmisor eq {RUT_EMISOR}

# 2. Identificar pendientes: buscar documentos donde:
#    - conAcuseRecibo = false
#    - fechaRespuesta = null

# Ejemplo de documento pendiente:
{
  "idDocumento": "c6a5587b-ace6-4dfd-b5cf-694127a4591c",
  "rutEmisor": "96945440-8",
  "emisor": "SOC CONCESIONARIA AUTOPISTA CENTRAL S A",
  "folio": 19005812,
  "fechaEmision": "2025-12-17",
  "montoTotal": 13080.0,
  "conAcuseRecibo": false,    ← PENDIENTE
  "fechaRespuesta": null      ← SIN RESPUESTA
}
```

### Endpoints relacionados verificados:

| Endpoint | Estado |
|----------|--------|
| `GET /sii/dte/recibidos` | ✅ Funciona (lista todos) |
| `GET /sii/dte/recibidos?search=RutEmisor eq X` | ✅ Funciona (filtra por emisor) |
| `GET /contabilidad/reportes/librocompras/{periodo}` | ✅ Funciona |
| `POST /sii/dte/recibidos/{id}/aprobar` | ❌ Error "Tenant Not Found" |

---

## CONSULTA 2: Contabilizar Documentos ❌ NO DISPONIBLE

```
Hola, tengo DTEs aceptados en /sii/dte/recibidos pero necesito contabilizarlos asignando:
- Cuenta contable
- Centro de costo
- Proyecto

¿Existe un endpoint POST para crear el documento contable a partir del DTE recibido?

¿O debo usar otro método?

Gracias.
```

**RESPUESTA SOPORTE:** No hay un endpoint para contabilizar. Debe hacerse desde la interfaz del sistema.

---

## CONSULTA 3: Conciliar Movimientos Bancarios ❌ NO DISPONIBLE

```
Hola, puedo ver movimientos bancarios con GET /bancos/{cuenta}

Cada movimiento tiene campo "conciliado: false"

¿Cómo puedo marcar un movimiento como conciliado vía API?

¿Existe un PUT o PATCH?

Gracias.
```

**RESPUESTA SOPORTE:** No hay un endpoint para conciliar. Debe hacerse desde la interfaz del sistema.

---

## CONSULTA 4: Estado de Resultados (Evolutivo) ⏳ PENDIENTE DOCUMENTACIÓN

```
Hola, intento obtener el Estado de Resultados con:

GET /{RUT}/contabilidad/reportes/resultados?fechaCorte=2025-11-30

Pero retorna: "No hay información a listar"

¿Requiere alguna configuración previa?
¿Cuáles son los parámetros correctos?

Empresa: CISI (77949039-4)

Gracias.
```

**RESPUESTA SOPORTE:** Faltan parámetros necesarios para la consulta. Adjuntaron documentación "Evolución de Resultados".

**ESTADO:** ⏳ Aún sin recibir la documentación con los parámetros requeridos (23/12/2025)

---

## ~~CONSULTA 5: Libro Mayor~~ ✅ RESUELTO

Parámetros correctos:
```
GET /{RUT}/contabilidad/reportes/libromayor
  ?IdCuentaInicio=1101001
  &IdCuentaFin=5999999
  &desde=2025-01-01
  &hasta=2025-06-30
  &IdSucursal=0
  &IncluyeAjusteTributario=false
```

---

## CONSULTA 6: Listar Documentos ✅ RESPONDIDO

```
Hola, el endpoint /documentos siempre me da error:

GET /{RUT}/documentos?IDTipoDocumento=FACE
→ "Debe indicar al menos un criterio de filtro"

Ya probé con: IDTipoDocumento, Fecha, Folio, IDEstado

¿Cuál es el filtro correcto?

Gracias.
```

**RESPUESTA SOPORTE:** La query estaba mal construida. Debe usar sintaxis OData:

```
✅ Correcto: ?search=IDTipoDocumento eq FAVE
❌ Incorrecto: ?IDTipoDocumento=FAVE
```

---

## CONSULTA 7: Permisos del Token ✅ RESPONDIDO

```
Hola, ¿podrían confirmar qué permisos tiene mi token?

Necesito saber si puedo:
- Aprobar DTEs (escritura en /sii/dte)
- Crear documentos (escritura en /documentos)
- Conciliar bancos (escritura en /bancos)

Empresas: FIDI (77285542-7), CISI (77949039-4)

Gracias.
```

**RESPUESTA SOPORTE:** El token otorga **permiso total** sobre la API, sin restricción alguna.

---

## ~~CONSULTA 8: Webhooks~~ ✅ RESUELTO

Endpoints funcionando:
```
GET  /{RUT}/integraciones/webhooks          → Listar
POST /{RUT}/integraciones/webhooks          → Crear {url, eventos}
GET  /{RUT}/integraciones/webhooks/{id}     → Obtener
PUT  /{RUT}/integraciones/webhooks          → Actualizar
DELETE /{RUT}/integraciones/webhooks/{id}   → Eliminar
```

Eventos disponibles:
- DOCUMENTO_CREATED, DOCUMENTO_UPDATED, DOCUMENTO_DELETED
- COMPROBANTE_CREATED, COMPROBANTE_UPDATED, COMPROBANTE_DELETED
- AUXILIAR_CREATED, AUXILIAR_UPDATED
- Y más...

---

## CONSULTA 9: Eventos Webhook Adicionales

```
Hola, ya tengo los webhooks funcionando con:

POST /{RUT}/integraciones/webhooks
{url, eventos: ["DOCUMENTO_CREATED", ...]}

Veo estos eventos: DOCUMENTO_CREATED, COMPROBANTE_CREATED, AUXILIAR_CREATED, etc.

Necesito saber si existen estos eventos:

1. ¿Hay evento cuando llega un DTE desde el SII?
   Ejemplo: DTE_RECIBIDO o SII_DTE_CREATED
   (para notificar cuando un proveedor envía factura)

2. ¿Hay evento para movimientos bancarios?
   Ejemplo: MOVIMIENTO_BANCARIO_CREATED o BANCO_MOVIMIENTO_CREATED
   (para notificar cuando entra/sale dinero de la cuenta)

Gracias.
```

---

## Información de Contexto (si la piden)

```
Endpoints que SÍ funcionan:
- GET /empresa ✅
- GET /auxiliares ✅
- GET /contabilidad/reportes/balancetributario/{periodo} ✅
- GET /contabilidad/reportes/librodiario ✅
- GET /contabilidad/reportes/libromayor ✅
- GET /bancos/{cuenta} ✅
- GET /sii/dte/recibidos ✅
- GET /documentos/{tipo}/{folio} ✅
- GET /tablas/tiposdocumentos ✅
- GET /tablas/centroscostos ✅
- GET/POST/DELETE /integraciones/webhooks ✅

Empresas: FIDI (77285542-7), CISI (77949039-4)
```
