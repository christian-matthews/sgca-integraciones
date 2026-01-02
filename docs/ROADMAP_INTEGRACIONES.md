# Roadmap de Integraciones SGCA

> Versión 1.0 - 2 Enero 2026

---

## Estado Actual

| Fuente | Tipo | Empresas | Estado |
|--------|------|----------|--------|
| **Skualo** | API REST | FIDI, CISITEL, Wingman | ✅ Producción |
| **Odoo** | PostgreSQL directo | FactorIT SpA, FactorIT Ltda | ✅ Producción |
| **Fintoc** | API REST | - | 🔜 Pendiente |
| **SII** | Portal + API | - | 🔜 Pendiente |
| **Clay** | API REST | - | 🔜 Pendiente |
| **Transtecnia** | ¿API? ¿Export? | - | 🔍 Investigando |

---

## 🔧 1. Mejorar Reporte ODOO

### ✅ RESUELTO - 2 Enero 2026

### Problema Original

Los pendientes SII incluían documentos antiguos (> 8 días) que ya fueron aceptados tácitamente por el SII, inflando el contador de "pendientes".

### Solución Implementada

Se separaron los documentos SII en dos grupos:

| Grupo | Criterio | Activa SLA | Uso |
|-------|----------|------------|-----|
| **Accionables** | `< 8 días` desde fecha doc | ✅ Sí | Trabajo pendiente real |
| **Tácitos sin revisar** | `>= 8 días` en estado draft | ❌ No | Auditoría / Finding de control |

### Archivos Modificados

1. **`odoo/pendientes.py`**
   - Agregada constante `SII_DIAS_ACEPTACION_TACITA = 8`
   - Query separa documentos en `accionables` y `tacitos_sin_revisar`
   - Cada tácito incluye `dias_sin_revisar` para contexto

2. **`bridge/sync_odoo_to_checks.py`**
   - `sii_count` en snapshot = solo accionables (activa SLA)
   - `raw.sii_tacitos` = cantidad de tácitos (auditoría)
   - `raw.sii_tacitos_monto` = monto total de tácitos

### Estructura JSON Resultante

```json
{
  "pendientes_sii": {
    "cantidad": 12,           // Total (compatibilidad)
    "total": 22645090,
    
    "accionables": {
      "cantidad": 4,          // Requieren acción real
      "total": 1000000,
      "documentos": [...]
    },
    
    "tacitos_sin_revisar": {
      "cantidad": 8,          // Aceptados por SII sin revisar
      "total": 21645090,
      "documentos": [
        {
          "id": 123,
          "fecha": "2025-07-17",
          "dias_sin_revisar": 169,  // Días desde la fecha del doc
          ...
        }
      ]
    }
  }
}
```

### Impacto en SGCA

```
erp_backlog_snapshots.sii_count = SOLO accionables
                                ↓
v_company_sla_realtime detecta breach si sii_count > 0
                                ↓
SLA_BREACH finding se crea solo por accionables
                                ↓
Documentos tácitos NO activan SLA (correcto)
```

### Queries Finales

| Pendiente | Tabla | Criterio |
|-----------|-------|----------|
| **SII Accionables** | `mail_message_dte_document` | `state = 'draft' AND date >= today - 8 days` |
| **SII Tácitos** | `mail_message_dte_document` | `state = 'draft' AND date < today - 8 days` |
| **Conciliar** | `account_bank_statement_line` | `NOT EXISTS (SELECT 1 FROM account_move_line WHERE statement_line_id = abl.id)` ✅ |
| **Contabilizar** | `account_move` | `state = 'draft'` |

---

## 🔧 2. Corregir Query Conciliación

### ✅ RESUELTO - 2 Enero 2026

### Problema Original

La query contaba TODOS los movimientos en extractos abiertos (169), cuando Odoo solo mostraba 14 pendientes.

### Causa

El criterio `extracto.state = 'open'` incluía movimientos ya conciliados dentro de extractos aún abiertos.

### Solución

El criterio correcto es verificar si el movimiento tiene un `account_move_line` asociado:

```sql
-- ANTES (incorrecto): 169 movimientos
WHERE abs.state = 'open'

-- AHORA (correcto): 21 movimientos (14 BCI Pesos + 7 otros)
WHERE NOT EXISTS (
    SELECT 1 FROM account_move_line aml 
    WHERE aml.statement_line_id = abl.id
)
```

### Resultado

| Empresa | Antes | Ahora |
|---------|-------|-------|
| FactorIT SpA | 169 | **21** ✅ |
| FactorIT Ltda | 15 | **4** ✅ |
| **Total** | 184 | **25** |

---

## 🏦 2. Integrar Fintoc

> **📚 Documentación completa**: [`docs/FINTOC_API_BIBLIA.md`](./FINTOC_API_BIBLIA.md)

### ¿Qué es Fintoc?

API bancaria chilena para:
- Obtener saldos de cuentas
- Obtener movimientos bancarios
- Acceso a DTEs SII (via widget)
- Iniciación de pagos

### Valor para SGCA

| Caso de Uso | Beneficio |
|-------------|-----------|
| **Conciliación automática** | Movimientos en tiempo real vs ERP |
| **Detección de pagos** | Previred, F29, Remuneraciones |
| **Validación SII** | Segunda fuente independiente |

### Limitación Principal

⚠️ **Requiere acción del usuario**: El usuario debe autenticarse via Widget Fintoc. No es 100% automático.

### Comparación con Clay

| Criterio | Fintoc | Clay |
|----------|--------|------|
| **SII** | ✅ Via widget | ✅ Automático |
| **Bancos** | ✅ Múltiples | ⚠️ Limitado |
| **Automatización** | ⚠️ Requiere widget | ✅ Completa |
| **Costo** | Por transacción | Por empresa/mes |

### Arquitectura Propuesta

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Fintoc    │ ──► │   Bridge    │ ──► │ Supabase    │
│   API       │     │   fintoc/   │     │ erp_backlog │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Próximos Pasos

1. [ ] Crear cuenta Fintoc (dev/sandbox)
2. [x] Documentar API → `docs/FINTOC_API_BIBLIA.md`
3. [ ] Definir qué datos sincronizar
4. [ ] Vincular primera empresa de prueba

---

## 🇨🇱 3. Integrar SII

### ¿Qué es SII?

Servicio de Impuestos Internos de Chile. Portal para:
- DTEs recibidos/emitidos
- Estado de aceptación/rechazo
- Declaraciones (F29, etc.)

### Opciones de Integración

| Método | Pros | Contras |
|--------|------|---------|
| **API MiPyme** | Oficial, estable | Solo para MiPymes |
| **Scraping portal** | Universal | Frágil, requiere credenciales |
| **Proveedores terceros** | Simple | Costo adicional |
| **Facturador electrónico** | Ya tienen integración | Depende del proveedor |

### Valor para SGCA

| Caso de Uso | Beneficio |
|-------------|-----------|
| **DTEs recibidos** | Fuente de verdad para facturas por aprobar |
| **Estado de DTEs** | Saber si ya fue aceptado/rechazado |
| **F29** | Verificar declaración y pago |

### Preguntas a Resolver

1. **¿Qué facturador usan las empresas?**
   - Acepta, Nubox, Bsale, otro?
   
2. **¿Tienen acceso a API SII MiPyme?**
   - Solo aplica para empresas pequeñas

3. **¿Preferencia scraping vs tercero?**
   - Scraping es gratis pero frágil
   - Tercero (ej: Nubox API) tiene costo

### Próximos Pasos

1. [ ] Identificar facturador de cada empresa
2. [ ] Evaluar si tienen API disponible
3. [ ] Si no, evaluar scraping con autenticación

---

## 🧩 4. Integrar Clay

### ¿Qué es Clay?

ERP chileno con API REST documentada: [https://api.clay.cl/docs](https://api.clay.cl/docs)

### Características (a explorar en docs)

- API REST moderna
- Autenticación por token (probablemente)
- Endpoints para: ¿Contabilidad? ¿Bancos? ¿DTEs?

### Preguntas a Resolver

1. **¿Qué empresas usan Clay?**
   - Identificar clientes actuales o futuros

2. **¿Qué módulos tiene la API?**
   - Revisar docs en detalle
   
3. **¿Es similar a Skualo?**
   - Si es similar, podemos reutilizar estructura

### Próximos Pasos

1. [ ] Revisar documentación API en detalle
2. [ ] Identificar endpoints equivalentes a Skualo
3. [ ] Crear módulo `clay/` similar a `skualo/`

---

## 🔀 Análisis: Clay como Hub vs Integraciones Directas

### Qué ofrece Clay

Según [clay.cl](https://www.clay.cl/apis-bancarias-y-sii):

| Módulo | Funcionalidad |
|--------|---------------|
| **SII** | Importa DTEs automáticamente (facturas, boletas) |
| **Bancos** | Descarga cartolas y movimientos automáticamente |
| **Contabilidad** | ERP completo |

### Comparación de Enfoques

| Aspecto | Clay como Hub | Integraciones Directas |
|---------|---------------|------------------------|
| **Complejidad inicial** | 🟢 Baja (1 API) | 🔴 Alta (SII + Fintoc + N) |
| **Mantenimiento** | 🟢 Clay lo mantiene | 🔴 Nosotros mantenemos |
| **Costo** | 🟡 Suscripción Clay | 🟢 Solo desarrollo |
| **Independencia** | 🔴 Dependemos de Clay | 🟢 Control total |
| **Cobertura bancos** | 🟡 Los que Clay soporte | 🟢 Fintoc tiene más bancos |
| **Datos SII** | 🟡 Lo que Clay exponga | 🟢 Acceso completo |

### Escenarios de Uso

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESCENARIO A: CLAY COMO HUB                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Empresa Nueva ──► Clay ──► API Clay ──► SGCA                  │
│                      │                                          │
│                      ├── SII (DTEs)                             │
│                      └── Bancos (movimientos)                   │
│                                                                 │
│   Pros: Simple, rápido                                          │
│   Contras: Solo empresas con Clay                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              ESCENARIO B: INTEGRACIONES DIRECTAS                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Empresa ──┬── SII Directo ──► SGCA                            │
│             ├── Fintoc ────────► SGCA                           │
│             └── ERP (Odoo/Skualo/Clay) ──► SGCA                 │
│                                                                 │
│   Pros: Independiente, fuente de verdad                         │
│   Contras: Más complejo de mantener                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    ESCENARIO C: HÍBRIDO                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Empresas Clay ──► Clay API ──► SGCA                           │
│                                                                 │
│   Empresas Skualo ──► Skualo API ──► SGCA                       │
│                                                                 │
│   Empresas Odoo ──► Odoo PostgreSQL ──► SGCA                    │
│                                                                 │
│   Validación cruzada (futuro):                                  │
│   └── SII Directo para auditoría                                │
│   └── Fintoc para empresas sin carga bancaria                   │
│                                                                 │
│   Pros: Pragmático, escala por caso                             │
│   Contras: Múltiples conectores                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Recomendación

**Escenario C (Híbrido)** con esta prioridad:

1. **Clay** para empresas nuevas (ya tienen SII + Bancos)
2. **SII Directo** como proyecto futuro de auditoría
3. **Fintoc** solo para casos específicos (empresas sin carga bancaria)

---

## 📋 Resumen de Decisiones

| # | Decisión | Resolución |
|---|----------|------------|
| 1 | Criterio "por contabilizar" Odoo | Por validar con datos reales |
| 2 | Clay como hub para nuevas empresas | ✅ Sí |
| 3 | SII Directo | Futuro, para auditoría/independencia |
| 4 | Fintoc | Solo casos específicos |

---

## 🗓️ Secuencia Definitiva (Enfoque Híbrido)

```
FASE 1: ESTABILIZAR (Semana 1)
├── [P0] Corregir queries Odoo
│   └── Validar: SII, contabilizar, conciliar
└── [P1] Verificar Skualo (ya funciona)

FASE 2: CLAY (Semana 2-3)
├── [P0] Crear cuenta Clay developer
├── [P1] Explorar API Clay (docs)
├── [P2] Crear módulo clay/ (similar a skualo/)
└── [P3] Primera empresa en Clay → SGCA

FASE 3: FUTURO (Q2 2026+)
├── [ ] SII Directo (auditoría/independencia)
└── [ ] Fintoc (casos sin carga bancaria)
```

### Estado de Cada Integración

| Integración | Estado | Acción |
|-------------|--------|--------|
| **Odoo** | 🟡 Revisar | Corregir queries esta semana |
| **Skualo** | ✅ Producción | Mantener |
| **Clay** | 🔜 Iniciar | Semana 2 |
| **SII Directo** | 📋 Backlog | Q2 2026 |
| **Fintoc** | 📋 Backlog | Solo si necesario |

---

## Notas

- **Fintoc** parece el más fácil de integrar (API moderna, buena documentación)
- **SII** es crítico para los SLAs de aceptación
- **Odoo** es urgente si los números están mal

---

*Documento vivo - actualizar según avancemos*
