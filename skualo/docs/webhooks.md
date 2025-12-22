# Webhooks Skualo

## ¿Qué son?

Los webhooks permiten que Skualo **notifique automáticamente** a tu servidor cuando ocurre un evento, en lugar de tener que consultar constantemente la API.

---

## Formato de Notificación

Skualo envía un **POST** con JSON:

```json
{
    "tipoEvento": "DOCUMENTO_CREATED",
    "identificador": "9f077032-f346-495d-8008-005a9449950c"
}
```

---

## Tipos de Eventos Disponibles

| Objeto | Eventos |
|--------|---------|
| **Documentos** | `DOCUMENTO_CREATED`, `DOCUMENTO_UPDATED`, `DOCUMENTO_DELETED` |
| **Comprobantes** | `COMPROBANTE_CREATED`, `COMPROBANTE_UPDATED`, `COMPROBANTE_DELETED` |
| **Auxiliares** | `AUXILIAR_CREATED`, `AUXILIAR_UPDATED` |
| **Direcciones** | `DIRECCION_CREATED`, `DIRECCION_UPDATED` |
| **Contactos** | `CONTACTO_CREATED`, `CONTACTO_UPDATED` |
| **Ficha Trabajador** | `FICHA_CREATED`, `FICHA_UPDATED` |
| **Licencia Médica** | `LICENCIA_CREATED`, `LICENCIA_UPDATED`, `LICENCIA_DELETED` |

---

## Requisitos del Endpoint

1. **Recibir POST** con JSON
2. **Responder 2xx** rápidamente
3. **Procesar de forma asíncrona** (no bloquear)
4. Si falla, Skualo reintenta **hasta 10 veces**

---

## Casos de Uso para Nosotros

### 1. Nuevo Documento Recibido
```
DOCUMENTO_CREATED → Notificar por Telegram
```

### 2. Documento Contabilizado
```
DOCUMENTO_UPDATED → Actualizar reporte de pendientes
```

### 3. Nuevo Comprobante
```
COMPROBANTE_CREATED → Verificar conciliación bancaria
```

---

## Implementación con el Bot de Telegram

```python
from flask import Flask, request, jsonify
from skualo import SkualoControl
import asyncio

app = Flask(__name__)
ctrl = SkualoControl()

# Tu función para enviar a Telegram
async def notificar_telegram(mensaje):
    # Implementar envío a Telegram
    pass

@app.route('/webhook/skualo', methods=['POST'])
def webhook_skualo():
    # 1. Obtener evento
    data = request.json
    tipo_evento = data.get('tipoEvento')
    identificador = data.get('identificador')
    
    # 2. Responder 2xx inmediatamente
    response = jsonify({'status': 'ok'})
    
    # 3. Procesar de forma asíncrona
    if tipo_evento == 'DOCUMENTO_CREATED':
        # Nuevo documento - notificar
        asyncio.create_task(notificar_telegram(
            f"📄 Nuevo documento recibido\nID: {identificador}"
        ))
    
    elif tipo_evento == 'COMPROBANTE_CREATED':
        # Nuevo comprobante - verificar si hay pendientes
        asyncio.create_task(notificar_telegram(
            f"📋 Nuevo comprobante contable\nID: {identificador}"
        ))
    
    return response, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## Flujo Completo con Bot

```
┌─────────────────┐
│  SKUALO ERP     │
│                 │
│ Documento nuevo │
└────────┬────────┘
         │
         ▼ POST /webhook/skualo
┌─────────────────┐
│  TU SERVIDOR    │
│                 │
│ - Recibe evento │
│ - Responde 200  │
│ - Procesa async │
└────────┬────────┘
         │
         ▼ API Telegram
┌─────────────────┐
│  BOT TELEGRAM   │
│                 │
│ "📄 Nuevo doc   │
│  de Proveedor X"│
└─────────────────┘
```

---

## API de Webhooks ✅ VALIDADO

### Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/{RUT}/integraciones/webhooks` | Listar webhooks |
| `POST` | `/{RUT}/integraciones/webhooks` | Crear webhook |
| `GET` | `/{RUT}/integraciones/webhooks/{id}` | Obtener webhook |
| `PUT` | `/{RUT}/integraciones/webhooks` | Actualizar webhook |
| `DELETE` | `/{RUT}/integraciones/webhooks/{id}` | Eliminar webhook |

### Crear Webhook

```python
import requests

url = "https://api.skualo.cl/77285542-7/integraciones/webhooks"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer {TOKEN}",
    "content-type": "application/json"
}
payload = {
    "url": "https://tu-servidor.com/webhook/skualo",
    "eventos": ["DOCUMENTO_CREATED", "DOCUMENTO_UPDATED", "COMPROBANTE_CREATED"]
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
# {"href": "https://api.skualo.cl/.../webhooks/{id}", "id": "uuid-del-webhook"}
```

### Listar Webhooks

```python
response = requests.get(
    "https://api.skualo.cl/77285542-7/integraciones/webhooks",
    headers=headers
)
print(response.json())  # Lista de webhooks configurados
```

### Eliminar Webhook

```python
webhook_id = "4b22b198-1398-4658-83eb-7391487139a5"
response = requests.delete(
    f"https://api.skualo.cl/77285542-7/integraciones/webhooks/{webhook_id}",
    headers=headers
)
# Status: 204 No Content = Eliminado exitosamente
```

---

## Pendiente Preguntar a Soporte

1. **¿Hay evento para DTEs recibidos del SII?** (ej: `DTE_RECIBIDO`, `SII_DTE_CREATED`)
2. **¿Hay evento para movimientos bancarios?** (ej: `MOVIMIENTO_BANCARIO_CREATED`)
3. **¿Se filtran automáticamente por empresa o hay que usar un webhook por tenant?**

