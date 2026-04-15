# 🛒 Auditoría de Datos y Embudo de Conversión para E-commerce

**Rol:** Data Analyst  
**Herramientas:** SQL  
**Objetivo:** Diagnosticar la salud del inventario y medir las tasas de conversión de usuarios desde el registro hasta la compra final.

## 🚀 El Problema del Cliente
Las tiendas online suelen tener bases de datos saturadas con "ítems de prueba" generados por los desarrolladores, lo que ensucia los reportes de ventas. Además, es vital saber exactamente en qué punto de la navegación se están perdiendo los clientes para poder lanzar campañas de marketing efectivas.

## 🛠️ Solución Técnica Implementada
1. **Saneamiento de Base de Datos:** Utilización de CTEs (Common Table Expressions) y cláusulas lógicas (`CASE WHEN`, `IS NOT NULL`) para aislar los productos reales de la "basura" del sistema.
2. **Segmentación Dinámica:** Creación de reglas de negocio en SQL para clasificar automáticamente el inventario en "Bajo Costo", "Ticket Medio" y "Ticket Premium".
3. **Funnel de Ventas (Métricas de Conversión):** Uso avanzado de `COUNT(DISTINCT)` y `LEFT JOIN` a través de múltiples tablas (Usuarios, Eventos, Órdenes) para calcular la *Tasa de Activación* y la *Tasa de Conversión Final*.

## 💡 Impacto Comercial
Con estas consultas, el dueño del negocio obtiene una radiografía exacta en segundos: sabe cuánto inventario real tiene disponible y entiende exactamente qué porcentaje de sus usuarios registrados realmente están dejando dinero en la empresa.
