# CLAY_API_BIBLIA_SGCA.md

# 0) Portada
**Qué es Clay API**:
La API de Clay (Clay.cl) expone funcionalidades core de su plataforma de gestión financiera y contable automatizada. Está centrada en la automatización bancaria (Fintoc/Scraping), gestión de obligaciones (DTEs del SII) y la conciliación inteligente ("Match"). Su diseño sugiere un enfoque de "contabilidad derivada de operaciones" más que un libro mayor manual tradicional.

**Alcance**:
Este documento indexa la totalidad de los endpoints expuestos en la especificación OpenAPI v3 oficial, documenta los modelos de datos (Schemas) y evalúa su viabilidad técnica como motor contable subyacente para pequeñas empresas en el contexto de SGCA.

**Fecha**: 02 de Enero de 2026
**Fuentes consultadas**:
- [Swagger UI Oficial](https://api.clay.cl/docs)
- [ReDoc Oficial](https://api.clay.cl/redoc)
- [OpenAPI Spec (JSON)](https://api.clay.cl/openapi.json)

---

# 1) Quickstart técnico

- **Base URL**: `https://api.clay.cl`
- **Auth**: Autenticación vía Header.
  - Header Name: `Token`
  - Valor: `<API_KEY>`
  - Esquema: `apiKey` (según especificación OpenAPI).
- **Rate Limits**: NO DOCUMENTADO EN FUENTES. No se observan headers `X-RateLimit` en la especificación.
- **Paginación**: Estándar en endpoints de listado (`GET`).
  - `limit`: (Optional) entero, por defecto suele ser 50 o 100.
  - `offset`: (Optional) entero, desplazamiento de registros.
  - Respuesta incluye campo `records` con `total_records`, `limit`, `offset` para calcular paginación.
- **Errores**:
  - Estructura estándar `HTTPValidationError` (Status 422).
  - Cuerpo: `{ "detail": [ { "loc": [...], "msg": "...", "type": "..." } ] }`
- **Entornos**: Único entorno productivo detectado en `servers`.

---

# 2) Catálogo TOTAL de endpoints

A continuación se listan **todos** los endpoints detectados en la especificación OpenAPI.

### Módulo: Obligaciones (Facturación/Compras/DTE)
| Método | Path | Resumen | Auth | Params Principales |
|---|---|---|---|---|
| POST | `/v1/obligaciones/crear_obligacion/` | Crea nueva obligación | Token | Body: `ObligationValidator` |
| GET | `/v1/obligaciones/boletas_honorarios/` | Listar boletas honorarios | Token | `rut_receptor`, `fecha_desde`, `limit`, `offset` |
| GET | `/v1/obligaciones/documentos_productos/` | Listar productos de DTEs/BH | Token | `rut_empresa`, `fecha_desde` |
| GET | `/v1/obligaciones/documentos_tributarios/` | Listar DTEs (recibidos/emitidos) | Token | `rut_empresa`, `fecha_desde`, `tipo` (recibida/pagada) |
| GET | `/v1/obligaciones/invoices/` | Listar invoices | Token | `rut_empresa`, `match`, `limit` |
| GET | `/v1/obligaciones/documentos_pendientes/` | DTEs por pagar (desde RCV SII) | Token | `rut_empresa` |
| GET | `/v1/obligaciones/cesiones/` | Listar cesiones (factoring) | Token | `rut_empresa`, `fecha_desde` |
| POST | `/v1/obligaciones/crear_nota_venta/` | Crear Notas de Venta | Token | Body: `ObligationNVValidator` |
| POST | `/v1/obligaciones/crear_orden_compra/` | Crear Órdenes de Compra | Token | Body: `OrderPurchaseValidator` |

### Módulo: Empresas (Organización)
| Método | Path | Resumen | Auth | Params Principales |
|---|---|---|---|---|
| POST | `/v1/empresas/crear_empresa/` | Crear empresa | Token | Body: `OrganizationValidator` |
| GET | `/v1/empresas/` | Listar empresas | Token | `limit`, `offset` |
| GET | `/v1/empresas/impuestos/` | Info impuestos (F29) | Token | `rut`, `anio`, `mes` |
| GET | `/v1/empresas/estado_avance/` | Progreso de carga/procesamiento | Token | `rut`, `fecha_desde`, `info` |
| POST | `/v1/empresas/activar_webhook/` | Activar Webhook | Token | Body: `WebhookValidator` |
| DELETE | `/v1/empresas/webhook/` | Eliminar Webhook | Token | Body: `WebhookDeleteValidator` |

### Módulo: Cuentas Bancarias (Tesorería)
| Método | Path | Resumen | Auth | Params Principales |
|---|---|---|---|---|
| GET | `/v1/cuentas_bancarias/saldos/` | Saldo bancario | Token | `numero_cuenta`, `rut_empresa`, `fecha_desde` |
| GET | `/v1/cuentas_bancarias/matches/` | Conciliaciones (Matches) | Token | `numero_cuenta`, `rut_empresa` |
| GET | `/v1/cuentas_bancarias/movimientos/{id}` | Movimiento específico | Token | Path: `id` |
| GET | `/v1/cuentas_bancarias/movimientos/` | Listar movimientos | Token | `numero_cuenta`, `rut_empresa`, `con_match` |
| GET | `/v1/cuentas_bancarias/movimientos_tc/` | Movimientos Tarjeta Crédito | Token | `numero_cuenta`, `periodo` |

### Módulo: Clientes y Proveedores
| Método | Path | Resumen | Auth | Params Principales |
|---|---|---|---|---|
| GET | `/v1/companias/clientes_proveedores/` | Listar contrapartes | Token | `rut_empresa`, `cliente` (bool) |

### Módulo: Contabilidad (Reporting)
| Método | Path | Resumen | Auth | Params Principales |
|---|---|---|---|---|
| GET | `/v1/contabilidad/balance/` | Balance de 8 columnas | Token | `rut_empresa`, `fecha_desde`, `tipo` |
| GET | `/v1/contabilidad/eerr/` | Estado de Resultados | Token | `rut_empresa`, `anio` |
| GET | `/v1/contabilidad/libro_diario/` | Libro Diario | Token | `rut_empresa`, `ordenar_por` |
| GET | `/v1/contabilidad/libro_mayor/` | Libro Mayor (por cuenta) | Token | `rut_empresa`, `cuenta` (req) |
| GET | `/v1/contabilidad/plan_cuenta/` | Plan de Cuentas | Token | `rut_empresa`, `nivel` |

### Módulo: Conexiones (Bank Feeds)
| Método | Path | Resumen | Auth | Params Principales |
|---|---|---|---|---|
| GET | `/v1/conexiones/` | Listar conexiones bancarias | Token | `rut_empresa` |
| PUT | `/v1/conexiones/` | Editar conexión | Token | Body: `IdConnectionValidator` |
| POST | `/v1/conexiones/crear/` | Crear conexión (Bank/SII) | Token | Body: `ConnectionValidator` |
| POST | `/v1/conexiones/actualizar/` | Forzar sincronización | Token | Body: `UpdateConnectionValidator` |
| POST | `/v1/conexiones/onboarding/` | Validar conexión | Token | Body: `UpdateConnectionValidator` |
| DELETE | `/v1/conexiones/{id}` | Eliminar conexión | Token | Path: `id` |

---

# 3) Schemas / Modelos (Selección Crítica)

Se han extraído los esquemas fundamentales para la operación.

### Transaction / DTE Models
- **DTEValidator**: Estructura base para crear obligaciones.
  - `fecha_emision` (string), `codigo_sii` (string), `folio` (string), `emisor` (DTEEntity), `receptor` (DTEReceiver), `totales` (Amounts), `detalle` (Array).
- **ObligationNVValidator** / **OrderPurchaseValidator**: Para notas de venta y OC. Incluyen arrays de items y referencias a emisor/receptor.
- **ResponseModelDTE**: Respuesta de listados DTE. Incluye `status` y `data` (con `records` y `items`).

### Banking Models
- **ConnectionValidator**: Credenciales para scraping bancario.
  - `proveedor`, `rut_empresa`, `rut_usuario`, `clave` (Bancaria!).
  - *Nota*: API requiere envío de credenciales bancarias en plano o estructura directa, implica alto nivel de confianza.
- **Match**: Objeto de conciliación.
  - `monto_conciliado`, `fecha_match`, `movimiento_id`, `folio` (factura).

### Accounting Models
- **ItemBalance**: Fila del balance.
  - `cuenta` (nombre), `debe`, `haber`, `deudor`, `acreedor`, `activo`, `pasivo`, `perdida`, `ganancia`.
- **ItemLD** (Libro Diario):
  - `numero_asientos`, `fecha_contabilizacion`, `cuenta`, `debito`, `credito`, `detalles`.
- **ItemLM** (Libro Mayor):
  - Similar a LD pero filtrado por cuenta, con `saldo_acumulado`.

### Webhooks
- **WebhookValidator**:
  - `url`: URL destino.
  - `rut`: RUT empresa asociada. (Schema inferido, campos exactos no detallados en properties pero sí en uso).

---

# 4) Flujos funcionales (end-to-end)

### A) Onboarding Cliente
1. **Crear Empresa**: `POST /v1/empresas/crear_empresa/`
   - Payload: RUT, Razón Social, RUT Facturador.
2. **Conectar SII/Banco**: `POST /v1/conexiones/crear/`
   - Payload: Credenciales (SII o Banco). Trigger de scraping inicial.
3. **Verificar Estado**: `GET /v1/empresas/estado_avance/`
   - Revisar flag de carga inicial completa.

### B) Conciliación Bancaria Automática
1. **Obtener Movimientos**: `GET /v1/cuentas_bancarias/movimientos/` (+params `con_match=false`)
   - Obtiene cartola sin conciliar.
2. **Obtener Documentos Pendientes**: `GET /v1/obligaciones/documentos_pendientes/`
   - Obtiene facturas impagas del SII.
3. **(Manual/Interno) Match**: No existe endpoint "Crear Match" explícito público documentado en `paths` bajo `/v1/matches`. La conciliación parece ser automática por el motor de Clay o vía interfaz UI.
   - *Nota*: Existe `GET /v1/cuentas_bancarias/matches/` para leerlos, pero **falta endpoint de escritura para forzar match vía API**.

### C) Reporting Contable
1. **Obtener Plan de Cuentas**: `GET /v1/contabilidad/plan_cuenta/`
2. **Obtener Libro Diario**: `GET /v1/contabilidad/libro_diario/?fecha_desde=2024-01-01`
   - Permite reconstruir la contabilidad completa para auditoría.

---

# 5) Webhooks

- **Eventos disponibles**: No hay un enum público de "topics". El endpoint es genérico `/v1/empresas/activar_webhook/`. Se presume que notifica sobre eventos core (llegada DTE, movimiento bancario).
- **Configuración**:
  - Activar: Envía URL y RUT empresa.
  - Eliminar: Envía RUT empresa.
- **Payloads**: No documentados explícitamente en schemas (tipo `WebhookPayload`). Se asume envío de JSON estándar ante eventos.
- **Firma/Seguridad**: NO DOCUMENTADO. Recomendación: Usar URL con token secreto en query param (e.g. `https://mi-callback.com?token=xyz`) dado que no se documenta firma HMAC.

---

# 6) Matriz de capacidades

| Dominio | ¿Existe en API? | Endpoint(s) | Profundidad | Notas / Riesgos |
|---|---|---|---|---|
| **DTE / SII** | **SÍ** | `/v1/obligaciones/...` | ADVANCED | Muy completo. Permite leer RCV completo, emitidos, recibidos, pendientes. |
| **Bancos / Tesorería** | **SÍ** | `/v1/cuentas_bancarias/...` | ADVANCED | Lectura de saldos y cartolas. Requiere entregar credenciales bancarias (Riesgo). |
| **Conciliación (Match)** | **PARCIAL** | `.../matches/` | MEDIUM | Lectura de matches excelente. **Escritura (Hacer match) no documentada**. |
| **Contabilidad (Libros)** | **SÍ (Solo Lectura)** | `/v1/contabilidad/...` | MEDIUM | Genera Balances y Libros automáticos. |
| **Asientos Manuales** | **NO** | - | NULA | **GAP CRÍTICO**. No se ve `POST /asiento` o `journal_entry`. No permite ajustes manuales vía API. |
| **Facturación (Emisión)** | **SÍ** | `crear_obligacion`, `crear_nota_venta` | MEDIUM | Permite inyectar ventas/compras para que Clay procese. |
| **Usuarios/Permisos** | **NO** | - | NULA | Gestión de equipo parece ser solo UI. |

---

# 7) Evaluación: ¿Puede Clay ser “motor contable/ERP” para empresas pequeñas?

**Veredicto**: **"Sirve como motor contable mínimo (Automated Ledger), pero NO reemplaza un ERP contable completo para contadores exigentes."**

**Evidencia**:
1.  **Plan de Cuentas Agregado**: Permite ver el plan de cuentas (`GET /plan_cuenta`), pero no se visualiza un endpoint para **crear/editar cuentas contables** (`POST /plan_cuenta`). El plan parece ser fijo o gestionado automáticamente según la industria.
2.  **Carencia de Asientos Manuales**: La ausencia de un endpoint `POST /journal_entry` impide realizar ajustes contables complejos (devengos manuales, provisiones específicas, ajustes de cierre) vía API. Depende 100% de que la "Operación" (Factura/Banco) genere el asiento.
3.  **Auditoría y Trazabilidad**: El Libro Diario (`GET /libro_diario`) expone el resultado, lo cual es excelente para auditoría ex-post (Backlog Snapshots), pero no permite control fino sobre la generación del dato.
4.  **Integración DTE**: Es su punto más fuerte. Como motor de "SII -> Contabilidad", es superior a un ERP genérico.

**Conclusión para SGCA**:
Clay es ideal como **Fuente de Verdad Operativa** (Bancos + SII) y pre-contabilidad. Puede alimentar a SGCA con datos muy limpios de "lo que pasó en el banco" y "lo que pasó en el SII". Sin embargo, si SGCA necesita *ejecutar* correcciones contables (e.g., "Mover este gasto de la cuenta X a la Y"), la API de Clay no ofrece (documentadamente) esa capacidad de escritura directa en el libro mayor.

---

# 8) Mapeo SGCA (Clay → SGCA)

| Concepto SGCA | Equivalente Clay API | Integración |
|---|---|---|
| **backlog_snapshots** | `GET /v1/obligaciones/documentos_pendientes/` | Snapshot diario de facturas por pagar y cobrar. |
| **expected_item_checks** | `GET /v1/cuentas_bancarias/movimientos/` | Detectar abonos sin match inmediato. |
| **findings (Evidencia)** | `GET /v1/obligaciones/invoices/` | Obtener detalle de facturas para adjuntar a hallazgos. |
| **Reconciliación (Auto)** | `GET /v1/cuentas_bancarias/matches/` | Verificar qué % de la cartola está conciliada automáticamente. |
| **GAP Odoo/Skualo** | `GET /v1/contabilidad/balance/` | Comparar saldos contables de Clay vs Odoo para detectar desvíos. |

---

# 9) Gaps, ambigüedades y preguntas para soporte Clay

### Gaps detectados
1.  **Falta endpoints de escritura contable**: No hay cómo crear un asiento manual o editar una cuenta contable vía API.
2.  **Webhooks opacos**: No se documenta la estructura del payload que envía el webhook, ni mecanismo de firma para seguridad (`X-Hub-Signature`).
3.  **Falta endpoint de Match manual**: No existe forma evidente de forzar una conciliación bancaria vía API, solo leer las existentes.

### Preguntas para Soporte (Copy/Paste)
> "Hola equipo Clay, estamos integrando su API para un sistema de auditoría.
> 1. ¿Existe algún endpoint no documentado para **crear asientos contables manuales** (`vouchers` / `journal entries`)? Necesitamos inyectar provisiones que no vienen de DTEs ni Bancos.
> 2. En la documentación de Webhooks (`/v1/empresas/activar_webhook/`), ¿dónde puedo ver la **estructura JSON del payload** que envían y qué eventos específicos gatillan la notificación?
> 3. ¿Existe endpoint para realizar un **Match bancario** vía API (asociar movimiento ID X con obligación ID Y)?
> 4. ¿Cuál es la tasa de **Rate Limiting** (requests/min) para la API? No la vimos en la documentación."
