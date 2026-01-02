# FINTOC API - Documentación SGCA

## 1. Introducción

Fintoc es una API REST que permite conectar aplicaciones con instituciones financieras chilenas para acceder a información bancaria y fiscal (SII).

**Base URL**: `https://api.fintoc.com/v1`

**Documentación oficial**: [docs.fintoc.com](https://docs.fintoc.com)

---

## 2. Productos Disponibles

| Producto | Descripción | Relevancia SGCA |
|----------|-------------|-----------------|
| **Fiscal API (SII)** | DTEs, facturas emitidas/recibidas | ⚠️ Alternativa a SII directo |
| **Movements API** | Movimientos bancarios en tiempo real | ✅ Conciliación automática |
| **Transfers API** | Envío de pagos programáticos | 🔄 Futuro: pagos automáticos |
| **Payment Initiation** | Cobros via widget | ❌ No aplica |
| **Débito Directo** | Cobros recurrentes | ❌ No aplica |

---

## 3. Autenticación

### API Keys
Obtener desde [Dashboard Fintoc](https://dashboard.fintoc.com/developers/api_keys).

```bash
# Header de autenticación
Authorization: sk_live_xxxxxxxxxxxx
```

| Tipo | Uso |
|------|-----|
| `sk_test_...` | Modo pruebas (sandbox) |
| `sk_live_...` | Modo producción |
| `pk_...` | Clave pública (widget) |

### Link Token
Token temporal que representa la conexión a un banco/SII específico.
- Se obtiene via **Widget Fintoc** (callback `onSuccess`)
- Necesario para la mayoría de endpoints

---

## 4. Flujo de Conexión

```
┌─────────────────────────────────────────────────────────────┐
│  1. Frontend inicializa Widget con public_key               │
│  2. Usuario selecciona banco/SII y se autentica            │
│  3. Widget dispara onSuccess(link_token)                    │
│  4. Frontend envía link_token al Backend                    │
│  5. Backend usa link_token para consultar datos             │
│  6. Webhooks notifican actualizaciones                      │
└─────────────────────────────────────────────────────────────┘
```

### Widget (JavaScript)
```javascript
import { Fintoc } from '@fintoc/fintoc-js';

const widget = await Fintoc.create({
  publicKey: 'pk_live_...',
  holderType: 'business',
  product: 'movements', // o 'invoices' para SII
  onSuccess: (link) => {
    // Enviar link.token al backend
    sendToBackend(link.token);
  },
  onExit: () => console.log('Usuario cerró widget')
});

widget.open();
```

---

## 5. API Reference

### 5.1 Links (Conexiones)

```bash
# Obtener link por ID
GET /links/{link_id}
Authorization: sk_live_...

# Listar todos los links
GET /links
```

**Objeto Link**:
```json
{
  "id": "link_nMNe...",
  "username": "77123456-8",
  "institution": {
    "id": "cl_banco_de_chile",
    "country": "cl"
  },
  "status": "active",
  "refresh_status": "refreshed"
}
```

| Status | Significado |
|--------|-------------|
| `active` | Conectado y actualizando |
| `login_required` | Credenciales expiradas |
| `inactive` | Desconectado |

---

### 5.2 Fiscal API (SII)

**Requiere**: Link conectado a `cl_fiscal_sii`

```bash
# Listar facturas
GET /invoices?link_token=xxx&since=2025-01-01&until=2025-12-31
```

**Objeto Invoice**:
```json
{
  "id": "inv_nMNe...",
  "number": "135",
  "total_amount": 12123,
  "net_amount": 12000,
  "tax_period": "06/2025",
  "issue_type": "received",
  "issuer": {
    "id": "77123456-8",
    "name": "Proveedor SpA"
  },
  "institution_invoice": {
    "document_type": 33,
    "vat_amount": 123,
    "received_at": "2025-06-25T19:27:04.000Z",
    "invoice_status": "registered"
  }
}
```

| document_type | Tipo DTE |
|---------------|----------|
| 33 | Factura Electrónica |
| 34 | Factura Exenta |
| 61 | Nota de Crédito |
| 56 | Nota de Débito |

---

### 5.3 Movements API (Bancos)

**Requiere**: Link conectado a banco (ej: `cl_banco_de_chile`)

```bash
# Listar cuentas
GET /accounts?link_token=xxx

# Listar movimientos de una cuenta
GET /accounts/{account_id}/movements?link_token=xxx&since=2025-01-01
```

**Objeto Movement**:
```json
{
  "id": "mov_BO381...",
  "amount": -59400,
  "currency": "CLP",
  "transaction_date": "2025-04-16T11:31:12.000Z",
  "description": "Transfer to Fintoc SpA",
  "type": "transfer",
  "recipient_account": {
    "holder_name": "Fintoc SpA",
    "number": "1234567890"
  }
}
```

| Campo | Nota |
|-------|------|
| `amount` | Negativo = egreso, Positivo = ingreso |
| `type` | transfer, payment, deposit, withdrawal, etc. |

---

### 5.4 Transfers API

```bash
POST /transfers
Content-Type: application/json
Authorization: sk_live_...

{
  "amount": 100000,
  "currency": "CLP",
  "recipient_account": {
    "holder_id": "77123456-8",
    "number": "1234567890",
    "institution_id": "cl_banco_estado"
  },
  "link_token": "xxx"
}
```

---

## 6. Webhooks

Configurar URL en Dashboard → Developers → Webhooks

### Eventos principales:

| Evento | Descripción |
|--------|-------------|
| `account.refresh_intent.succeeded` | Datos bancarios/SII actualizados |
| `payment_intent.succeeded` | Pago recibido |
| `transfer.succeeded` | Transferencia completada |
| `link.credentials_changed` | Usuario debe re-autenticar |

### Verificación de firma:
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## 7. SDKs Oficiales

| Lenguaje | Instalación | Repositorio |
|----------|-------------|-------------|
| Python | `pip install fintoc` | [fintoc-python](https://github.com/fintoc-com/fintoc-python) |
| Node.js | `npm install fintoc` | [fintoc-node](https://github.com/fintoc-com/fintoc-node) |
| Ruby | `gem install fintoc` | [fintoc-ruby](https://github.com/fintoc-com/fintoc-ruby) |
| React | `npm install @fintoc/fintoc-js` | [fintoc-js](https://github.com/fintoc-com/fintoc-js) |

### Ejemplo Python:
```python
from fintoc import Client

client = Client("sk_live_...")

# Listar links
links = client.links.all()

# Obtener movimientos
movements = client.accounts.movements(
    account_id="acc_xxx",
    link_token="link_token_xxx",
    since="2025-01-01"
)
```

---

## 8. Evaluación para SGCA

### Comparación con alternativas:

| Criterio | Fintoc | Clay | SII Directo |
|----------|--------|------|-------------|
| **SII DTEs** | ✅ Via widget | ✅ Automático | ✅ Directo |
| **Bancos** | ✅ Múltiples | ⚠️ Limitado | ❌ No |
| **Requiere acción usuario** | ⚠️ Sí (widget) | ❌ No | ❌ No |
| **Tiempo real** | ✅ Webhooks | ✅ Polling | ⚠️ Polling |
| **Costo** | Por transacción | Por empresa/mes | Gratis |

### Casos de uso SGCA:

1. **Conciliación bancaria automática** → Movements API
2. **Auditoría SII independiente** → Fiscal API (segunda fuente vs ERP)
3. **Pagos automáticos a proveedores** → Transfers API (futuro)

### Limitaciones:

- Requiere que el usuario se autentique via widget
- Credenciales expiran → usuario debe re-autenticarse
- No apto para automatización 100% sin intervención

---

## 9. Recomendación Estratégica

```
┌─────────────────────────────────────────────────────────────┐
│  CLAY       → Empresas nuevas (automatización completa)    │
│  FINTOC     → Conciliación bancaria multi-banco            │
│  SII DIRECTO → Auditoría independiente / respaldo          │
└─────────────────────────────────────────────────────────────┘
```

Para SGCA, Fintoc es ideal como **complemento** para:
- Obtener movimientos bancarios de bancos no cubiertos por el ERP
- Validar datos SII como segunda fuente independiente

---

## 10. Próximos Pasos

1. [ ] Crear cuenta Fintoc (sandbox)
2. [ ] Implementar widget en frontend de prueba
3. [ ] Crear módulo `sgca-integraciones/fintoc/`
4. [ ] Definir flujo de conexión por empresa
5. [ ] Implementar sync de movimientos bancarios

---

*Última actualización: 2026-01-02*
