# CLAY API BIBLIA (SGCA)

**Versión API:** 1.0.1
**Generado:** 2026-01-02 12:58

## Introducción

La API de Clay transformará tu forma de interactuar con el software contable y financiero. Diseñada para brindarte un acceso seguro y eficaz a una amplia gama de funcionalidades y datos financieros, esta API se integra sin esfuerzo a tus sistemas y aplicaciones actuales. Ya sea que necesites optimizar procesos, generar informes detallados o cualquier otra función, la API de Clay es tu aliado perfecto. Hemos simplificado la integración al máximo, con documentación completa disponible <a href=/redoc>aquí</a> para garantizar un proceso fluido. Aprovecha al máximo tus soluciones contables y financieras con el poder de Clay API.

## Autenticación y Quickstart

Para interactuar con la API de Clay, se requiere autenticación.

### Esquema: APIKeyHeader

- **Tipo:** API Key
- **Ubicación:** header (`Token`)

Ejemplo de uso en Header:
```http
Token: <TU_API_TOKEN>
```

### Base URL

`https://api.clay.cl`

## Catálogo TOTAL de Endpoints

### Clientes y proveedores

#### GET `/v1/companias/clientes_proveedores/`

**Retorna los clientes o proveedores de una empresa**

Parametros:
- `rut_empresa`: RUT de la empresa que busca sus clientes o provedores sin digito verificador

- `rut_contraparte`: Rut del cliente o proveedore que estoy buscando

- `cliente`: Indica el tipo de compañía, true para clientes, false para proveedores

- `limit`: número de ítems retornados en la respuesta, trabaja en conjunto con offset

- `offset`: número de ítems a saltar. Por ejemplo, si tu limit es de 200 y quieres ir a la 2da página, tu offset es 200


Ejemplo:
```
{
    "rut_empresa": "76345678", // Rut de la empresa del cual se está buscando la información
    "rut_contraparte": "96547710-1", // Rut del cliente o proveedore que estoy buscando
    "cliente": true, // Indica si se trata de un cliente (true) o proveedor (false)
    "limit": 200, // Límite de resultados a retornar
    "offset": 0 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `cliente` | query | No | boolean |  |
| `rut_contraparte` | query | No | string |  |
| `rut_empresa` | query | Sí | string |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

### Conexiones

#### GET `/v1/conexiones/`

**Listar conexiones**

Parametros:
- `rut_empresa`: RUT de la empresa sin dígito verificador ni puntos

- `limit`: número de items retornados en la respuesta, trabaja en juego con offset 

- `offset`: número de items a saltar. Ejemplo si tu limit es de 200 y quieres ir a la 2da página tu offset es 200

Ejemplo: 
```
{
    "rut_empresa": "76345678", // Rut de la empresa de la cual se está buscando la información
    "limit": 200, // Límite de resultados a retornar
    "offset": 1 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `rut_empresa` | query | No | string |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### PUT `/v1/conexiones/`

**Editar conexiones**

Parametros:
- `proveedor`: Nombre del servicio, opciones: ['sii', 'siicompany', 'banks', 'siicompany_eboletas'] 

- `rut_empresa`: RUT de la empresa a conectar 

- `dv_empresa`: DV de la empresa a conectar 

- `info`: { 

        `account_number`: número de cuenta bancaria,

        `bank`: "bci" nombre de banco ['estado', 'internacional','itau','bci','bice','chilebanconexion','santanderselect','bci360connect','scotiabank','itaupyme','santander','bbva','security','bciempresarios'],

    }

- `id`: Id de la conexión retornado en 'listar conexiones' 

- `rut_usuario`: RUT del usuario 

- `dv_usuario`: DV del usuario 

- `clave`: Clave de la conexión 

- `fecha_inicio_carga`: Fecha de inicio de carga de las obligaciones en formato YYYY-MM-DD 

Ejemplo: 
```
{
    "proveedor": "banks", // Proveedor de la información (ejemplo: SII)
    "info": {
        "account_number": "123456789", // Número de cuenta bancaria
        "bank": "bci", // Banco de la cuenta
    },
    "rut_empresa": "76345678", // Rut de la empresa
    "dv_empresa": "k", // Dígito verificador de la empresa
    "rut_usuario": "12345678", // Rut del usuario
    "dv_usuario": "k", // Dígito verificador del usuario
    "clave": "miClaveSegura123", // Clave de acceso segura al banco
    "fecha_inicio_carga": "2023-01-01" // Fecha de inicio de la carga de información
}
```

**Request Body:** [IdConnectionValidator](#model-idconnectionvalidator)

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### POST `/v1/conexiones/crear/`

**Creacion de conexión**

  Parametros:
- `proveedor`: Nombre del servicio, opciones: ['sii', 'siicompany', 'banks', 'siicompany_eboletas'] 

- `info`: { 

      `account_number`: número de cuenta bancaria,

      `bank`: "bci" nombre de banco ['estado','internacional','itau','bci','bice','chilebanconexion','santanderselect','bci360connect','scotiabank','itaupyme','santander','bbva','security','bciempresarios'],

      `currency`: "usd" ['clp', 'usd', 'eur'],

  }

- `rut_empresa`: RUT de la empresa a editar 

- `dv_empresa`: DV de la empresa a editar 

- `rut_usuario`: RUT del usuario 

- `dv_usuario`: DV del usuario 

- `clave`: Clave de la conexión 

- `fecha_inicio_carga`: Fecha de inicio de carga de las obligaciones en formato YYYY-MM-DD


  Ejemplo: 
  ```
  {
      "proveedor": "banks", // Proveedor de la información (ejemplo: SII)
      "info": {
          "account_number": "123456789", // Número de cuenta bancaria
          "bank": "bci", // Banco de la cuenta
          "currency": "clp" // Moneda de la cuenta (ejemplo: CLP)
      },
      "rut_empresa": "76345678", // Rut de la empresa
      "dv_empresa": "k", // Dígito verificador de la empresa
      "rut_usuario": "12345678", // Rut del usuario
      "dv_usuario": "k", // Dígito verificador del usuario
      "clave": "miClaveSegura123", // Clave de acceso segura al banco
      "fecha_inicio_carga": "2023-01-01" // Fecha de inicio de la carga de información
  }
  ```
  

**Request Body:** [ConnectionValidator](#model-connectionvalidator)

**Respuestas:**

- **201**: Successful Response
- **422**: Validation Error

---

#### POST `/v1/conexiones/actualizar/`

**Sincronizar conexión**

Parametros:
- `proveedor`: Nombre del servicio, opciones: ['estado','previred','internacional','itau','talana','bci','bsale','bice','sii', 'chilebanconexion','santanderselect','siicompany_eboletas', 'siicompany','bci360connect','nubox','scotiabank','itaupyme','santander','febos', 'security'] 

- `rut_empresa`: RUT de la empresa dueña de la cuenta bancaria 

- `dv_empresa`: DV de la empresa dueña de la cuenta bancaria 

- `categoria`: obligaciones, bancos o todos (para todas tus credenciales) si coloca todos se enviará a actualizar todas sus conexiones 

- `numero_cuenta`: Número de cuenta si actualizas un banco

Ejemplo: 
```
{
    "proveedor": "itau", // Proveedor de la información (ejemplo: itau)
    "rut_empresa": "76345678", // Rut de la empresa
    "dv_empresa": "k", // Dígito verificador de la empresa
    "categoria": "obligaciones" // Categoría de la información buscada (ejemplo: obligaciones)
}
```

**Request Body:** [UpdateConnectionValidator](#model-updateconnectionvalidator)

**Respuestas:**

- **201**: Successful Response
- **422**: Validation Error

---

#### POST `/v1/conexiones/onboarding/`

**Validación de conexión**

Parametros:
- `proveedor`: Nombre del servicio, opciones: ['estado','previred','internacional','itau','talana','bci','bsale','bice','sii', 'chilebanconexion','santanderselect','siicompany_eboletas', 'siicompany','bci360connect','nubox','scotiabank','itaupyme','santander','febos', 'security'] 

- `rut_empresa`: RUT de la empresa dueña de la cuenta bancaria 

- `dv_empresa`: DV de la empresa dueña de la cuenta bancaria 

- `categoria`: obligaciones, bancos o todos (para todas tus credenciales) si coloca todos se enviará a actualizar todas sus conexiones 

- `numero_cuenta`: Número de cuenta si el onboarding es para un banco

Ejemplo: 
```
{
    "proveedor": "itau", // Proveedor de la información (ejemplo: itau)
    "rut_empresa": "76345678", // Rut de la empresa
    "dv_empresa": "k", // Dígito verificador de la empresa
    "categoria": "obligaciones" // Categoría de la información buscada (ejemplo: obligaciones)
}
```

**Request Body:** [UpdateConnectionValidator](#model-updateconnectionvalidator)

**Respuestas:**

- **201**: Successful Response
- **422**: Validation Error

---

#### DELETE `/v1/conexiones/{id}`

**Eliminación de conexión**

Parametros:
- `id`: Id de la conexión retornado en 'listar conexiones' 


Ejemplo: 
```
{
    "id": "1234567890"
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | Sí | string |  |

**Respuestas:**

- **201**: Successful Response
- **422**: Validation Error

---

### Contabilidad

#### GET `/v1/contabilidad/balance/`

**Balance de 8 columnas**

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los asientos realizados sin dígito verificador ni puntos
- `fecha_desde`: Fecha desde en formato yyyy-mm-dd. Ej. 2018-01-23
- `fecha_hasta`: Fecha hasta en formato yyyy-mm-dd. Ej. 2018-01-23
- `tipo`: Tipo de reporte, por defecto se muestra tributario

Ejemplo: 
```
{
    "rut_empresa": "76345678", // rut de la empresa de la cual estoy buscando la informacion 
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda
    "tipo": "tributario" // Tipo de información que se está buscando (por ejemplo, tributaria)
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `tipo` | query | No | any |  |
| `rut_empresa` | query | Sí | string |  |
| `fecha_desde` | query | Sí | string |  |
| `fecha_hasta` | query | No | string |  |
| `initialize_until` | query | No | boolean |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/contabilidad/eerr/`

**Retorna el EERR de una empresa según el año especificado**

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los documentos tributarios sin dígito verificador ni puntos 

- `año`: Año visualización el reporte 

- `nivel`: Nivel de las cuentas contables en la que se visualiza el reporte, por defecto se muestran en nivel 3 

- `tipo`: Tipo de reporte, por defecto se muestra financiero 

- `limit`: número de items retornados en la respuesta, trabaja en juego con offset 

- `offset`: número de items a saltar. Ejemplo si tu limit es de 200 y quieres ir a la 2da página tu offset es 200

Ejemplo: 
```
{
    "rut_empresa": "76345678", // Rut de la empresa de la cual se está buscando la información
    "año": 2023, // Año al que corresponde la información financiera
    "nivel": "nivel 3", // Nivel de detalle de la información (por ejemplo, nivel 3)
    "tipo": "financiero" // Tipo de información que se está buscando (por ejemplo, financiera)
    "limit": 200, // Límite de resultados a retornar
    "offset": 0 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `tipo` | query | No | any |  |
| `nivel` | query | No | any |  |
| `año` | query | No | integer |  |
| `rut_empresa` | query | Sí | string |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/contabilidad/libro_diario/`

**Retorna el libro diario de una empresa según el rango de fechas**

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los documentos tributarios sin dígito verificador ni puntos 

- `fecha_desde`: fecha desde formato YYYY-MM-DD 

- `fecha_hasta`: fecha hasta formato YYYY-MM-DD 

- `fecha_creacion_desde`: fecha creación desde formato YYYY-MM-DD 

- `fecha_creacion_hasta`: fecha creación hasta formato YYYY-MM-DD 

- `tipo`: Tipo de reporte, por defecto se muestra tributario 

- `ordenar_por`: Permite ordenar el libro mayor por fecha de contabilización o fecha de creación, por defecto se ordena por fecha de contabilización 

- `limit`: número de items retornados en la respuesta, trabaja en juego con offset 

- `offset`: número de items a saltar. Ejemplo si tu limit es de 200 y quieres ir a la 2da página tu offset es 200

Ejemplo: 
```
{
    "rut_empresa": "76345678", // Rut de la empresa de la cual se está buscando la información
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda
    "fecha_creacion_desde": "2023-01-01", // Fecha de creación desde la cual se filtra la información
    "fecha_creacion_hasta": "2023-12-31", // Fecha de creación hasta la cual se filtra la información
    "tipo": "tributario", // Tipo de información que se está buscando (por ejemplo, tributaria)
    "ordenar_por": "fecha_contabilizacion", // Campo por el cual se ordenará la información
    "limit": 200, // Límite de resultados a retornar
    "offset": 0 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `tipo` | query | No | any |  |
| `ordenar_por` | query | No | any |  |
| `rut_empresa` | query | Sí | string |  |
| `fecha_desde` | query | No | string |  |
| `fecha_hasta` | query | No | string |  |
| `fecha_creacion_desde` | query | No | string |  |
| `fecha_creacion_hasta` | query | No | string |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/contabilidad/libro_mayor/`

**Retorna el libro mayor de una empresa según el rango de fechas de una cuenta específica**

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los asientos realizados 

- `cuenta`: Número de la cuenta contable Ej. 1.01.01.01, si lo quieres más de una cuenta sepáralas por coma (,). Ej. 1.01.01.01,1.01.01.02 

- `fecha_desde`: fecha desde formato YYYY-MM-DD 

- `fecha_hasta`: fecha hasta formato YYYY-MM-DD 

- `fecha_creacion_desde`: fecha creación desde formato YYYY-MM-DD 

- `fecha_creacion_hasta`: fecha creación hasta formato YYYY-MM-DD 

- `tipo`: Tipo de reporte, por defecto se muestra tributario 

- `ordenar_por`: Permite ordenar el libro mayor por fecha de contabilización o fecha de creación, por defecto se ordena por fecha de contabilización 

- `limit`: número de items retornados en la respuesta, trabaja en juego con offset 

- `offset`: número de items a saltar. Ejemplo si tu limit es de 200 y quieres ir a la 2da página tu offset es 200

Ejemplo: 
```
{
    "rut_empresa": "76345678", // Rut de la empresa de la cual se está buscando la información
    "cuenta": "1.01.01.01,1.01.01.02", // Números de cuenta separados por comas
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda
    "fecha_creacion_desde": "2023-01-01", // Fecha de creación desde la cual se filtra la información
    "fecha_creacion_hasta": "2023-12-31", // Fecha de creación hasta la cual se filtra la información
    "tipo": "tributario", // Tipo de información que se está buscando (por ejemplo, tributaria)
    "ordenar_por": "fecha_contabilizacion", // Campo por el cual se ordenará la información
    "limit": 200, // Límite de resultados a retornar
    "offset": 1 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `tipo` | query | No | any |  |
| `ordenar_por` | query | No | any |  |
| `cuenta` | query | Sí | string |  |
| `rut_empresa` | query | Sí | string |  |
| `fecha_desde` | query | No | string |  |
| `fecha_hasta` | query | No | string |  |
| `initialize_until` | query | No | boolean |  |
| `fecha_creacion_desde` | query | No | string |  |
| `fecha_creacion_hasta` | query | No | string |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/contabilidad/plan_cuenta/`

**Retorna el plan de cuenta**

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los asientos realizados sin dígito verificador ni puntos 

- `nivel`: Nivel de la cuenta 

- `codigos`: Filtra por códigos de la cuenta separados por coma 

- `nive_debajo_de`: Filtra por las cuentas inferiores al nivel seleccionado

Ejemplo: 
```
{
    "rut_empresa": "76345678", // Rut de la empresa de la cual se está buscando la información
    "nivel": 3, // Nivel de de la cuentas de la búsqueda
    "codigos": "1.02.01.01", // Códigos de cuenta contable separados por comas
    "nive_debajo_de": 5 // Nivel máximo debajo del cual se buscarán cuentas
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `nivel` | query | No | integer |  |
| `codigos` | query | No | string |  |
| `nivel_debajo_de` | query | No | string |  |
| `rut_empresa` | query | Sí | string |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

### Cuentas bancarias

#### GET `/v1/cuentas_bancarias/saldos/`

**Retorna el saldo bancario de una cuenta**

Crea un nuevo item con todos los detalles

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los documentos tributarios sin digito verificador ni puntos 

- `numero_cuenta`: Numero de cuenta a validar 

- `fecha_desde`: formato YYYY-MM-DD 

- `fecha_hasta`: formato YYYY-MM-DD 

- `limit`: número de items retornados en la respuesta, trabaja en juego con offset 

- `offset`: número de items a saltar. Ejemplo si tu limit es de 200 y quieres ir a la 2da página tu offset es 200


Ejemplo:
```
{
    "rut_empresa": "1", // Rut de la empresa de la cual se está buscando la información 
    "numero_cuenta": "xxxxxxxxxxxxx", // Número de cuenta que se está buscando
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda 
    "limit": 200, // Límite de resultados a retornar
    "offset": 1 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `numero_cuenta` | query | Sí | string |  |
| `rut_empresa` | query | Sí | string |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |
| `fecha_desde` | query | Sí | string |  |
| `fecha_hasta` | query | No | string |  |
| `initialize_until` | query | No | boolean |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/cuentas_bancarias/matches/`

**Retorna los matches de una cuenta bancaria**

Crea un nuevo item con todos los detalles

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los documentos tributarios sin digito verificador ni puntos 

- `numero_cuenta`: Numero de cuenta a validar 

- `abono`: true si es abono, false para cargos, no enviar para traer todo 

- `fecha_desde`: formato YYYY-MM-DD 

- `fecha_hasta`: formato YYYY-MM-DD 

- `fecha_match_desde`: formato YYYY-MM-DD 

- `fecha_match_hasta`: formato YYYY-MM-DD 

- `limit`: número de items retornados en la respuesta, trabaja en juego con offset 

- `offset`: número de items a saltar. Ejemplo si tu limit es de 200 y quieres ir a la 2da página tu offset es 200


Ejemplo:
```
{
    "rut_empresa": "1", // Rut de la empresa de la cual se está buscando la información
    "numero_cuenta": "xxxxxxxxxxxx", // Número de cuenta que se está buscando
    "abono": true, // Indica si se está buscando abonos en la cuenta (true) o cargos (false)
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda general
    "fecha_match_desde": "2023-12-31", // Fecha de inicio del periodo de búsqueda específico para coincidencias
    "fecha_match_hasta": "2023-01-01", // Fecha de fin del periodo de búsqueda específico para coincidencias
    "limit": 200, // Límite de resultados a retornar
    "offset": 1 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `abono` | query | No | boolean |  |
| `orden` | query | No | any |  |
| `numero_cuenta` | query | Sí | string |  |
| `rut_empresa` | query | Sí | string |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |
| `fecha_match_desde` | query | No | string |  |
| `fecha_match_hasta` | query | No | string |  |
| `fecha_desde` | query | No | string |  |
| `fecha_hasta` | query | No | string |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/cuentas_bancarias/movimientos/{id}`

**Retorna la informacion de un movimiento en especifico**

Crea un nuevo item con todos los detalles

Parametros:
- `id`: Movement unique identifier 


Ejemplo:
```
{
    "id": "0icwe0948m908wx0m9c484957x9n457t984tu57cxgtcnm89
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `id` | path | Sí | string |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/cuentas_bancarias/movimientos/`

**Retorna los movimientos bancarios de una cuenta**

Crea un nuevo item con todos los detalles

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los documentos tributarios sin digito verificador ni puntos 

- `numero_cuenta`: Numero de cuenta a validar 

- `abono`: true si es abono, false para cargos, no enviar para traer todo 

- `pagado`: true si los movimientos estan totalmente pagado 

- `con_match`: true si tiene los movimientos tienen algun match 

- `fecha_desde`: formato YYYY-MM-DD 

- `fecha_hasta`: formato YYYY-MM-DD 

- `limit`: número de items retornados en la respuesta, trabaja en juego con offset 

- `offset`: número de items a saltar. Ejemplo si tu limit es de 200 y quieres ir a la 2da página tu offset es 200


Ejemplo:
```
{
    "rut_empresa": "1", // Rut de la empresa de la cual se está buscando la información 
    "numero_cuenta": "xxxxxxxxxxxx", // numero de la cuenta que se está buscando
    "abono": true, // Indica si se está buscando abonos en la cuenta (true) o cargos (false)
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda general
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda
    "limit": 200, // Límite de resultados a retornar
    "offset": 1 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `abono` | query | No | boolean |  |
| `pagado` | query | No | boolean |  |
| `con_match` | query | No | boolean |  |
| `numero_cuenta` | query | Sí | string |  |
| `rut_empresa` | query | Sí | string |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |
| `fecha_desde` | query | Sí | string |  |
| `fecha_hasta` | query | No | string |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/cuentas_bancarias/movimientos_tc/`

**Retorna los movimientos de estados de cuenta de una tarjeta de credito**

Crea un nuevo item con todos los detalles

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los documentos tributarios sin digito verificador ni puntos 

- `numero_cuenta`: Numero de cuenta a validar 

- `abono`: true si es abono, false para cargos, no enviar para traer todo 

- `pagado`: true si los movimientos estan totalmente pagado 

- `con_match`: true si tiene los movimientos tienen algun match 

- `periodo`: formato YYYY-MM 

- `moneda`: moneda de la tarjeta de credito 

- `fecha_desde`: formato YYYY-MM-DD 

- `fecha_hasta`: formato YYYY-MM-DD 

- `limit`: número de items retornados en la respuesta, trabaja en juego con offset 

- `offset`: número de items a saltar. Ejemplo si tu limit es de 200 y quieres ir a la 2da página tu offset es 200


Ejemplo:
```
{
    "rut_empresa": "1", // Rut de la empresa de la cual se está buscando la información 
    "numero_cuenta": "xxxxxxxxxxxx", // numero de la cuenta que se está buscando
    "abono": true, // Indica si se está buscando abonos en la cuenta (true) o cargos (false)
    "periodo": "2023-01", // periodo de la tarjeta de credito
    "moneda": "CLP", // moneda de la tarjeta de credito
    "pagado": true, // true si los movimientos estan totalmente pagado
    "con_match": true, // true si tiene los movimientos tienen algun match
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda general
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda
    "limit": 200, // Límite de resultados a retornar
    "offset": 1 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `abono` | query | No | boolean |  |
| `pagado` | query | No | boolean |  |
| `con_match` | query | No | boolean |  |
| `periodo` | query | No | string |  |
| `moneda` | query | No | string |  |
| `numero_cuenta` | query | Sí | string |  |
| `rut_empresa` | query | Sí | string |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |
| `fecha_desde` | query | Sí | string |  |
| `fecha_hasta` | query | No | string |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

### Empresas

#### POST `/v1/empresas/crear_empresa/`

**Crear una nueva empresa**

Parametros:
- `nombre`: Nombre de la empresa 

- `razon_social`: Razon social de la empresa 

- `rut`: RUT de la empresa 

- `dv`: DV de la empresa 

- `rut_facturador`: RUT de la empresa a la que se le factura 

- `dv_facturador`: DV de la empresa a la que se le factura

Ejemplo:
```
{
    "nombre": "Nombre de la empresa",
    "razon_social": "Razon social de la empresa",
    "rut": "RUT de la empresa",
    "dv": "DV de la empresa",
    "rut_facturador": "RUT de la empresa a la que se le factura",
    "dv_facturador": "DV de la empresa a la que se le factura"
}
```

**Request Body:** [OrganizationValidator](#model-organizationvalidator)

**Respuestas:**

- **201**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/empresas/`

**Retorna todas las empresas**

Este endpoint solo muestra organizaciones que están activas o en periodo de prueba. Para gestionar organizaciones suspendidas o fuera del periodo de prueba, ve a app.clay.cl.

Parámetros opcionales:
- `contador`: Filtro por contador asignado a la organización.

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |
| `contador` | query | No | string |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/empresas/impuestos/`

**Retorna informacion de los impuestos de la empresa**

Parametros:
- `rut`: RUT de la empresa dueña de los asientos realizados 

- `anio`: Año del impuesto 

- `mes`: Mes del impuesto 

- `tipo`: Tipo de reporte, por defecto se muestra tributario ejemplo f29 o f22

- `limit`: número de ítems retornados en la respuesta, trabaja en conjunto con offset 

- `offset`: número de ítems a saltar. Por ejemplo, si tu limit es de 200 y quieres ir a la 2da página, tu offset es 200

Ejemplo:
```
{
    "rut": "76345678", // Rut de la empresa dueña de los asientos realizados 
    "anio": "2023", // Año del impuesto
    "mes": "01", // Mes del impuesto
    "tipo": "f29", // Tipo de formulario (ejemplo: f29)
    "limit": 200, // Límite de resultados a retornar
    "offset": 1 // Índice de inicio para la paginación de resultados
} 
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `tipo` | query | No | any |  |
| `rut` | query | Sí | string |  |
| `anio` | query | Sí | integer |  |
| `mes` | query | No | integer |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/empresas/estado_avance/`

**Organization Progress**

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `rut` | query | Sí | string |  |
| `fecha_desde` | query | Sí | string |  |
| `fecha_hasta` | query | No | string |  |
| `initialize_until` | query | No | boolean |  |
| `info` | query | Sí | string |  |

**Respuestas:**

- **201**: Successful Response
- **422**: Validation Error

---

#### POST `/v1/empresas/activar_webhook/`

**Activar URL de webhook**

Activa y valida una URL de webhook enviando una petición de prueba.

## Parámetros (en el body):

- `rut`: RUT de la empresa (sin puntos, sin guión). Ejemplo: `76123456`
- `url`: URL completa del webhook a activar
- `token`: (Opcional) Token de autenticación que se enviará en el header `x-webhook-key: {token}` para validar el webhook

## Ejemplo de uso:

**URL:**
```
POST /api/v1/organizations/activar_webhook/
```

**Body sin token:**
```json
{
    "rut": "76123456",
    "url": "https://tu-dominio.com/webhook"
}
```

**Body con token:**
```json
{
    "rut": "76123456",
    "url": "https://tu-dominio.com/webhook",
    "token": "mi-token-secreto-123"
}
```


## Respuesta exitosa (200):

Si tu webhook responde con status 200:
- ✅ El webhook queda activado para recibir notificaciones reales
- ℹ️ Si enviaste un `token`, se guardará y se usará en el header `x-webhook-key: {token}` en las notificaciones reales
- ℹ️ Si NO enviaste un `token`, las notificaciones NO tendrán el header `x-webhook-key`

**Con token:**
```json
{
    "status": true,
    "data": {
        "rut": "1",
        "url": "https://tu-dominio.com/webhook",
        "http_status": 200,
        "validated": true,
        "webhook_token": "mi-token-secreto-123"
    },
    "message": "Webhook validado correctamente"
}
```

**Sin token:**
```json
{
    "status": true,
    "data": {
        "rut": "1",
        "url": "https://tu-dominio.com/webhook",
        "http_status": 200,
        "validated": true
    },
    "message": "Webhook validado correctamente"
}
```

## Respuesta fallida:

Si tu webhook NO responde con status 200:
- ❌ No se guarda la configuración del webhook

```json
{
    "status": false,
    "data": {
        "rut": "1"
        "url": "https://tu-dominio.com/webhook",
        "http_status": 500,
        "validated": false
    },
    "message": "Webhook no validado"
}
```

**Request Body:** [WebhookValidator](#model-webhookvalidator)

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### DELETE `/v1/empresas/webhook/`

**Eliminar webhook configurado**

Elimina (soft delete) el webhook configurado de una organización.

## Parámetros (en el body):

- `rut`: RUT de la empresa (sin puntos, sin guión). Ejemplo: `76123456`

## Ejemplo de uso:

**URL:**
```
DELETE /api/v1/organizations/webhook/
```

**Body:**
```json
{
    "rut": "76123456"
}
```
    
## Respuesta exitosa (200):

```json
{
    "status": true,
    "message": "Webhook eliminado correctamente",
    "data": {
        "rut": "76123456-9",
        "webhook_url": "https://tu-dominio.com/webhook",
        "deleted_at": "2025-11-12 15:30:45"
    }
}
```

## Respuestas de error:

**404 - No se encontró la empresa:**
```json
{
    "detail": "No se encontró la empresa con el RUT 76123456"
}
```

**404 - No tiene webhook configurado:**
```json
{
    "detail": "La organización no tiene un webhook configurado"
}
```

**400 - Webhook ya eliminado:**
```json
{
    "detail": "El webhook ya se encuentra eliminado"
}
```

**403 - Sin permisos:**
```json
{
    "detail": "No tiene permiso para consultar la empresa del rut 76123456"
}
```

**Request Body:** [WebhookDeleteValidator](#model-webhookdeletevalidator)

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

### Obligaciones

#### POST `/v1/obligaciones/crear_obligacion/`

**Crea una nueva obligación**

Parametros:
- `organization_rut`: RUT de la empresa creadora de la obligación Ej. 76345678-k' 

- `oficina_partes`: Si es un dte que va a la oficina de partes true or false 

- `dte`:
- `fecha_emision`: La fecha en que se emitió el documento tributario electrónico.
- `codigo_sii`: El código asignado por el Servicio de Impuestos Internos (SII) al documento.
- `folio`: El número de folio asociado al documento.
- `emisor`: Los detalles del emisor del documento.
    - `rut_emisor`: El RUT del emisor.
    - `razon_social`: La razón social del emisor.
    - `giro`: El giro del emisor.
    - `direccion`: La dirección del emisor.
    - `comuna`: La comuna del emisor.
    - `ciudad`: La ciudad del emisor.
- `receptor`: Los detalles del receptor del documento.
    - `rut_receptor`: El RUT del receptor.
    - `razon_social`: La razón social del receptor.
    - `giro`: El giro del receptor.
    - `direccion`: La dirección del receptor.
    - `comuna`: La comuna del receptor.
    - `ciudad`: La ciudad del receptor.
- `totales`: Los totales asociados al documento.
    - `monto_afecto`: El monto afecto del documento.
    - `monto_exento`: El monto exento del documento.
    - `tasa_iva`: La tasa del Impuesto al Valor Agregado (IVA).
    - `iva`: El monto del IVA.
    - `otros_impuestos`: Otros impuestos, si los hubiera.
    - `monto_total`: El monto total del documento.
- `detalle`: Los detalles de los ítems del documento.
    - Para cada ítem, se incluyen los siguientes campos:
    - `numero_linea`: El número de línea del ítem.
    - `nombre_item`: El nombre o código del ítem.
    - `descripcion`: La descripción del ítem.
    - `cantidad`: La cantidad del ítem.
    - `precio_unitario`: El precio unitario del ítem.
    - `precio_total`: El precio total del ítem.

Ejemplo:
```
{
    "organization_rut": "76345678-k",
    "oficina_partes": true,
    "dte": {
        "fecha_emision": "2023-01-23",
        "codigo_sii": "34",
        "folio": 123,
        "emisor": {
            "rut_emisor": "76345678-k",
            "razon_social": "Razón social del emisor",
            "giro": "Giro del emisor",
            "direccion": "Dirección del emisor",
            "comuna": "Comuna del emisor",
            "ciudad": "Ciudad del emisor"
        },
        "receptor": {
            "rut_receptor": "76345678-k",
            "razon_social": "Razón social del receptor",
            "giro": "Giro del receptor",
            "direccion": "Dirección del receptor",
            "comuna": "Comuna del receptor",
            "ciudad": "Ciudad del receptor"
        },
        "totales": {
            "monto_afecto": 10000,
            "monto_exento": 5000,
            "tasa_iva": 19,
            "iva": 1900,
            "otros_impuestos": 0,
            "monto_total": 11900
        },
        "detalle": [
            {
                "numero_linea": 1,
                "nombre_item": "Item 1",
                "descripcion": "Descripción del Item 1",
                "cantidad": 2,
                "precio_unitario": 5000,
                "precio_total": 10000
            },
            {
                "numero_linea": 2,
                "nombre_item": "Item 2",
                "descripcion": "Descripción del Item 2",
                "cantidad": 1,
                "precio_unitario": 5000,
                "precio_total": 5000
            }
        ]
    }
```

**Request Body:** [ObligationValidator](#model-obligationvalidator)

**Respuestas:**

- **201**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/obligaciones/boletas_honorarios/`

**Estatus de la boleta de honorarios**

Parametros:
- `rut_emisor`: RUT del emisor de la boleta de honorarios 

- `dv_emisor`: DV del emisor de la boleta de honorarios 

- `rut_receptor`: RUT del receptor de la boleta de honorarios 

- `dv_receptor`: DV del receptor de la boleta de honorarios 

- `match`: Filtra por match (por defecto no se envía el filtro) 

- `fecha_desde`: formato YYYY-MM-DD 

- `fecha_hasta`: formato YYYY-MM-DD 

- `limit`: número de items retornados en la respuesta, trabaja en juego con offset 

- `offset`: número de items a saltar. Ejemplo si tu limit es de 200 y quieres ir a la 2da página tu offset es 200

Ejemplo:
```
{
    "rut_emisor": "12345678-9", // Rut del emisor de la boleta de honorarios
    "dv_emisor": "K", // Dígito verificador del emisor
    "rut_receptor": "87654321-0", // Rut del receptor de la boleta de honorarios
    "dv_receptor": "7", // Dígito verificador del receptor
    "match": true, // Indica si se desea buscar boleta de honorarios que coincidan entre emisor y receptor
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda
    "limit": 200, // Límite de resultados a retornar
    "offset": 0 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `match` | query | No | boolean |  |
| `rut_emisor` | query | No | string |  |
| `dv_emisor` | query | No | string |  |
| `rut_receptor` | query | Sí | string |  |
| `dv_receptor` | query | Sí | string |  |
| `fecha_desde` | query | Sí | string |  |
| `fecha_hasta` | query | No | string |  |
| `initialize_until` | query | No | boolean |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/obligaciones/documentos_productos/`

**Retorna los productos de los DTE y Boletas de Honorarios**

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los documentos tributarios sin digito verificador ni puntos 

- `recibida`: Indica si la boleta es por pagar recibida (true) o por cobrar (false) 

- `fecha_desde`: formato YYYY-MM-DD 

- `fecha_hasta`: formato YYYY-MM-DD 

- `limit`: Limita la cantidad de items de una respuesta JSON, por defecto el limit es 200, el máximo permitido es 200 

- `offset`: Permite paginar los items de una respuesta JSON, por defecto el offset es 0

Ejemplo:
```
{
    "rut_empresa": "12345678-k", // Rut de la empresa de la cual se está buscando la información
    "recibida": true, // Indica si la obligacion es por pagar recibida (true) o por cobrar (false)
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda
    "limit": 200, // Límite de resultados a retornar
    "offset": 0 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `recibida` | query | No | boolean |  |
| `rut_empresa` | query | Sí | string |  |
| `fecha_desde` | query | Sí | string |  |
| `fecha_hasta` | query | No | string |  |
| `initialize_until` | query | No | boolean |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/obligaciones/documentos_tributarios/`

**Retorna los documentos tributarios de una empresa**

Parametros:
- `rut_empresa`: RUT de la empresa dueña de los documentos tributarios sin digito verificador ni puntos 

- `rut_contraparte`: RUT de la empresa contraparte de la boleta sin dígito verificador ni puntos (opcional) 

- `recibida`: Indica si la boleta es recibida (true) o si es emitida (false) 

- `guia_despacho`: Indica si quieres traer las guias de despacho (true) o no (false), por defecto es false 

- `pagada`: Indica si quieres traer las boletas pagadas (true), las no pagadas (false) o todas (dejar vacío) 

- `folios`: Folios que quieras filtrar en la búsqueda separados por coma. Ej. 93636, 935552.

- `codigo_sii_exclud`: Códigos tributarios que quieras excluir en la búsqueda separados por coma. Ej. 48, 33. 

- `codigo_sii`: Filtra documentos por el código tributario 

- `cesion`: Filtra los documentos por si estan cedidas (por defecto no se envía el filtro) 

- `rechazada`: Filtra los documentos por si estan rechazados (por defecto no se envía el filtro) 

- `match`: Filtra los documentos por match (por defecto no se envía el filtro) 

- `fecha_desde`: formato YYYY-MM-DD 

- `fecha_hasta`: formato YYYY-MM-DD 

- `limit`: Limita la cantidad de items de una respuesta JSON, por defecto el limit es 200, el máximo permitido es 200 

- `offset`: Permite paginar los items de una respuesta JSON, por defecto el offset es 0

Ejemplo:
```
{
    "rut_empresa": "12345678", // Rut de la empresa de la cual se está buscando la información
    "rut_contraparte": "87654321", // Rut de la empresa contraparte de la boleta sin dígito verificador ni puntos
    "recibida": true, // Indica si la dte es por pagar (true) o por cobrar (false)
    "guia_despacho": false, // Indica si quieres traer las guias de despacho (true) o no (false), por defecto es false 
    "pagada": true, // Indica si la dte está pagada
    "folios": "93636, 935552", // Folios asociados a la dte
    "codigo_sii_exclud": "48, 33", // Códigos SII a excluir en la búsqueda
    "cesion": false, // Filtra los documentos por si estan cedidas (por defecto no se envía el filtro)
    "rechazada": true, // Filtra los documentos por si estan rechazados (por defecto no se envía el filtro)
    "codigo_sii": "123456", // Código SII asociado a la dte
    "match": true, // Indica si se desea buscar dte que coincidan con los criterios establecidos
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda
    "limit": 200, // Límite de resultados a retornar
    "offset": 0 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `recibida` | query | No | boolean |  |
| `pagada` | query | No | boolean |  |
| `guia_despacho` | query | No | boolean |  |
| `folio` | query | No | string |  |
| `codigo_sii_exclud` | query | No | string |  |
| `codigo_sii` | query | No | string |  |
| `match` | query | No | boolean |  |
| `cesion` | query | No | boolean |  |
| `rechazada` | query | No | boolean |  |
| `rut_contraparte` | query | No | string |  |
| `rut_empresa` | query | Sí | string |  |
| `fecha_desde` | query | Sí | string |  |
| `fecha_hasta` | query | No | string |  |
| `initialize_until` | query | No | boolean |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/obligaciones/invoices/`

**Retorna los invoices de una empresa**

Parametros:
- `rut_empresa`: RUT de la empresa dueña de las invoices sin digito verificador ni puntos 

- `taxid`: Taxid del proveedor emisor de las invoices (opcional) 

- `recibida`: Indica si la invoices es recibida (true) o si es emitida (false) 

- `match`: Filtra invoices por match (por defecto no se envía el filtro) 

- `fecha_desde`: formato YYYY-MM-DD 

- `fecha_hasta`: formato YYYY-MM-DD 

- `limit`: Limita la cantidad de items de una respuesta JSON, por defecto el limit es 200, el máximo permitido es 200 

- `offset`: Permite paginar los items de una respuesta JSON, por defecto el offset es 0

Ejemplo:
```
{
    "rut_empresa": "12345678-k", // Rut de la empresa de la cual se está buscando la información
    "taxid": "987654321", // Tax ID asociado a la obligación
    "recibida": true, //  Indica si la invoices es recibida (true) o si es emitida (false) 

    "match": true, // Filtra invoices por match (por defecto no se envía el filtro)
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda
    "limit": 200, // Límite de resultados a retornar
    "offset": 0 // Índice de inicio para la paginación de resultados
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `recibida` | query | No | boolean |  |
| `taxid` | query | No | string |  |
| `match` | query | No | boolean |  |
| `rut_empresa` | query | Sí | string |  |
| `fecha_desde` | query | Sí | string |  |
| `fecha_hasta` | query | No | string |  |
| `initialize_until` | query | No | boolean |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/obligaciones/documentos_pendientes/`

**Retorna los documentos tributarios por pagar desde el RCV del SII, que están pendientes por aprobar. Esta información se actualiza cada 4 horas**

Parametros:
- `rut_empresa`: RUT de la empresa dueña de las documentos pendientes sin digito verificador ni puntos 


Ejemplo:
```
{
    "rut_empresa": "12345678-k"
}
```

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `rut_empresa` | query | Sí | string |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### GET `/v1/obligaciones/cesiones/`

**Cesiones dte**

Parámetros:
- `folio`: Número de folio del documento 

- `codigo_sii`: Tipo de documento segun SII 

- `rut_emisor`: RUT del emisor del documento 

- `fecha_creacion_cesion`:  Formato YYYY-MM-DD 

- `fecha_desde`: Formato YYYY-MM-DD 

- `fecha_hasta`: Formato YYYY-MM-DD 

- `limit`: Número de items retornados en la respuesta, trabaja en juego con offset. Por ejemplo, si tu limit es de 200 y quieres ir a la segunda página, tu offset es 200. 

- `offset`: Número de items a saltar, trabaja a juego con limit. Ejemplo si tu limit es de 200 y quieres ir a la 2da página tu offset es 200

Ejemplo:
```
{
    "folio": "1234", //Se pueden enviar varios folios separados por ','
    "codigo_sii": "33",
    "fecha_creacion_cesion": "2024-01-01", // Fecha en la que se creó la cesión en Clay.
    "rut_emisor": "12345678", // Rut del emisor de la factura
    "fecha_desde": "2023-01-01", // Fecha de inicio del periodo de búsqueda
    "fecha_hasta": "2023-12-31", // Fecha de fin del periodo de búsqueda
    "limit": 200, // Límite de resultados a retornar
    "offset": 0 // Índice de inicio para la paginación de resultados
}
```

En la respuesta, las cesiones tienen el campo "numero" que refleja el orden ascendente en el cuál fueron cedidos los documentos

**Parámetros:**

| Nombre | Ubicación | Requerido | Tipo | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `folio` | query | No | string |  |
| `codigo_sii` | query | No | string |  |
| `rut_emisor` | query | No | string |  |
| `fecha_creacion_cesion` | query | No | string |  |
| `fecha_desde` | query | Sí | string |  |
| `fecha_hasta` | query | No | string |  |
| `initialize_until` | query | No | boolean |  |
| `rut_empresa` | query | Sí | string |  |
| `limit` | query | No | integer |  |
| `offset` | query | No | integer |  |

**Respuestas:**

- **200**: Successful Response
- **422**: Validation Error

---

#### POST `/v1/obligaciones/crear_nota_venta/`

**Crea una o multiples notas de venta**

Parametros:
- `rut_empresa`: RUT de la empresa creadora de la obligación Ej. 76345678' 

- `dv_empresa`: DV de la empresa creadora de la obligación Ej. k' 

- `notas`: Lista de notas de venta a crear
    - `fecha_emision`: La fecha en que se emitió el documento tributario electrónico.
    - `folio`: El número de folio asociado al documento.
    - `emisor`: Los detalles del emisor del documento.
        - `rut_emisor`: El RUT del emisor.
        - `dv_emisor`: El DV del emisor.
        - `razon_social`: La razón social del emisor.
        - `giro`: El giro del emisor.
        - `direccion`: La dirección del emisor.
        - `comuna`: La comuna del emisor.
        - `ciudad`: La ciudad del emisor.
    - `receptor`: Los detalles del receptor del documento.
        - `rut_receptor`: El RUT del receptor.
        - `dv_receptor`: El DV del receptor.
        - `razon_social`: La razón social del receptor.
        - `giro`: El giro del receptor.
        - `direccion`: La dirección del receptor.
        - `comuna`: La comuna del receptor.
        - `ciudad`: La ciudad del receptor.
    - `detalle`: Los detalles de los ítems del documento.
        - Para cada ítem, se incluyen los siguientes campos:
        - `numero_linea`: El número de línea del ítem.
        - `nombre_item`: El nombre o código del ítem.
        - `descripcion`: La descripción del ítem.
        - `cantidad`: La cantidad del ítem.
        - `precio_unitario`: El precio unitario del ítem.
        - `precio_total`: El precio total del ítem.
        - `descuento`: El descuento del ítem en porcentaje(0-100%).

Ejemplo:
```
{
    "rut_empresa": "76345678",
    "dv_empresa": "k",
    "notas": [
        {
            "fecha_emision": "2023-01-23",
            "folio": 123,
            "emisor": {
                "rut_emisor": "76345678",
                "dv_emisor": "k",
                "razon_social": "Razón social del emisor",
                "giro": "Giro del emisor",
                "direccion": "Dirección del emisor",
                "comuna": "Comuna del emisor",
                "ciudad": "Ciudad del emisor"
            },
            "receptor": {
                "rut_receptor": "76345678",
                "dv_receptor": "k",
                "razon_social": "Razón social del receptor",
                "giro": "Giro del receptor",
                "direccion": "Dirección del receptor",
                "comuna": "Comuna del receptor",
                "ciudad": "Ciudad del receptor"
            },
            "detalle": [
                {
                    "numero_linea": 1,
                    "nombre_item": "Item 1",
                    "comentario": "Comentario del Item 1",
                    "cantidad": 2,
                    "unidad": "Unidad del Item 1",
                    "precio_unitario": 5000,
                    "descuento": 0
                },
                {
                    "numero_linea": 2,
                    "nombre_item": "Item 2",
                    "comentario": "Comentario del Item 2",
                    "cantidad": 1,
                    "unidad": "Unidad del Item 2",
                    "precio_unitario": 5000,
                    "descuento": 0
                }
            ]
        }
    ]
}
```

**Request Body:** [ObligationNVValidator](#model-obligationnvvalidator)

**Respuestas:**

- **201**: Successful Response
- **422**: Validation Error

---

#### POST `/v1/obligaciones/crear_orden_compra/`

**Crea una o multiples ordenes de compra**

Parametros:
- `rut_empresa`: RUT de la empresa creadora de la orden de compra Ej. '76345678' 

- `dv_empresa`: DV de la empresa creadora de la orden de compra Ej. 'k' 

- `ordenes_compra`: Lista de órdenes de compra a crear
    - `fecha_emision`: La fecha en que se emitió la orden de compra (formato: YYYY-MM-DD).
    - `folio`: El número de folio/número de la orden de compra.
    - `currency`: Moneda de la orden (opcional, por defecto 'clp'). Valores: 'clp', 'usd', 'uf', etc.
    - `emitido`: Indica si la orden fue emitida por la empresa (opcional, por defecto false). Si es true, is_received será false. Si es false, is_received será true.
    - `exenta`: Indica si la orden es exenta de IVA (opcional, por defecto false). 
        - Si es false: Se calcula IVA del 19% sobre el neto. Ejemplo: neto=$84,034, IVA=$15,966, total=$100,000
        - Si es true: No se calcula IVA, todo va como monto exento. Ejemplo: exento=$100,000, IVA=$0, total=$100,000
    - `emisor`: Los detalles del emisor de la orden de compra (quien ordena la compra).
        - `rut_emisor`: El RUT del emisor.
        - `dv_emisor`: El DV del emisor.
        - `razon_social`: La razón social del emisor.
        - `giro`: El giro del emisor.
        - `direccion`: La dirección del emisor.
        - `comuna`: La comuna del emisor.
        - `ciudad`: La ciudad del emisor.
    - `receptor`: Los detalles del receptor (proveedor que recibe la orden).
        - `rut_receptor`: El RUT del receptor.
        - `dv_receptor`: El DV del receptor.
        - `razon_social`: La razón social del receptor.
        - `giro`: El giro del receptor (opcional).
        - `direccion`: La dirección del receptor (opcional).
        - `comuna`: La comuna del receptor (opcional).
        - `ciudad`: La ciudad del receptor (opcional).
    - `condiciones_pago`: Condiciones o términos de pago (opcional). Ej: 'Tarjeta', '30 días', 'Contado'.
    - `notas`: Notas adicionales de la orden (opcional).
    - `nota_documento`: Nota específica del documento (opcional).
    - `fecha_pago`: Lista de pagos esperados (opcional).
        - `fecha`: Fecha del pago esperado (formato: YYYY-MM-DD).
        - `monto`: Monto del pago esperado.
        - `description`: Descripción del pago. Ej: 'Pago único', 'Primera cuota'.
    - `detalle`: Los detalles de los ítems de la orden de compra.
        - Para cada ítem, se incluyen los siguientes campos:
        - `numero_linea`: El número de línea del ítem.
        - `nombre_item`: El nombre o descripción del ítem.
        - `comentario`: Comentario adicional del ítem (opcional).
        - `cantidad`: La cantidad del ítem.
        - `unidad`: La unidad de medida del ítem. Ej: 'UN', 'KG', 'MT'.
        - `precio_unitario`: El precio unitario del ítem.
        - `descuento`: El descuento del ítem en porcentaje (0-100%).

Ejemplo:
```
{
    "rut_empresa": "76570751",
    "dv_empresa": "K",
    "ordenes_compra": [
        {
            "fecha_emision": "2025-10-21",
            "folio": "7",
            "currency": "clp",
            "emitido": false,
            "exenta": false,
            "emisor": {
                "rut_emisor": "76570751",
                "dv_emisor": "K",
                "razon_social": "CLAY TECHNOLOGIES SPA",
                "giro": "Servicios Tecnológicos",
                "direccion": "santiago",
                "comuna": "providencia",
                "ciudad": "santiago"
            },
            "receptor": {
                "rut_receptor": "39151862",
                "dv_receptor": "K",
                "razon_social": "Monster Inc.",
                "giro": "Comercio",
                "direccion": "Av. Principal 456",
                "comuna": "Providencia",
                "ciudad": "Santiago"
            },
            "condiciones_pago": "Tarjeta",
            "notas": "Orden de compra para equipamiento de oficina",
            "nota_documento": "Esta es la nota del documento",
            "fecha_pago": [
                {
                    "fecha": "2025-10-21",
                    "monto": 100000,
                    "description": "Pago único"
                }
            ],
            "detalle": [
                {
                    "numero_linea": 1,
                    "nombre_item": "Televisor LED 55 pulgadas",
                    "comentario": "Este es un comentario del producto",
                    "cantidad": 2,
                    "unidad": "UN",
                    "precio_unitario": 100000,
                    "descuento": 10
                },
                {
                    "numero_linea": 2,
                    "nombre_item": "Cable HDMI",
                    "comentario": "Cable de 3 metros",
                    "cantidad": 3,
                    "unidad": "UN",
                    "precio_unitario": 5000,
                    "descuento": 0
                }
            ]
        }
    ]
}
```

**Request Body:** [OrderPurchaseValidator](#model-orderpurchasevalidator)

**Respuestas:**

- **201**: Successful Response
- **422**: Validation Error

---

## Schemas / Modelos

<a id='model-accountantlevels'></a>
### AccountantLevels

An enumeration.

*Sin propiedades o estructura compleja.*

<a id='model-amountspending'></a>
### AmountsPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `other_taxes` | Array<string> | Other Taxes |

<a id='model-amountsvalidator'></a>
### AmountsValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `monto_afecto` **(Req)** | integer | Monto Afecto |
| `monto_exento` **(Req)** | integer | Monto Exento |
| `tasa_iva` **(Req)** | string | Tasa Iva |
| `iva` **(Req)** | integer | Iva |
| `otros_impuestos` **(Req)** | integer | Otros Impuestos |
| `monto_total` **(Req)** | integer | Monto Total |

<a id='model-asientosusuariosev'></a>
### AsientosUsuariosEV

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `descripcion` | string | Descripcion |
| `listado` | Array<[ListadoEV](#model-listadoev)> | Listado |

<a id='model-bancocompanypending'></a>
### BancoCompanyPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `nombre` | string | Nombre |
| `tipo` | string | Tipo |
| `cuenta` | string | Cuenta |
| `email` | string | Email |

<a id='model-billinginfoorg'></a>
### BillingInfoOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `active` | boolean | Active |
| `source` | string | Source |
| `updated_at` | string | Updated At |
| `updated_by` | string | Updated By |

<a id='model-cassiusinfoorg'></a>
### CassiusInfoOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `active` | boolean | Active |
| `dte_emitidos` | boolean | Dte Emitidos |
| `dte_recibidos` | boolean | Dte Recibidos |
| `f29` | boolean | F29 |
| `honorarium` | boolean | Honorarium |
| `international` | boolean | International |
| `mov_abonos` | boolean | Mov Abonos |
| `mov_cargos` | boolean | Mov Cargos |
| `salaries` | boolean | Salaries |
| `start_date` | string | Start Date |
| `by_default` | boolean | By Default |
| `refund` | boolean | Refund |

<a id='model-cesionprod'></a>
### CesionProd

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `codigo` | string | Codigo |
| `numero` | string | Numero |
| `monto` | integer | Monto |
| `correo` | string | Correo |
| `razon_social` | string | Razon Social |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `fecha` | integer | Fecha |
| `fecha_humana` | string | Fecha Humana |
| `fecha_vencimiento` | integer | Fecha Vencimiento |
| `fecha_vencimiento_humana` | string | Fecha Vencimiento Humana |

<a id='model-cessionitem'></a>
### CessionItem

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `estado` | string | Estado |
| `rut_cesionario` | string | Rut Cesionario |
| `dv_cesionario` | string | Dv Cesionario |
| `razon_social_cesionario` | string | Razon Social Cesionario |
| `email_cesionario` | string | Email Cesionario |
| `rut_cedente` | string | Rut Cedente |
| `dv_cedente` | string | Dv Cedente |
| `razon_social_cedente` | string | Razon Social Cedente |
| `email_cedente` | string | Email Cedente |
| `fecha_cesion` | string | Fecha Cesion |
| `monto` | integer | Monto |
| `fecha_expiracion` | string | Fecha Expiracion |
| `numero` | integer | Numero |
| `fecha_creacion` | string | Fecha Creacion |

<a id='model-connectionvalidator'></a>
### ConnectionValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `proveedor` **(Req)** | string | Proveedor |
| `rut_empresa` **(Req)** | string | Rut Empresa |
| `dv_empresa` **(Req)** | string | Dv Empresa |
| `rut_usuario` **(Req)** | string | Rut Usuario |
| `dv_usuario` **(Req)** | string | Dv Usuario |
| `clave` **(Req)** | string | Clave |
| `fecha_inicio_carga` | string | Fecha Inicio Carga |
| `info` | [InfoBankAccount](#model-infobankaccount) |  |

<a id='model-contactos'></a>
### Contactos

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `nombre` | string | Nombre |
| `telefono` | string | Telefono |
| `email` | string | Email |

<a id='model-costcenterld'></a>
### CostCenterLD

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `nombre` | string | Nombre |
| `debito` | integer | Debito |
| `credito` | integer | Credito |

<a id='model-dteentityvalidator'></a>
### DTEEntityValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut_emisor` **(Req)** | string | Rut Emisor |
| `dv_emisor` | string | Dv Emisor |
| `razon_social` **(Req)** | string | Razon Social |
| `giro` **(Req)** | string | Giro |
| `direccion` **(Req)** | string | Direccion |
| `comuna` **(Req)** | string | Comuna |
| `ciudad` **(Req)** | string | Ciudad |

<a id='model-dtereceivervalidator'></a>
### DTEReceiverValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut_receptor` **(Req)** | string | Rut Receptor |
| `dv_receptor` | string | Dv Receptor |
| `razon_social` **(Req)** | string | Razon Social |
| `giro` **(Req)** | string | Giro |
| `direccion` **(Req)** | string | Direccion |
| `comuna` **(Req)** | string | Comuna |
| `ciudad` **(Req)** | string | Ciudad |

<a id='model-dtevalidator'></a>
### DTEValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `fecha_emision` **(Req)** | string | Fecha Emision |
| `codigo_sii` **(Req)** | string | Codigo Sii |
| `folio` **(Req)** | string | Folio |
| `emisor` **(Req)** | [DTEEntityValidator](#model-dteentityvalidator) |  |
| `receptor` **(Req)** | [DTEReceiverValidator](#model-dtereceivervalidator) |  |
| `totales` **(Req)** | [AmountsValidator](#model-amountsvalidator) |  |
| `detalle` **(Req)** | Array<object> | Detalle |

<a id='model-dataev'></a>
### DataEV

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_movimientos` | [TotalMovimientosEV](#model-totalmovimientosev) |  |
| `total_movimientos_matches` | [TotalMovimientosMatchesEV](#model-totalmovimientosmatchesev) |  |
| `matches_usuarios` | [MatchesUsuariosEV](#model-matchesusuariosev) |  |
| `asientos_usuarios` | [AsientosUsuariosEV](#model-asientosusuariosev) |  |
| `movimientos_sin_contabilizar` | [MovimientosSinContabilizarEV](#model-movimientossincontabilizarev) |  |
| `matches_sin_contabilizar` | [MatchesSinContabilizarEV](#model-matchessincontabilizarev) |  |

<a id='model-dataplan'></a>
### DataPlan

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordDataPlan](#model-recorddataplan) |  |
| `items` | Array<[ItemDataPlan](#model-itemdataplan)> | Items |

<a id='model-datetypes'></a>
### DateTypes

An enumeration.

*Sin propiedades o estructura compleja.*

<a id='model-descripciondte'></a>
### DescripcionDTE

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `item` | string | Item |
| `descripcion` | string | Descripcion |
| `cantidad` | integer | Cantidad |
| `unidad` | string | Unidad |
| `precio_unitario` | integer | Precio Unitario |
| `precio_total` | integer | Precio Total |

<a id='model-detailtaxlogs'></a>
### DetailTaxlogs

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `code` | integer | Code |
| `name` | string | Name |
| `value` | integer | Value |

<a id='model-detailsocvalidator'></a>
### DetailsOCValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `numero_linea` **(Req)** | integer | Numero Linea |
| `nombre_item` **(Req)** | string | Nombre Item |
| `comentario` | string | Comentario |
| `cantidad` **(Req)** | integer | Cantidad |
| `unidad` | string | Unidad |
| `precio_unitario` **(Req)** | integer | Precio Unitario |
| `descuento` | integer | Descuento |

<a id='model-detalleimpuestos'></a>
### DetalleImpuestos

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `codigo` | integer | Codigo |
| `monto` | integer | Monto |

<a id='model-detallescompanypending'></a>
### DetallesCompanyPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `folio` | integer | Folio |
| `tipo` | string | Tipo |
| `monto_total` | integer | Monto Total |
| `fecha_emision` | integer | Fecha Emision |
| `fecha_emision_humana` | string | Fecha Emision Humana |

<a id='model-embedorg'></a>
### EmbedOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `has` | boolean | Has |
| `updated_at` | string | Updated At |
| `updated_by` | string | Updated By |

<a id='model-emisorbh'></a>
### EmisorBH

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `razon_social` | string | Razon Social |

<a id='model-emisordte'></a>
### EmisorDTE

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `razon_social` | string | Razon Social |
| `rut` | string | Rut |
| `dv` | string | Dv |

<a id='model-emisorinvoice'></a>
### EmisorInvoice

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `razon_social` | string | Razon Social |
| `taxid` | string | Taxid |

<a id='model-emisorpending'></a>
### EmisorPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `razon_social` | string | Razon Social |
| `rut` | string | Rut |
| `dv` | string | Dv |

<a id='model-emisorprod'></a>
### EmisorProd

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `razon_social` | string | Razon Social |

<a id='model-fechapagovalidator'></a>
### FechaPagoValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `fecha` **(Req)** | string | Fecha |
| `monto` **(Req)** | integer | Monto |
| `description` | string | Description |

<a id='model-httpvalidationerror'></a>
### HTTPValidationError

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `detail` | Array<[ValidationError](#model-validationerror)> | Detail |

<a id='model-idconnectionvalidator'></a>
### IdConnectionValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `proveedor` **(Req)** | string | Proveedor |
| `rut_empresa` **(Req)** | string | Rut Empresa |
| `dv_empresa` **(Req)** | string | Dv Empresa |
| `id` **(Req)** | string | Id |
| `rut_usuario` **(Req)** | string | Rut Usuario |
| `dv_usuario` **(Req)** | string | Dv Usuario |
| `clave` **(Req)** | string | Clave |
| `fecha_inicio_carga` **(Req)** | string | Fecha Inicio Carga |
| `info` | [InfoBankAccount](#model-infobankaccount) |  |

<a id='model-infobankaccount'></a>
### InfoBankAccount

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `account_number` **(Req)** | string | Account Number |
| `bank` **(Req)** | string | Bank |
| `currency` | string | Currency |

<a id='model-internacionalinvoice'></a>
### InternacionalInvoice

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `pais` | string | Pais |
| `moneda` | string | Moneda |
| `cambio` | integer | Cambio |
| `monto_local` | integer | Monto Local |

<a id='model-internaluseorg'></a>
### InternalUseOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `groups` | Array<string> | Groups |

<a id='model-item'></a>
### Item

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | string | Este ID podria modificarse por la actualización de información del banco |
| `fecha` | integer | Fecha |
| `fecha_humana` | string | Fecha Humana |
| `numero_documento` | string | Numero Documento |
| `reconocido` | boolean | Reconocido |
| `pagado` | boolean | Pagado |
| `abono` | boolean | Abono |
| `sucursal` | string | Sucursal |
| `descripcion` | string | Descripcion |
| `monto` | number | Monto |
| `monto_original` | number | Monto Original |
| `saldo_insoluto` | number | Saldo Insoluto |
| `ids_relacionados` | Array<string> | Ids Relacionados |
| `mas_info` | [MasInfo](#model-masinfo) |  |
| `matches` | Array<[Match](#model-match)> | Matches |
| `contablemente_correcto` | string | Contablemente Correcto |
| `fecha_humana_creacion` | string | Fecha Humana Creacion |
| `fecha_creacion` | integer | Fecha Creacion |
| `moneda` | string | Moneda |

<a id='model-itembh'></a>
### ItemBH

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `pdf` | [PDFBH](#model-pdfbh) |  |
| `fecha` | integer | Fecha |
| `fecha_humana` | string | Fecha Humana |
| `status` | string | Status |
| `numero` | string | Numero |
| `tipo` | string | Tipo |
| `impuesto_retiene` | string | Impuesto Retiene |
| `emisor` | [EmisorBH](#model-emisorbh) |  |
| `receptor` | [ReceptorBH](#model-receptorbh) |  |
| `total` | [TotalBH](#model-totalbh) |  |
| `pagada` | boolean | Pagada |
| `descripcion` | string | Descripcion |

<a id='model-itembalance'></a>
### ItemBalance

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `debe` | integer | Debe |
| `haber` | integer | Haber |
| `deudor` | integer | Deudor |
| `acreedor` | integer | Acreedor |
| `activo` | integer | Activo |
| `pasivo` | integer | Pasivo |
| `perdida` | integer | Perdida |
| `ganancia` | integer | Ganancia |
| `cuenta` | string | Cuenta |
| `es_resultado` | boolean | Es Resultado |

<a id='model-itemcompanypending'></a>
### ItemCompanyPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `tipo` | string | Tipo |
| `razon_social` | string | Razon Social |
| `rut` | string | Rut |
| `direccion` | string | Direccion |
| `comuna` | string | Comuna |
| `ciudad` | string | Ciudad |
| `plazo_pago` | string | Plazo Pago |
| `banco` | [BancoCompanyPending](#model-bancocompanypending) |  |
| `contactos` | Array<[Contactos](#model-contactos)> | Contactos |
| `facturas_pendiente` | integer | Facturas Pendiente |
| `monto_pendiente` | integer | Monto Pendiente |
| `detalles` | Array<[DetallesCompanyPending](#model-detallescompanypending)> | Detalles |

<a id='model-itemconex'></a>
### ItemConex

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | string | Id |
| `rut_empresa` | string | Rut Empresa |
| `dv_empresa` | string | Dv Empresa |
| `proveedor` | string | Proveedor |
| `validado` | string | Validado |
| `fecha_validacion` | string | Fecha Validacion |
| `razon` | string | Razon |
| `fecha_humana_validacion` | string | Fecha Humana Validacion |
| `ultima_actualizacion` | string | Ultima Actualizacion |
| `numero_cuenta` | string | Numero Cuenta |
| `tipo_documentos` | Array<Array<string>> | Tipo Documentos |

<a id='model-itemdte'></a>
### ItemDTE

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `_id` **(Req)** | string |  Id |
| `xml` | object | Xml |
| `fecha_emision` | integer | Fecha Emision |
| `fecha_humana_emision` | string | Fecha Humana Emision |
| `numero` | string | Numero |
| `saldo_insoluto` | integer | Saldo Insoluto |
| `pagado` | boolean | Pagado |
| `recibida` | boolean | Recibida |
| `emisor` | [EmisorDTE](#model-emisordte) |  |
| `receptor` | [ReceptorDTE](#model-receptordte) |  |
| `total` | [TotalDTE](#model-totaldte) |  |
| `doc_relacionados` | Array<object> | Doc Relacionados |
| `informacion_pago` | Array<object> | Informacion Pago |
| `descripcion` | Array<[DescripcionDTE](#model-descripciondte)> | Descripcion |
| `codigo` | string | Codigo |
| `tipo` | string | Tipo |
| `recepcion` | [ReceptionDTE](#model-receptiondte) |  |
| `cesion` | [CesionProd](#model-cesionprod) |  |

<a id='model-itemdataplan'></a>
### ItemDataPlan

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `nivel` | integer | Nivel |
| `nombre` | string | Nombre |
| `codigo` | string | Codigo |
| `subcategoria` | Array<string> | Subcategoria |
| `es_puente` | boolean | Es Puente |

<a id='model-itemeerr'></a>
### ItemEERR

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `mes` | integer | Mes |
| `cuenta_contable` | string | Cuenta Contable |
| `categoria` | string | Categoria |
| `debe` | integer | Debe |
| `haber` | integer | Haber |
| `saldo` | integer | Saldo |
| `centro_costo` | string | Centro Costo |

<a id='model-iteminvoice'></a>
### ItemInvoice

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `fecha_emision` | integer | Fecha Emision |
| `fecha_humana_emision` | string | Fecha Humana Emision |
| `numero` | string | Numero |
| `saldo_insoluto` | integer | Saldo Insoluto |
| `pagado` | boolean | Pagado |
| `recibida` | boolean | Recibida |
| `emisor` | [EmisorInvoice](#model-emisorinvoice) |  |
| `descripcion` | Array<[DescripcionDTE](#model-descripciondte)> | Descripcion |
| `receptor` | [ReceptorInvoice](#model-receptorinvoice) |  |
| `total` | [TotalInvoice](#model-totalinvoice) |  |
| `codigo` | string | Codigo |
| `internacional` | [InternacionalInvoice](#model-internacionalinvoice) |  |
| `contablemente_correcto` | string | Contablemente Correcto |

<a id='model-iteminvoicetransfer'></a>
### ItemInvoiceTransfer

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `folio` | string | Folio |
| `cesiones` | Array<[CessionItem](#model-cessionitem)> | Cesiones |
| `codigo_sii` | string | Codigo Sii |
| `rut_emisor` | string | Rut Emisor |
| `dv_emisor` | string | Dv Emisor |
| `razon_social_emisor` | string | Razon Social Emisor |
| `rut_receptor` | string | Rut Receptor |
| `email_receptor` | string | Email Receptor |
| `fecha_documento` | string | Fecha Documento |
| `monto` | integer | Monto |
| `tipo_documento` | string | Tipo Documento |

<a id='model-itemld'></a>
### ItemLD

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `numero_asientos` | integer | Numero Asientos |
| `fecha_contabilizacion` | integer | Fecha Contabilizacion |
| `fecha_contabilizacion_humana` | string | Fecha Contabilizacion Humana |
| `fecha_creacion` | integer | Fecha Creacion |
| `fecha_creacion_humana` | string | Fecha Creacion Humana |
| `creado_por` | string | Creado Por |
| `cuenta` | string | Cuenta |
| `debito` | integer | Debito |
| `credito` | integer | Credito |
| `detalles` | string | Detalles |
| `ruta` | [RutaLD](#model-rutald) |  |
| `cetro_costos` | Array<[CostCenterLD](#model-costcenterld)> | Cetro Costos |
| `contraparte` | string | Contraparte |
| `rut` | string | Rut |

<a id='model-itemlm'></a>
### ItemLM

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `cuenta` | string | Cuenta |
| `fecha_contabilizacion` | integer | Fecha Contabilizacion |
| `fecha_contabilizacion_humana` | string | Fecha Contabilizacion Humana |
| `fecha_creacion` | integer | Fecha Creacion |
| `fecha_creacion_humana` | string | Fecha Creacion Humana |
| `creado_por` | string | Creado Por |
| `numero_asiento` | integer | Numero Asiento |
| `debito` | integer | Debito |
| `credito` | integer | Credito |
| `numero_obligacion` | string | Numero Obligacion |
| `obligacion` | string | Obligacion |
| `contraparte` | string | Contraparte |
| `rut` | string | Rut |
| `detalles` | string | Detalles |
| `evento` | string | Evento |
| `fecha_registro_compra_venta` | integer | Fecha Registro Compra Venta |
| `fecha_registro_compra_venta_humana` | string | Fecha Registro Compra Venta Humana |
| `saldo_acumulado` | integer | Saldo Acumulado |
| `ruta` | [RutaLM](#model-rutalm) |  |

<a id='model-itemmatches'></a>
### ItemMatches

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `movimiento_id` | string | Movimiento Id |
| `fecha_match` | integer | Fecha Match |
| `fecha_match_humana` | string | Fecha Match Humana |
| `fecha_movimiento` | integer | Fecha Movimiento |
| `fecha_movimiento_humana` | string | Fecha Movimiento Humana |
| `fecha_emision_obligacion` | integer | Fecha Emision Obligacion |
| `fecha_emision_obligacion_humana` | string | Fecha Emision Obligacion Humana |
| `folio` | string | Folio |
| `descripción` | string | Descripción |
| `emisor_obligacion` | [Obligacion](#model-obligacion) |  |
| `receptor_obligacion` | [Obligacion](#model-obligacion) |  |
| `tipo_obligacion` | string | Tipo Obligacion |
| `tipo_cambio` | number | Tipo Cambio |
| `monto_match` | number | Monto Match |
| `monto_local` | number | Monto Local |
| `monto_original_movimiento` | integer | Monto Original Movimiento |
| `abono` | boolean | Abono |
| `comentario` | string | Comentario |
| `invertido` | boolean | Invertido |
| `pagado` | boolean | Pagado |
| `descripcion_primer_item` | string | Descripcion Primer Item |
| `email_usuario_match` | string | Email Usuario Match |

<a id='model-itemorg'></a>
### ItemOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `name` | string | Name |
| `real_name` | string | Real Name |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `country` | string | Country |
| `activated` | boolean | Activated |
| `sub_domain` | string | Sub Domain |
| `created_at` | string | Created At |
| `owner_id` | string | Owner Id |
| `trial` | [TrialInfoOrg](#model-trialinfoorg) |  |
| `plan` | [PlanInfoOrg](#model-planinfoorg) |  |
| `test` | [TestInfoOrg](#model-testinfoorg) |  |
| `settings` | [SettingsOrg](#model-settingsorg) |  |
| `internal_use` | [InternalUseOrg](#model-internaluseorg) |  |
| `size` | string | Size |
| `updated_at` | string | Updated At |
| `sort` | integer | Sort |
| `id` | string | Id |

<a id='model-itempending'></a>
### ItemPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `xml` | [XmlPending](#model-xmlpending) |  |
| `amounts` | [AmountsPending](#model-amountspending) |  |
| `fecha_emision` | integer | Fecha Emision |
| `fecha_humana_emision` | string | Fecha Humana Emision |
| `numero` | string | Numero |
| `pagado` | boolean | Pagado |
| `recibida` | boolean | Recibida |
| `emisor` | [EmisorPending](#model-emisorpending) |  |
| `receptor` | [ReceptorPending](#model-receptorpending) |  |
| `total` | [TotalPending](#model-totalpending) |  |
| `codigo` | string | Codigo |
| `tipo` | string | Tipo |
| `recepcion` | [ReceptionPending](#model-receptionpending) |  |

<a id='model-itemprod'></a>
### ItemProd

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `xml` | object | Xml |
| `reception` | object | Reception |
| `fecha_emision` | integer | Fecha Emision |
| `fecha_humana_emision` | string | Fecha Humana Emision |
| `numero` | string | Numero |
| `tipo` | string | Tipo |
| `codigo` | string | Codigo |
| `pagado` | boolean | Pagado |
| `recibida` | boolean | Recibida |
| `emisor` | [EmisorProd](#model-emisorprod) |  |
| `receptor` | [ReceptorProd](#model-receptorprod) |  |
| `total` | [TotalProd](#model-totalprod) |  |
| `producto` | [ProductoProd](#model-productoprod) |  |
| `recepcion` | [RecepcionProd](#model-recepcionprod) |  |
| `cesion` | [CesionProd](#model-cesionprod) |  |

<a id='model-itemsaldo'></a>
### ItemSaldo

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `numero_cuenta` | string | Numero Cuenta |
| `saldo_disponible` | number | Saldo Disponible |
| `saldo_contable` | number | Saldo Contable |
| `fecha` | string | Fecha |
| `fecha_humana` | string | Fecha Humana |

<a id='model-itemtax'></a>
### ItemTax

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `tipo` | string | Tipo |
| `periodo` | string | Periodo |
| `anio` | string | Anio |
| `mes` | string | Mes |
| `detalle` | Array<[DetailTaxlogs](#model-detailtaxlogs)> | Detalle |

<a id='model-levellm'></a>
### LevelLM

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `nombre` | string | Nombre |
| `nivel` | string | Nivel |
| `codigo` | string | Codigo |

<a id='model-listadoev'></a>
### ListadoEV

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `cantidad` | integer | Cantidad |
| `usuario` | string | Usuario |

<a id='model-logconexion'></a>
### LogConexion

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `error` | boolean | Error |
| `mensaje` | string | Mensaje |

<a id='model-masinfo'></a>
### MasInfo

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `contraparte` | string | Contraparte |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `banco` | string | Banco |
| `numero_cuenta` | string | Numero Cuenta |
| `mensaje` | object | Mensaje |

<a id='model-match'></a>
### Match

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `fecha_emision` | integer | Fecha Emision |
| `fecha_emision_humana` | string | Fecha Emision Humana |
| `tipo_obligacion` | string | Tipo Obligacion |
| `subtipo_obligacion` | string | Subtipo Obligacion |
| `es_reverso` | boolean | Es Reverso |
| `numero` | string | Numero |
| `monto` | integer | Monto |
| `monto_conciliado` | integer | Monto Conciliado |
| `fecha_match` | integer | Fecha Match |
| `fecha_match_humana` | string | Fecha Match Humana |
| `email_usuario_match` | string | Email Usuario Match |
| `tipo_cambio` | number | Tipo Cambio |
| `monto_local` | number | Monto Local |
| `rut_contraparte` | string | Rut Contraparte |
| `razon_social_contraparte` | string | Razon Social Contraparte |
| `descripcion_primer_item` | string | Descripcion Primer Item |

<a id='model-matchessincontabilizarev'></a>
### MatchesSinContabilizarEV

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `descripcion` | string | Descripcion |
| `cantidad` | object | Cantidad |

<a id='model-matchesusuariosev'></a>
### MatchesUsuariosEV

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `descripcion` | string | Descripcion |
| `listado` | Array<[ListadoEV](#model-listadoev)> | Listado |

<a id='model-monto'></a>
### Monto

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `valor` | integer | Valor |
| `currency` | string | Currency |
| `descuento` | integer | Descuento |

<a id='model-movimientossincontabilizarev'></a>
### MovimientosSinContabilizarEV

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `descripcion` | string | Descripcion |
| `cantidad` | object | Cantidad |

<a id='model-nvvalidator'></a>
### NVValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `fecha_emision` **(Req)** | string | Fecha Emision |
| `folio` **(Req)** | string | Folio |
| `emisor` **(Req)** | [DTEEntityValidator](#model-dteentityvalidator) |  |
| `receptor` **(Req)** | [DTEReceiverValidator](#model-dtereceivervalidator) |  |
| `detalle` **(Req)** | Array<object> | Detalle |

<a id='model-obligacion'></a>
### Obligacion

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `razon_social` | string | Razon Social |

<a id='model-obligationnvvalidator'></a>
### ObligationNVValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut_empresa` **(Req)** | string | Rut Empresa |
| `dv_empresa` **(Req)** | string | Dv Empresa |
| `notas` **(Req)** | Array<[NVValidator](#model-nvvalidator)> | Notas |

<a id='model-obligationvalidator'></a>
### ObligationValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `organization_rut` **(Req)** | string | Organization Rut |
| `oficina_partes` | boolean | Oficina Partes |
| `dte` **(Req)** | [DTEValidator](#model-dtevalidator) |  |

<a id='model-onboardingorg'></a>
### OnboardingOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `start_date` | string | Start Date |
| `end_date` | string | End Date |
| `onboarder` | string | Onboarder |
| `days` | integer | Days |

<a id='model-order'></a>
### Order

An enumeration.

*Sin propiedades o estructura compleja.*

<a id='model-orderpurchaseitemvalidator'></a>
### OrderPurchaseItemValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `fecha_emision` **(Req)** | string | Fecha Emision |
| `folio` **(Req)** | string | Folio |
| `currency` | string | Currency |
| `emitido` | boolean | Emitido |
| `exenta` | boolean | Exenta |
| `emisor` **(Req)** | [DTEEntityValidator](#model-dteentityvalidator) |  |
| `receptor` **(Req)** | [DTEReceiverValidator](#model-dtereceivervalidator) |  |
| `condiciones_pago` | string | Condiciones Pago |
| `notas` | string | Notas |
| `nota_documento` | string | Nota Documento |
| `fecha_pago` | Array<[FechaPagoValidator](#model-fechapagovalidator)> | Fecha Pago |
| `detalle` **(Req)** | Array<[DetailsOCValidator](#model-detailsocvalidator)> | Detalle |

<a id='model-orderpurchasevalidator'></a>
### OrderPurchaseValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut_empresa` **(Req)** | string | Rut Empresa |
| `dv_empresa` **(Req)** | string | Dv Empresa |
| `ordenes_compra` **(Req)** | Array<[OrderPurchaseItemValidator](#model-orderpurchaseitemvalidator)> | Ordenes Compra |

<a id='model-organizationvalidator'></a>
### OrganizationValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `nombre` **(Req)** | string | Nombre |
| `razon_social` **(Req)** | string | Razon Social |
| `rut` **(Req)** | string | Rut |
| `dv` **(Req)** | string | Dv |
| `rut_facturador` **(Req)** | string | Rut Facturador |
| `dv_facturador` **(Req)** | string | Dv Facturador |

<a id='model-pdfbh'></a>
### PDFBH

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `has` | boolean | Has |
| `reference` | string | Reference |

<a id='model-planinfoorg'></a>
### PlanInfoOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `state` | string | State |
| `since` | string | Since |
| `what` | [WhatDetailsOrg](#model-whatdetailsorg) |  |

<a id='model-productoprod'></a>
### ProductoProd

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `name` | string | Name |
| `numero` | integer | Numero |
| `unidad` | string | Unidad |
| `unit_price` | integer | Unit Price |
| `total_price` | integer | Total Price |

<a id='model-recepcionprod'></a>
### RecepcionProd

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `estado` | string | Estado |
| `descripcion_estado` | string | Descripcion Estado |
| `fecha_recepcion` | integer | Fecha Recepcion |
| `fecha_recepcion_humana` | string | Fecha Recepcion Humana |

<a id='model-receptiondte'></a>
### ReceptionDTE

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `estado` | string | Estado |
| `descripcion_estado` | string | Descripcion Estado |
| `fecha_recepcion` | integer | Fecha Recepcion |
| `fecha_recepcion_humana` | string | Fecha Recepcion Humana |

<a id='model-receptionpending'></a>
### ReceptionPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `estado` | string | Estado |
| `descripcion_estado` | string | Descripcion Estado |
| `fecha_recepcion` | integer | Fecha Recepcion |
| `fecha_recepcion_humana` | string | Fecha Recepcion Humana |

<a id='model-receptorbh'></a>
### ReceptorBH

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `razon_social` | string | Razon Social |

<a id='model-receptordte'></a>
### ReceptorDTE

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `razon_social` | string | Razon Social |

<a id='model-receptorinvoice'></a>
### ReceptorInvoice

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `razon_social` | string | Razon Social |

<a id='model-receptorpending'></a>
### ReceptorPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `razon_social` | string | Razon Social |

<a id='model-receptorprod'></a>
### ReceptorProd

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut` | string | Rut |
| `dv` | string | Dv |
| `razon_social` | string | Razon Social |

<a id='model-record'></a>
### Record

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |
| `fecha_ultima_actualizacion` | integer | Fecha Ultima Actualizacion |
| `banco` | string | Banco |
| `numero_cuenta` | string | Numero Cuenta |
| `cuenta_validada` | boolean | Cuenta Validada |
| `tipo_moneda` | string | Tipo Moneda |
| `log_conexion` | [LogConexion](#model-logconexion) |  |

<a id='model-recordbh'></a>
### RecordBH

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `fecha_ultima_actualizacion` | integer | Fecha Ultima Actualizacion |
| `fecha_humana_ultima_actualizacion` | string | Fecha Humana Ultima Actualizacion |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-recordbalance'></a>
### RecordBalance

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `rut_empresa` | string | Rut Empresa |
| `dv_empresa` | string | Dv Empresa |
| `items` | integer | Items |

<a id='model-recordcompanypending'></a>
### RecordCompanyPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |
| `rut_empresa` | string | Rut Empresa |
| `dv_empresa` | string | Dv Empresa |

<a id='model-recordconex'></a>
### RecordConex

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-recorddte'></a>
### RecordDTE

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `fecha_ultima_actualizacion` | integer | Fecha Ultima Actualizacion |
| `fecha_humana_ultima_actualizacion` | string | Fecha Humana Ultima Actualizacion |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-recorddataplan'></a>
### RecordDataPlan

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `items` | integer | Items |

<a id='model-recordeerr'></a>
### RecordEERR

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `rut_empresa` | string | Rut Empresa |
| `dv_empresa` | string | Dv Empresa |
| `anio` | integer | Anio |
| `items` | integer | Items |

<a id='model-recordinvoice'></a>
### RecordInvoice

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `fecha_ultima_actualizacion` | integer | Fecha Ultima Actualizacion |
| `fecha_humana_ultima_actualizacion` | string | Fecha Humana Ultima Actualizacion |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-recordinvoicetransfer'></a>
### RecordInvoiceTransfer

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `fecha_ultima_actualizacion` | integer | Fecha Ultima Actualizacion |
| `fecha_humana_ultima_actualizacion` | string | Fecha Humana Ultima Actualizacion |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-recordld'></a>
### RecordLD

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `rut_empresa` | string | Rut Empresa |
| `dv_empresa` | string | Dv Empresa |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-recordlm'></a>
### RecordLM

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `rut_empresa` | string | Rut Empresa |
| `dv_empresa` | string | Dv Empresa |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-recordorg'></a>
### RecordOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-recordpending'></a>
### RecordPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `items` | integer | Items |

<a id='model-recordprod'></a>
### RecordProd

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `fecha_ultima_actualizacion` | integer | Fecha Ultima Actualizacion |
| `fecha_humana_ultima_actualizacion` | string | Fecha Humana Ultima Actualizacion |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-recordsaldo'></a>
### RecordSaldo

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `fecha_ultima_actualizacion` | string | Fecha Ultima Actualizacion |
| `fecha_humana_ultima_actualizacion` | integer | Fecha Humana Ultima Actualizacion |
| `banco` | string | Banco |
| `cuenta_validada` | boolean | Cuenta Validada |
| `numero_cuenta` | string | Numero Cuenta |
| `tipo_moneda` | string | Tipo Moneda |
| `log_conexion` | [LogConexion](#model-logconexion) |  |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-recordtax'></a>
### RecordTax

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_records` | integer | Total Records |
| `items` | integer | Items |
| `limit` | integer | Limit |
| `offset` | integer | Offset |

<a id='model-reporttypes'></a>
### ReportTypes

An enumeration.

*Sin propiedades o estructura compleja.*

<a id='model-responsedata'></a>
### ResponseData

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` **(Req)** | [Record](#model-record) |  |
| `items` **(Req)** | Array<[Item](#model-item)> | Items |

<a id='model-responsedatabh'></a>
### ResponseDataBH

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordBH](#model-recordbh) |  |
| `items` | Array<[ItemBH](#model-itembh)> | Items |

<a id='model-responsedatabalance'></a>
### ResponseDataBalance

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordBalance](#model-recordbalance) |  |
| `items` | Array<[ItemBalance](#model-itembalance)> | Items |

<a id='model-responsedatacompanypending'></a>
### ResponseDataCompanyPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordCompanyPending](#model-recordcompanypending) |  |
| `items` | Array<[ItemCompanyPending](#model-itemcompanypending)> | Items |

<a id='model-responsedataconex'></a>
### ResponseDataConex

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordConex](#model-recordconex) |  |
| `items` | Array<[ItemConex](#model-itemconex)> | Items |

<a id='model-responsedatadte'></a>
### ResponseDataDTE

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordDTE](#model-recorddte) |  |
| `items` | Array<[ItemDTE](#model-itemdte)> | Items |

<a id='model-responsedataeerr'></a>
### ResponseDataEERR

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordEERR](#model-recordeerr) |  |
| `items` | Array<[ItemEERR](#model-itemeerr)> | Items |

<a id='model-responsedatainvoice'></a>
### ResponseDataInvoice

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordInvoice](#model-recordinvoice) |  |
| `items` | Array<[ItemInvoice](#model-iteminvoice)> | Items |

<a id='model-responsedatainvoicetransfer'></a>
### ResponseDataInvoiceTransfer

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordInvoiceTransfer](#model-recordinvoicetransfer) |  |
| `items` | Array<[ItemInvoiceTransfer](#model-iteminvoicetransfer)> | Items |

<a id='model-responsedatald'></a>
### ResponseDataLD

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordLD](#model-recordld) |  |
| `items` | Array<[ItemLD](#model-itemld)> | Items |

<a id='model-responsedatalm'></a>
### ResponseDataLM

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordLM](#model-recordlm) |  |
| `items` | Array<[ItemLM](#model-itemlm)> | Items |

<a id='model-responsedatamatches'></a>
### ResponseDataMatches

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [Record](#model-record) |  |
| `items` | Array<[ItemMatches](#model-itemmatches)> | Items |

<a id='model-responsedataorg'></a>
### ResponseDataOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordOrg](#model-recordorg) |  |
| `items` | Array<[ItemOrg](#model-itemorg)> | Items |

<a id='model-responsedatapending'></a>
### ResponseDataPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordPending](#model-recordpending) |  |
| `items` | Array<[ItemPending](#model-itempending)> | Items |

<a id='model-responsedataprod'></a>
### ResponseDataProd

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordProd](#model-recordprod) |  |
| `items` | Array<[ItemProd](#model-itemprod)> | Items |

<a id='model-responsedatasaldo'></a>
### ResponseDataSaldo

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordSaldo](#model-recordsaldo) |  |
| `items` | Array<[ItemSaldo](#model-itemsaldo)> | Items |

<a id='model-responsedatatax'></a>
### ResponseDataTax

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `records` | [RecordTax](#model-recordtax) |  |
| `items` | Array<[ItemTax](#model-itemtax)> | Items |

<a id='model-responsemodel'></a>
### ResponseModel

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseData](#model-responsedata) |  |

<a id='model-responsemodelbh'></a>
### ResponseModelBH

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataBH](#model-responsedatabh) |  |

<a id='model-responsemodelbalance'></a>
### ResponseModelBalance

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataBalance](#model-responsedatabalance) |  |

<a id='model-responsemodelcompanypending'></a>
### ResponseModelCompanyPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataCompanyPending](#model-responsedatacompanypending) |  |

<a id='model-responsemodelconex'></a>
### ResponseModelConex

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataConex](#model-responsedataconex) |  |

<a id='model-responsemodeldte'></a>
### ResponseModelDTE

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataDTE](#model-responsedatadte) |  |

<a id='model-responsemodeleerr'></a>
### ResponseModelEERR

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataEERR](#model-responsedataeerr) |  |

<a id='model-responsemodelev'></a>
### ResponseModelEV

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [DataEV](#model-dataev) |  |
| `request_counter` | integer | Request Counter |

<a id='model-responsemodelid'></a>
### ResponseModelId

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | string | Id |
| `fecha` | integer | Fecha |
| `fecha_humana` | string | Fecha Humana |
| `numero_documento` | string | Numero Documento |
| `reconocido` | boolean | Reconocido |
| `abono` | boolean | Abono |
| `sucursal` | string | Sucursal |
| `descripcion` | string | Descripcion |
| `monto` | integer | Monto |
| `monto_original` | integer | Monto Original |
| `saldo_insoluto` | integer | Saldo Insoluto |
| `ids_relacionados` | Array<string> | Ids Relacionados |
| `matches` | Array<[Match](#model-match)> | Matches |
| `contablemente_correcto` | string | Contablemente Correcto |
| `request_counter` | integer | Request Counter |
| `fecha_humana_creacion` | string | Fecha Humana Creacion |
| `fecha_creacion` | integer | Fecha Creacion |

<a id='model-responsemodelinvoice'></a>
### ResponseModelInvoice

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataInvoice](#model-responsedatainvoice) |  |

<a id='model-responsemodelinvoicetransfer'></a>
### ResponseModelInvoiceTransfer

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataInvoiceTransfer](#model-responsedatainvoicetransfer) |  |

<a id='model-responsemodelld'></a>
### ResponseModelLD

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataLD](#model-responsedatald) |  |

<a id='model-responsemodellm'></a>
### ResponseModelLM

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataLM](#model-responsedatalm) |  |

<a id='model-responsemodelmatches'></a>
### ResponseModelMatches

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataMatches](#model-responsedatamatches) |  |

<a id='model-responsemodelorg'></a>
### ResponseModelOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataOrg](#model-responsedataorg) |  |

<a id='model-responsemodelpending'></a>
### ResponseModelPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataPending](#model-responsedatapending) |  |

<a id='model-responsemodelplan'></a>
### ResponseModelPlan

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [DataPlan](#model-dataplan) |  |

<a id='model-responsemodelprod'></a>
### ResponseModelProd

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataProd](#model-responsedataprod) |  |

<a id='model-responsemodelsaldo'></a>
### ResponseModelSaldo

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataSaldo](#model-responsedatasaldo) |  |

<a id='model-responsemodeltax'></a>
### ResponseModelTax

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [ResponseDataTax](#model-responsedatatax) |  |

<a id='model-rutald'></a>
### RutaLD

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `level1` | [LevelLM](#model-levellm) |  |
| `level2` | [LevelLM](#model-levellm) |  |
| `level3` | [LevelLM](#model-levellm) |  |
| `level4` | [LevelLM](#model-levellm) |  |

<a id='model-rutalm'></a>
### RutaLM

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `level1` | [LevelLM](#model-levellm) |  |
| `level2` | [LevelLM](#model-levellm) |  |
| `level3` | [LevelLM](#model-levellm) |  |
| `level4` | [LevelLM](#model-levellm) |  |

<a id='model-settingsorg'></a>
### SettingsOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `collection` | boolean | Collection |
| `embed` | [EmbedOrg](#model-embedorg) |  |
| `billing` | [BillingInfoOrg](#model-billinginfoorg) |  |
| `address` | string | Address |
| `priorityAutoMatch` | string | Priorityautomatch |
| `giro` | string | Giro |
| `ppm_rate` | integer | Ppm Rate |
| `proporcionalidad` | boolean | Proporcionalidad |
| `recurring_revenue` | boolean | Recurring Revenue |
| `representante` | string | Representante |
| `vat_recovery` | boolean | Vat Recovery |
| `din` | boolean | Din |
| `impuestos_especiales` | boolean | Impuestos Especiales |
| `iva_digital` | boolean | Iva Digital |
| `autoMatch` | boolean | Automatch |
| `autoMatchCargos` | boolean | Automatchcargos |
| `autoMatchNv` | boolean | Automatchnv |
| `linkNVDTE` | boolean | Linknvdte |
| `tax_regime` | [TaxRegimeInfoOrg](#model-taxregimeinfoorg) |  |
| `link_nc_nd` | boolean | Link Nc Nd |
| `more_data_to_movement` | boolean | More Data To Movement |

<a id='model-taxregimeinfoorg'></a>
### TaxRegimeInfoOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `code` | string | Code |
| `name` | string | Name |
| `tipo_contabilidad` | string | Tipo Contabilidad |
| `tax` | integer | Tax |

<a id='model-testinfoorg'></a>
### TestInfoOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `is_` | boolean | Is  |
| `when` | string | When |
| `who` | string | Who |

<a id='model-totalbh'></a>
### TotalBH

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `total_honorario` | integer | Total Honorario |
| `impuesto` | integer | Impuesto |

<a id='model-totaldte'></a>
### TotalDTE

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `neto` | integer | Neto |
| `exento` | integer | Exento |
| `impuesto` | integer | Impuesto |
| `porcentaje_impuesto` | string | Porcentaje Impuesto |
| `detalles_otros_impuestos` | Array<[DetalleImpuestos](#model-detalleimpuestos)> | Detalles Otros Impuestos |
| `otros_impuestos` | integer | Otros Impuestos |
| `total` | integer | Total |

<a id='model-totalinvoice'></a>
### TotalInvoice

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `neto` | integer | Neto |
| `exento` | integer | Exento |
| `impuesto` | integer | Impuesto |
| `porcentaje_impuesto` | string | Porcentaje Impuesto |
| `otros_impuestos` | integer | Otros Impuestos |
| `total` | integer | Total |

<a id='model-totalmovimientosev'></a>
### TotalMovimientosEV

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `descripcion` | string | Descripcion |
| `cantidad` | integer | Cantidad |

<a id='model-totalmovimientosmatchesev'></a>
### TotalMovimientosMatchesEV

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `descripcion` | string | Descripcion |
| `cantidad` | object | Cantidad |

<a id='model-totalpending'></a>
### TotalPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `neto` | integer | Neto |
| `exento` | integer | Exento |
| `impuesto` | integer | Impuesto |
| `porcentaje_impuesto` | string | Porcentaje Impuesto |
| `otros_impuestos` | integer | Otros Impuestos |
| `total` | integer | Total |

<a id='model-totalprod'></a>
### TotalProd

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `neto` | integer | Neto |
| `exento` | integer | Exento |
| `impuesto` | integer | Impuesto |
| `porcentaje_impuesto` | string | Porcentaje Impuesto |
| `otros_impuestos` | integer | Otros Impuestos |
| `detalles_otros_impuestos` | Array<[DetalleImpuestos](#model-detalleimpuestos)> | Detalles Otros Impuestos |
| `total` | integer | Total |

<a id='model-trialinfoorg'></a>
### TrialInfoOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `start` | string | Start |
| `days` | integer | Days |
| `is_` | boolean | Is  |
| `finished` | boolean | Finished |

<a id='model-updateconnectionvalidator'></a>
### UpdateConnectionValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `proveedor` | string | Proveedor |
| `rut_empresa` **(Req)** | string | Rut Empresa |
| `dv_empresa` **(Req)** | string | Dv Empresa |
| `categoria` **(Req)** | string | Categoria |
| `numero_cuenta` | string | Numero Cuenta |

<a id='model-updateresponse'></a>
### UpdateResponse

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [functions___src__models__connections__DataResponse](#model-functions___src__models__connections__dataresponse) |  |

<a id='model-validationerror'></a>
### ValidationError

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `loc` **(Req)** | Array<object> | Location |
| `msg` **(Req)** | string | Message |
| `type` **(Req)** | string | Error Type |

<a id='model-webhookdeleteresponse'></a>
### WebhookDeleteResponse

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` **(Req)** | boolean | Status |
| `message` **(Req)** | string | Message |
| `data` | object | Data |

<a id='model-webhookdeletevalidator'></a>
### WebhookDeleteValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut` **(Req)** | string | Rut |

<a id='model-webhookvalidationresponse'></a>
### WebhookValidationResponse

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` **(Req)** | boolean | Status |
| `data` | object | Data |
| `message` | string | Message |

<a id='model-webhookvalidator'></a>
### WebhookValidator

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `rut` **(Req)** | string | Rut |
| `url` **(Req)** | string | Url |
| `token` | string | Token |

<a id='model-whatdetailsorg'></a>
### WhatDetailsOrg

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `details` | Array<string> | Details |
| `cassius` | [CassiusInfoOrg](#model-cassiusinfoorg) |  |
| `accountant` | string | Accountant |
| `balance_start_date` | string | Balance Start Date |
| `rrhh_platform` | string | Rrhh Platform |
| `type` | string | Type |
| `empleados` | integer | Empleados |
| `dte_start_date` | string | Dte Start Date |
| `vendedor` | string | Vendedor |
| `monto` | [Monto](#model-monto) |  |
| `alianza` | string | Alianza |
| `acuerdo_comercial` | string | Acuerdo Comercial |
| `onboarding` | [OnboardingOrg](#model-onboardingorg) |  |
| `balance_range` | string | Balance Range |

<a id='model-xmlpending'></a>
### XmlPending

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `has` | boolean | Has |
| `reference` | string | Reference |

<a id='model-functions___src__models__connections__dataresponse'></a>
### functions___src__models__connections__DataResponse

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `respuesta` **(Req)** | string | Respuesta |

<a id='model-functions___src__models__organizations__registerresponse'></a>
### functions___src__models__organizations__RegisterResponse

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` **(Req)** | boolean | Status |
| `data` | object | Data |

<a id='model-functions___src__models__transactions__dataresponse'></a>
### functions___src__models__transactions__DataResponse

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `respuesta` **(Req)** | string | Respuesta |

<a id='model-functions___src__models__transactions__registerresponse'></a>
### functions___src__models__transactions__RegisterResponse

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `status` | boolean | Status |
| `data` | [functions___src__models__transactions__DataResponse](#model-functions___src__models__transactions__dataresponse) |  |
| `logs` | Array<string> | Logs |

<a id='model-taxtypes'></a>
### taxTypes

An enumeration.

*Sin propiedades o estructura compleja.*

## Matriz de Capacidades

| Métrica | Cantidad |
| :--- | :--- |
| Endpoints Totales | 31 |
| Modelos de Datos | 164 |
