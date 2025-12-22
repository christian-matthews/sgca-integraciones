# Consultas para Soporte Skualo (Chat)

Copiar y pegar en el chat de soporte:

---

## CONSULTA 1: Aprobar DTEs

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

---

## CONSULTA 2: Contabilizar Documentos

```
Hola, tengo DTEs aceptados en /sii/dte/recibidos pero necesito contabilizarlos asignando:
- Cuenta contable
- Centro de costo
- Proyecto

¿Existe un endpoint POST para crear el documento contable a partir del DTE recibido?

¿O debo usar otro método?

Gracias.
```

---

## CONSULTA 3: Conciliar Movimientos Bancarios

```
Hola, puedo ver movimientos bancarios con GET /bancos/{cuenta}

Cada movimiento tiene campo "conciliado: false"

¿Cómo puedo marcar un movimiento como conciliado vía API?

¿Existe un PUT o PATCH?

Gracias.
```

---

## CONSULTA 4: Estado de Resultados

```
Hola, intento obtener el Estado de Resultados con:

GET /{RUT}/contabilidad/reportes/resultados?fechaCorte=2025-11-30

Pero retorna: "No hay información a listar"

¿Requiere alguna configuración previa?
¿Cuáles son los parámetros correctos?

Empresa: CISI (77949039-4)

Gracias.
```

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

## CONSULTA 6: Listar Documentos

```
Hola, el endpoint /documentos siempre me da error:

GET /{RUT}/documentos?IDTipoDocumento=FACE
→ "Debe indicar al menos un criterio de filtro"

Ya probé con: IDTipoDocumento, Fecha, Folio, IDEstado

¿Cuál es el filtro correcto?

Gracias.
```

---

## CONSULTA 7: Permisos del Token

```
Hola, ¿podrían confirmar qué permisos tiene mi token?

Necesito saber si puedo:
- Aprobar DTEs (escritura en /sii/dte)
- Crear documentos (escritura en /documentos)
- Conciliar bancos (escritura en /bancos)

Empresas: FIDI (77285542-7), CISI (77949039-4)

Gracias.
```

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
