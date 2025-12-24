# Respuestas Soporte Skualo API

**Fecha:** 23 de Diciembre 2025

> **Nota importante del soporte:** La API está pensada para consultar información de la base de datos, no para reemplazar la interfaz del sistema.

---

## Consultas y Respuestas

### 1. ¿Cómo aprobar DTEs recibidos pendientes?

**Respuesta:** El endpoint es:
```
POST sii/dte/recibidos/{id}/aprobar
```
El `id` se debe obtener del listado de DTEs recibidos (`GET sii/dte/recibidos`).

### 2. ¿Existe endpoint para contabilizar movimientos?

**Respuesta:** ❌ No hay un endpoint para contabilizar. 
> Esto debe hacerse desde la interfaz del sistema.

### 3. ¿Existe endpoint para conciliar movimientos bancarios?

**Respuesta:** ❌ No hay un endpoint para conciliar.
> La conciliación bancaria debe realizarse desde la interfaz del sistema.

### 4. Endpoint Evolución de Resultados

**Respuesta:** Faltan parámetros necesarios para la consulta. Ver documentación adjunta de "Evolución de Resultados".

**Parámetros requeridos (pendiente revisar documentación):**
- TODO: Agregar parámetros del documento adjunto

### 5. (Sin consulta)

### 6. Filtrar DTEs por tipo de documento

**Respuesta:** La query estaba mal construida.

❌ **Incorrecto:**
```
GET sii/dte?TipoDocumento=FAVE
```

✅ **Correcto:**
```
GET sii/dte?search=IDTipoDocumento eq FAVE
```

### 7. Permisos del Token API

**Respuesta:** El token otorga **permiso total** sobre la API, sin restricción alguna.

---

## Resumen de Limitaciones API

| Funcionalidad | Disponible vía API |
|---------------|:------------------:|
| Consultar DTEs emitidos | ✅ |
| Consultar DTEs recibidos | ✅ |
| Aprobar DTEs recibidos | ✅ |
| Consultar balance/auxiliares | ✅ |
| Consultar movimientos bancarios | ✅ |
| **Contabilizar movimientos** | ❌ |
| **Conciliar bancos** | ❌ |

---

## Sintaxis de Búsqueda (OData)

Para filtrar resultados usar el parámetro `search` con sintaxis OData:

```
?search={campo} eq {valor}
```

**Ejemplos:**
```bash
# Filtrar por tipo de documento
GET /sii/dte?search=IDTipoDocumento eq FAVE

# Filtrar por RUT receptor
GET /sii/dte?search=RutReceptor eq 61219000-3
```

**Operadores disponibles:**
- `eq` - igual a
- `ne` - diferente de
- `gt` - mayor que
- `lt` - menor que
- `ge` - mayor o igual
- `le` - menor o igual
- `contains()` - contiene texto

