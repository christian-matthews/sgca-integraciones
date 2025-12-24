# Proceso para Obtener Pendientes via API Skualo

## Lógica General

La API de Skualo está diseñada para **consultar** información, no para realizar acciones.
Para identificar pendientes, debemos consultar diferentes endpoints y aplicar lógica de negocio.

---

## 1. Pendientes por Aceptar en SII

### Endpoint
```
GET /{RUT}/sii/dte/recibidos
```

### Lógica
```python
# Obtener todos los DTEs recibidos (paginar si hay más de 100)
for page in range(1, 10):
    GET /{RUT}/sii/dte/recibidos?PageSize=100&Page={page}

# Filtrar pendientes:
pendientes = [d for d in dtes if 
    d['conAcuseRecibo'] == False and 
    d['fechaRespuesta'] == None
]
```

### Filtros útiles (sintaxis OData)
```
# Por emisor específico
?search=RutEmisor eq 96945440-8

# Por tipo de documento
?search=idTipoDocumento eq 33
```

---

## 2. Pendientes por Contabilizar

### Endpoints
```
GET /{RUT}/sii/dte/recibidos                           # DTEs aceptados
GET /{RUT}/contabilidad/reportes/librocompras/{periodo}  # Ya contabilizados
```

### Lógica
```python
# 1. Obtener DTEs aceptados del período
dtes_aceptados = [d for d in dtes_recibidos if d['conAcuseRecibo'] == True]
dtes_mes = [d for d in dtes_aceptados if d['fechaEmision'].startswith('2025-12')]

# 2. Obtener folios ya contabilizados
libro = GET /{RUT}/contabilidad/reportes/librocompras/202512
folios_contabilizados = set(item['NumDoc'] for item in libro)

# 3. Identificar pendientes
pendientes = [d for d in dtes_mes if d['folio'] not in folios_contabilizados]
```

---

## 3. Pendientes de Conciliar (Movimientos Bancarios)

### ⚠️ IMPORTANTE: Identificar cuentas de banco dinámicamente

Las cuentas de banco pueden variar entre empresas. **NO asumir códigos fijos.**

### Proceso correcto:

#### Paso 1: Obtener plan de cuentas desde el balance
```
GET /{RUT}/contabilidad/reportes/balancetributario/{periodo}
```

#### Paso 2: Identificar cuentas de banco
```python
# Criterios para identificar cuentas de banco:

def es_cuenta_banco(cuenta):
    codigo = cuenta['idCuenta']
    nombre = cuenta['cuenta'].lower()
    
    # Por código (típicamente 1102xxx para activos corrientes - bancos)
    if codigo.startswith('1102'):
        return True
    
    # Por nombre
    bancos_conocidos = [
        'banco', 'bci', 'santander', 'chile', 'estado',
        'scotiabank', 'itau', 'security', 'corpbanca',
        'falabella', 'ripley', 'consorcio', 'bice'
    ]
    
    for banco in bancos_conocidos:
        if banco in nombre:
            return True
    
    return False

# Obtener cuentas de banco
cuentas_banco = [c for c in balance if es_cuenta_banco(c)]
```

#### Paso 3: Obtener libro mayor de cada cuenta de banco
```
GET /{RUT}/contabilidad/reportes/libromayor
    ?IdCuentaInicio={codigo}
    &IdCuentaFin={codigo}
    &desde=2025-12-01
    &hasta=2025-12-31
    &IdSucursal=0
```

#### Paso 4: Identificar movimientos no conciliados
```python
# En el libro mayor, identificar movimientos sin conciliar
# Criterios posibles:
# - Campo 'conciliado' = false (si existe)
# - Movimientos sin documento asociado
# - Movimientos con glosa específica

# Estructura típica de movimiento:
{
    "fecha": "2025-12-15",
    "idCuenta": "1102007",
    "cuenta": "Banco Itau",
    "montoDebe": 500000,
    "montoHaber": 0,
    "glosa": "Depósito cliente",
    "comprobante": 1234
}
```

### Alternativa: Endpoint /bancos (si está disponible)
```
GET /{RUT}/bancos              # Listar cuentas
GET /{RUT}/bancos/{cuentaId}   # Obtener movimientos

# Filtrar: conciliado == false
```

> ⚠️ Este endpoint puede no estar disponible para todos los tenants.
> Si devuelve 404 "Tenant Not Found", usar el método del libro mayor.

---

## Códigos de Cuenta Típicos en Chile

| Rango | Descripción |
|-------|-------------|
| 1101xxx | Caja |
| 1102xxx | **Bancos** |
| 1103xxx | Inversiones corto plazo |
| 1104xxx | Cuentas por cobrar |
| 2101xxx | Proveedores |
| 2102xxx | Préstamos bancarios (pasivo) |

---

## Ejemplo Completo: Script de Pendientes

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('SKUALO_API_TOKEN')
BASE_URL = 'https://api.skualo.cl'
RUT = '77285645-8'

headers = {
    'Authorization': f'Bearer {token}',
    'accept': 'application/json'
}

def obtener_pendientes_completo():
    resultado = {
        'pendientes_sii': [],
        'pendientes_contabilizar': [],
        'pendientes_conciliar': []
    }
    
    # 1. Pendientes SII
    resp = requests.get(f'{BASE_URL}/{RUT}/sii/dte/recibidos', headers=headers)
    dtes = resp.json().get('items', [])
    resultado['pendientes_sii'] = [
        d for d in dtes 
        if not d.get('conAcuseRecibo', True)
    ]
    
    # 2. Pendientes Contabilizar
    # ... (comparar con libro de compras)
    
    # 3. Pendientes Conciliar
    # Paso 3.1: Obtener balance para identificar cuentas de banco
    periodo = '202512'
    resp = requests.get(
        f'{BASE_URL}/{RUT}/contabilidad/reportes/balancetributario/{periodo}',
        headers=headers
    )
    balance = resp.json().get('items', [])
    
    # Paso 3.2: Identificar cuentas de banco
    cuentas_banco = [
        c for c in balance 
        if c['idCuenta'].startswith('1102') or 'banco' in c['cuenta'].lower()
    ]
    
    # Paso 3.3: Para cada cuenta, obtener libro mayor
    for cuenta in cuentas_banco:
        codigo = cuenta['idCuenta']
        url = f'{BASE_URL}/{RUT}/contabilidad/reportes/libromayor'
        params = {
            'IdCuentaInicio': codigo,
            'IdCuentaFin': codigo,
            'desde': '2025-12-01',
            'hasta': '2025-12-31',
            'IdSucursal': 0
        }
        resp = requests.get(url, headers=headers, params=params)
        movimientos = resp.json().get('items', [])
        
        # Agregar a pendientes (aquí aplicar lógica de conciliación)
        resultado['pendientes_conciliar'].extend(movimientos)
    
    return resultado
```

---

## Resumen de Endpoints

| Propósito | Endpoint |
|-----------|----------|
| DTEs recibidos | `GET /sii/dte/recibidos` |
| Filtrar por emisor | `GET /sii/dte/recibidos?search=RutEmisor eq X` |
| Libro de compras | `GET /contabilidad/reportes/librocompras/{periodo}` |
| Balance tributario | `GET /contabilidad/reportes/balancetributario/{periodo}` |
| Libro mayor | `GET /contabilidad/reportes/libromayor?IdCuentaInicio=X&IdCuentaFin=X&desde=X&hasta=X` |
| Bancos (si disponible) | `GET /bancos/{cuentaId}` |

