# TRANSTECNIA API - Documentación SGCA

> **Estado:** 🔍 En Investigación  
> **Última actualización:** 2 Enero 2026

---

## 1. Información General

**Transtecnia** es una empresa chilena que provee soluciones de:
- Facturación Electrónica (DTE)
- Contabilidad Digital
- Libros Electrónicos
- Software Contable

**Sitio web:** [transtecnia.cl](https://transtecnia.cl)

---

## 2. Estado de la API

### ⚠️ API No Documentada Públicamente

A la fecha, **no existe documentación pública** de una API REST para Transtecnia.

**Opciones de integración conocidas:**
- Exportación manual de archivos (Excel, XML)
- Posible API privada para clientes enterprise
- Integración via archivos planos

---

## 3. Productos Principales

| Producto | Descripción | Potencial Integración |
|----------|-------------|----------------------|
| **Factura Electrónica** | Emisión/Recepción DTE | DTEs emitidos/recibidos |
| **Contabilidad Digital** | ERP Contable | Balance, Mayor, Diario |
| **Libros Electrónicos** | Libros SII | Compras, Ventas, Honorarios |
| **Remuneraciones** | Liquidaciones de sueldo | Provisiones, pagos |

---

## 4. Preguntas para Soporte Transtecnia

Contactar a: **soporteweb@transtecnia.cl**

### Preguntas a realizar:

1. **¿Existe una API REST para integración?**
   - Si existe, solicitar documentación
   - Credenciales de sandbox

2. **¿Qué métodos de exportación tienen?**
   - Formatos: JSON, XML, Excel, CSV
   - Automatización: ¿Se puede programar?

3. **¿Tienen webhooks o notificaciones?**
   - Eventos de nuevos documentos
   - Cambios de estado

4. **¿Cuál es el modelo de licenciamiento?**
   - Costo por API calls
   - Plan enterprise con integración

5. **¿Qué datos se pueden extraer?**
   - DTEs (emitidos/recibidos)
   - Balance, Mayor
   - Movimientos bancarios
   - Auxiliares (clientes/proveedores)

---

## 5. Alternativas de Integración

### Opción A: Exportación Manual
```
Usuario exporta → Archivo Excel/CSV → SGCA importa
```
- **Pros:** Simple, no requiere API
- **Contras:** Manual, no tiempo real

### Opción B: Base de Datos Directa
```
Transtecnia DB → Conexión SQL → SGCA
```
- **Pros:** Acceso completo
- **Contras:** Requiere permisos, posible on-premise

### Opción C: Scraping Portal
```
Login portal → Scraping → SGCA
```
- **Pros:** No requiere API oficial
- **Contras:** Frágil, mantenimiento alto

### Opción D: SII Directo
```
Ignorar Transtecnia → SII API → SGCA
```
- **Pros:** Fuente de verdad, independiente
- **Contras:** Solo DTEs, no contabilidad

---

## 6. Empresas SGCA que usan Transtecnia

| Empresa | Módulos | Estado |
|---------|---------|--------|
| (Pendiente de identificar) | - | - |

---

## 7. Próximos Pasos

1. [ ] Identificar qué empresas SGCA usan Transtecnia
2. [ ] Contactar soporte Transtecnia para info de API
3. [ ] Evaluar si existe API enterprise
4. [ ] Definir método de integración (API/Export/DB)
5. [ ] Crear módulo `transtecnia/` si procede

---

## 8. Comparación con Otros ERPs

| Aspecto | Skualo | Odoo | Transtecnia |
|---------|--------|------|-------------|
| API REST | ✅ Documentada | ❌ (PostgreSQL) | ❓ Desconocido |
| Webhooks | ✅ Sí | ❌ No | ❓ Desconocido |
| Acceso DB | ❌ No | ✅ Sí | ❓ Posible |
| Documentación | ✅ Pública | ✅ Pública | ❌ No pública |

---

## Contacto Soporte

- **Email:** soporteweb@transtecnia.cl
- **Portal:** [Centro de Asistencia](https://transtecniasoporte.zohodesk.com/portal/es/home)
- **Teléfono:** (Verificar en sitio web)

---

*Documento en desarrollo. Actualizar cuando se obtenga información de Transtecnia.*
