-- ==============================================================================
-- Proyecto: Optimización de Engagement Regional - Yelp Dataset
-- Objetivo: Identificar clústeres geográficos de alta rentabilidad cruzando 
--           calificaciones de negocios con el estatus "Elite" de los usuarios.
-- ==============================================================================

-- Paso 1: Creación de la tabla maestra con CTE para optimizar memoria
WITH master_data AS (
    SELECT 
        b.business_id,
        b.city,
        b.stars AS business_rating,
        b.review_count AS business_reviews,
        r.stars AS user_rating,
        u.elite,
        u.fans
    FROM business b
    -- Inner joins para cruzar las tablas principales
    INNER JOIN review r ON b.business_id = r.business_id
    INNER JOIN user u ON r.user_id = u.user_id
    -- Filtro de negocio: Solo evaluar negocios actualmente operativos
    WHERE b.is_open = 1
)

-- Paso 2: Agrupación regional y cálculo de KPIs
SELECT 
    city,
    COUNT(business_id) AS interacciones_totales,
    AVG(business_rating) AS rating_promedio_negocio,
    -- Cálculo del porcentaje de usuarios Elite por ciudad
    ROUND(SUM(CASE WHEN elite != 'None' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS porcentaje_elite,
    AVG(fans) AS promedio_fans_por_usuario
FROM master_data
GROUP BY city
-- Filtrar ciudades con volumen representativo para evitar sesgos de muestra pequeña
HAVING interacciones_totales > 1000
ORDER BY interacciones_totales DESC
LIMIT 15;
