# Skualo Cache

Este directorio almacena caché de DTEs procesados para evitar consultas repetidas a la API.

## Archivos

- `dte_status_{RUT}.json` - Estado de contabilización por DTE

## Estructura

```json
{
  "last_updated": "2025-12-29T23:00:00",
  "dtes": {
    "FACE-12345": {"contabilizado": true, "checked_at": "2025-12-29"},
    "FACE-12346": {"contabilizado": false, "checked_at": "2025-12-29"}
  }
}
```

## Limpieza

Los registros más antiguos de 90 días se pueden limpiar.

