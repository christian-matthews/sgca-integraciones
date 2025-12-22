# Control de Pendientes - Skualo ERP API

Este documento describe cómo obtener los 3 reportes de control más importantes a través de la API de Skualo.

---

## 1. 🏦 Movimientos Bancarios Sin Conciliar

### Endpoint
```
GET /{RUT}/bancos/{idCuenta}
```

### Parámetros
- `idCuenta`: Código de cuenta contable del banco (ej: `1102002` para Banco Santander)
- `PageSize`: Cantidad de registros por página (max 100)
- `Page`: Número de página

### Campo Clave
```json
{
  "conciliado": false  // true = conciliado, false = pendiente
}
```

### Ejemplo de Uso
```python
import requests

url = "https://api.skualo.cl/{RUT}/bancos/1102002?PageSize=100"
headers = {"Authorization": "Bearer {TOKEN}"}
response = requests.get(url, headers=headers)

movimientos = response.json().get('items', [])
no_conciliados = [m for m in movimientos if not m.get('conciliado', True)]

print(f"Movimientos sin conciliar: {len(no_conciliados)}")
```

### Campos del Movimiento
| Campo | Descripción |
|-------|-------------|
| `id` | GUID único del movimiento |
| `fecha` | Fecha del movimiento |
| `numDoc` | Número de documento |
| `glosa` | Descripción |
| `montoCargo` | Monto de cargo (egreso) |
| `montoAbono` | Monto de abono (ingreso) |
| `conciliado` | Boolean - si está conciliado |

### Cómo obtener las cuentas bancarias
1. Obtener el Balance Tributario: `GET /{RUT}/contabilidad/reportes/balancetributario/{periodo}`
2. Filtrar cuentas que empiecen con `1102` (Bancos)
3. Usar el código de cuenta como `idCuenta`

---

## 2. 📄 Documentos Pendientes de Aceptar en SII

### Endpoint
```
GET /{RUT}/sii/dte/recibidos
```

### Lógica de Negocio
- Un DTE recibido tiene **8 días** para ser aceptado/rechazado
- Después de 8 días se considera **aceptado tácitamente**
- Solo los documentos con `fechaRespuesta = null` Y menos de 8 días están pendientes

### Campo Clave
```json
{
  "fechaRespuesta": null,  // null = sin respuesta, fecha = respondido
  "creadoEl": "2025-12-15T..."  // Fecha de recepción
}
```

### Ejemplo de Uso
```python
from datetime import datetime

url = "https://api.skualo.cl/{RUT}/sii/dte/recibidos?PageSize=100"
response = requests.get(url, headers=headers)

items = response.json().get('items', [])
hoy = datetime.now()

pendientes_aceptar = []
for doc in items:
    fecha_respuesta = doc.get('fechaRespuesta')
    if fecha_respuesta:
        continue  # Ya respondido
    
    # Calcular días desde recepción
    fecha_recep = datetime.fromisoformat(doc['creadoEl'].split('.')[0])
    dias = (hoy - fecha_recep).days
    
    if dias <= 8:
        pendientes_aceptar.append(doc)

print(f"Pendientes de aceptar: {len(pendientes_aceptar)}")
```

### Campos del DTE Recibido
| Campo | Descripción |
|-------|-------------|
| `idDocumento` | GUID único |
| `rutEmisor` | RUT del proveedor |
| `emisor` | Nombre del proveedor |
| `idTipoDocumento` | Tipo DTE (33=Factura, 61=NC, etc.) |
| `folio` | Número de folio |
| `fechaEmision` | Fecha de emisión |
| `montoTotal` | Monto total |
| `creadoEl` | Fecha de recepción en Skualo |
| `fechaRespuesta` | Fecha de respuesta al SII (null si pendiente) |
| `conAcuseRecibo` | Boolean - si tiene acuse de recibo |

---

## 3. 📋 Documentos Pendientes de Contabilizar

### Lógica
Los documentos pendientes de contabilizar son aquellos que:
1. Están en `/sii/dte/recibidos` (recibidos del SII)
2. Ya están aceptados (> 8 días o con `fechaRespuesta`)
3. **NO** existen en `/documentos/{tipo}/{folio}` (no ingresados al sistema)

### Mapeo de Tipos
| Tipo DTE | Tipo Interno |
|----------|--------------|
| 33 | FACE (Factura Compra Electrónica) |
| 34 | FXCE (Factura Exenta Compra Electrónica) |
| 61 | NCCE (Nota Crédito Compra Electrónica) |
| 56 | NDCE (Nota Débito Compra Electrónica) |

### Ejemplo de Uso
```python
# 1. Obtener DTEs recibidos
r1 = requests.get(f"{BASE}/sii/dte/recibidos?PageSize=100", headers=headers)
dtes = r1.json().get('items', [])

# 2. Mapeo de tipos
tipo_map = {33: 'FACE', 34: 'FXCE', 61: 'NCCE', 56: 'NDCE'}

pendientes_contabilizar = []
hoy = datetime.now()

for dte in dtes:
    # Verificar si está aceptado (> 8 días o con respuesta)
    fecha_respuesta = dte.get('fechaRespuesta')
    fecha_recep = datetime.fromisoformat(dte['creadoEl'].split('.')[0])
    dias = (hoy - fecha_recep).days
    
    if not fecha_respuesta and dias <= 8:
        continue  # Aún pendiente de aceptar
    
    # Verificar si existe en /documentos
    tipo_interno = tipo_map.get(dte['idTipoDocumento'], 'FACE')
    folio = dte['folio']
    
    r2 = requests.get(f"{BASE}/documentos/{tipo_interno}/{folio}", headers=headers)
    
    if r2.status_code == 404:
        # No existe = pendiente de contabilizar
        pendientes_contabilizar.append(dte)

print(f"Pendientes de contabilizar: {len(pendientes_contabilizar)}")
```

---

## Resumen de Endpoints

| Control | Endpoint Principal | Endpoint Auxiliar |
|---------|-------------------|-------------------|
| Movimientos sin conciliar | `GET /{RUT}/bancos/{idCuenta}` | `GET /{RUT}/contabilidad/reportes/balancetributario/{periodo}` |
| Pendientes aceptar SII | `GET /{RUT}/sii/dte/recibidos` | - |
| Pendientes contabilizar | `GET /{RUT}/sii/dte/recibidos` | `GET /{RUT}/documentos/{tipo}/{folio}` |

---

## Endpoints Adicionales Relacionados

### DTEs Emitidos (Ventas)
```
GET /{RUT}/sii/dte
```
Muestra los DTEs emitidos por la empresa (facturas de venta, NC, etc.)

### Documentos Pendientes de Pago/Cobro
```
GET /{RUT}/contabilidad/reportes/analisisporcuenta/{idCuenta}?fechaCorte={fecha}&soloPendientes=true
```
- Cuenta `1107001`: Facturas por cobrar (clientes)
- Cuenta `2110001`: Facturas por pagar (proveedores)

---

## Ejemplo Completo: Script de Control

```python
#!/usr/bin/env python3
"""
Script de control de pendientes - Skualo ERP
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('SKUALO_API_TOKEN')
RUT = '77949039-4'  # CISI
BASE = f'https://api.skualo.cl/{RUT}'
headers = {'Authorization': f'Bearer {TOKEN}', 'accept': 'application/json'}

def control_pendientes():
    hoy = datetime.now()
    print(f"=== CONTROL DE PENDIENTES - {hoy.strftime('%Y-%m-%d')} ===\n")
    
    # 1. MOVIMIENTOS BANCARIOS SIN CONCILIAR
    print("1. MOVIMIENTOS BANCARIOS SIN CONCILIAR")
    print("-" * 50)
    
    # Obtener cuentas bancarias del balance
    r = requests.get(f'{BASE}/contabilidad/reportes/balancetributario/202511', headers=headers)
    cuentas_banco = [c for c in r.json() if c['idCuenta'].startswith('1102')]
    
    total_sin_conciliar = 0
    for cuenta in cuentas_banco:
        r = requests.get(f"{BASE}/bancos/{cuenta['idCuenta']}?PageSize=100", headers=headers)
        if r.ok:
            movs = r.json().get('items', [])
            sin_conc = [m for m in movs if not m.get('conciliado', True)]
            if sin_conc:
                print(f"  {cuenta['cuenta']}: {len(sin_conc)} movimientos")
                total_sin_conciliar += len(sin_conc)
    
    print(f"  TOTAL: {total_sin_conciliar} movimientos sin conciliar\n")
    
    # 2. DOCUMENTOS PENDIENTES DE ACEPTAR SII
    print("2. DOCUMENTOS PENDIENTES DE ACEPTAR EN SII")
    print("-" * 50)
    
    r = requests.get(f'{BASE}/sii/dte/recibidos?PageSize=100', headers=headers)
    dtes = r.json().get('items', [])
    
    pendientes_aceptar = []
    for dte in dtes:
        if dte.get('fechaRespuesta'):
            continue
        try:
            fecha_recep = datetime.fromisoformat(dte['creadoEl'].split('.')[0])
            dias = (hoy - fecha_recep).days
            if dias <= 8:
                pendientes_aceptar.append({**dte, 'dias': dias})
        except:
            pass
    
    for doc in pendientes_aceptar:
        print(f"  {doc['emisor'][:25]:<25} | Folio {doc['folio']:<8} | {doc['dias']} días | ${doc['montoTotal']:,.0f}")
    print(f"  TOTAL: {len(pendientes_aceptar)} documentos\n")
    
    # 3. DOCUMENTOS PENDIENTES DE CONTABILIZAR
    print("3. DOCUMENTOS PENDIENTES DE CONTABILIZAR")
    print("-" * 50)
    
    tipo_map = {33: 'FACE', 34: 'FXCE', 61: 'NCCE', 56: 'NDCE'}
    pendientes_contabilizar = []
    
    for dte in dtes:
        # Si está pendiente de aceptar, skip
        if not dte.get('fechaRespuesta'):
            try:
                fecha_recep = datetime.fromisoformat(dte['creadoEl'].split('.')[0])
                if (hoy - fecha_recep).days <= 8:
                    continue
            except:
                pass
        
        # Verificar si existe en documentos
        tipo = tipo_map.get(dte['idTipoDocumento'], 'FACE')
        r = requests.get(f"{BASE}/documentos/{tipo}/{dte['folio']}", headers=headers)
        if r.status_code == 404:
            pendientes_contabilizar.append(dte)
    
    for doc in pendientes_contabilizar:
        print(f"  {doc['emisor'][:25]:<25} | Folio {doc['folio']:<8} | ${doc['montoTotal']:,.0f}")
    
    total = sum(d['montoTotal'] for d in pendientes_contabilizar)
    print(f"  TOTAL: {len(pendientes_contabilizar)} documentos = ${total:,.0f}")

if __name__ == '__main__':
    control_pendientes()
```

---

*Documentación generada: 2025-12-21*

