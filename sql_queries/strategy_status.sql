SELECT 
    CASE 
        WHEN DATE_TRUNC('month', fechaaltatrunc) IS NULL THEN '  Grand Total'
        ELSE TO_CHAR(DATE_TRUNC('month', fechaaltatrunc), 'Mon')
    END AS mes_del_alta,
    CASE 
        WHEN modified_estado IS NULL AND DATE_TRUNC('month', fechaaltatrunc) IS NULL THEN ''
        WHEN modified_estado IS NULL AND DATE_TRUNC('month', fechaaltatrunc) IS NOT NULL THEN '	  Subtotal'
        ELSE modified_estado
    END AS estado,
    TO_CHAR(SUM(importe), 'FM$999,999,999,990.00') AS total_importe
FROM (
    SELECT 
        fechaaltatrunc,
        importe,
        CASE 
            WHEN uuid = 'No localizado' THEN 'Por facturar'
            ELSE "estado_c_r_"
        END AS modified_estado
    FROM eseotres_warehouse.altas_historicas
    WHERE 
        file_date = (SELECT MAX(file_date) FROM eseotres_warehouse.altas_historicas)
        AND fechaaltatrunc::date >= '2025-06-30'::date
) subquery
GROUP BY 
    ROLLUP(DATE_TRUNC('month', fechaaltatrunc), modified_estado)
ORDER BY 
    DATE_TRUNC('month', fechaaltatrunc) ASC NULLS LAST,
    modified_estado ASC NULLS LAST;