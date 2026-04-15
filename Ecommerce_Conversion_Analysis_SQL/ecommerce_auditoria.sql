-- ==============================================================================
-- Proyecto: Auditoría de Inventario y Embudo de Conversión (E-commerce)
-- Objetivo: Limpiar la base de datos de productos eliminando datos de prueba, 
--           y construir un Funnel de Ventas para medir la retención de clientes.
-- ==============================================================================

-- PASO 1: Limpieza de Inventario y Creación de Vista Maestra (CTEs)
-- Los sistemas de e-commerce suelen estar sucios con productos de prueba. 
-- Aquí normalizamos la data antes de analizar.
WITH item_limpios AS (
    SELECT 
        id AS item_id,
        category AS categoria,
        material,
        availability AS disponibilidad,
        list_price AS precio,
        display_name AS nombre,
        -- Segmentación de inventario para estrategias de marketing
        CASE 
            WHEN list_price < 50 THEN 'Bajo Costo'
            WHEN list_price BETWEEN 50 AND 150 THEN 'Ticket Medio'
            ELSE 'Ticket Premium' 
        END AS segmento_precio
    FROM items
    -- Filtros de calidad de datos: eliminando basura del sistema
    WHERE availability != 'TEST' 
      AND (is_test_item != 'VERDADERO' OR is_test_item IS NULL)
      AND list_price IS NOT NULL
)

-- PASO 2: Diagnóstico de Salud del Inventario
-- ¿Qué porcentaje de nuestro catálogo real está listo para venderse?
SELECT 
    COUNT(item_id) AS total_items_reales,
    SUM(CASE WHEN disponibilidad = 'Available' THEN 1 ELSE 0 END) AS items_disponibles,
    ROUND(SUM(CASE WHEN disponibilidad = 'Available' THEN 1 ELSE 0 END) * 100.0 / COUNT(item_id), 2) AS porcentaje_disponibilidad
FROM item_limpios;

-- PASO 3: Análisis de Embudo de Conversión de Usuarios (Funnel)
-- KPI Crítico: ¿Dónde estamos perdiendo a los usuarios? 
-- Desde que se registran, hasta que interactúan, hasta que finalmente compran.
SELECT 
    COUNT(DISTINCT u.id) AS total_registrados,
    COUNT(DISTINCT e.user_id) AS usuarios_con_actividad,
    COUNT(DISTINCT o.user_id) AS usuarios_con_compras,
    
    -- Tasa de Activación (% de registrados que hacen algo en la web)
    ROUND(COUNT(DISTINCT e.user_id) * 100.0 / COUNT(DISTINCT u.id), 2) AS tasa_activacion_pct,
    
    -- Tasa de Conversión Final (% de activos que terminan pagando)
    ROUND(COUNT(DISTINCT o.user_id) * 100.0 / COUNT(DISTINCT e.user_id), 2) AS tasa_conversion_ventas_pct
FROM users u
LEFT JOIN events e ON u.id = e.user_id
LEFT JOIN orders o ON u.id = o.user_id;
