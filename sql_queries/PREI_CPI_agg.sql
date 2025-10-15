SELECT 
    CASE 
        WHEN "estado_c_r_" IS NULL THEN 'Grand Total'
        ELSE "estado_c_r_"
    END AS estado,
    SUM(importe) AS total_importe
FROM eseotres_warehouse.altas_historicas
WHERE 
    file_date = (SELECT MAX(file_date) FROM eseotres_warehouse.altas_historicas)
    AND fechaaltatrunc::date >= '2025-06-30'::date
GROUP BY 
    ROLLUP("estado_c_r_")
ORDER BY 
    CASE 
        WHEN "estado_c_r_" = 'Sin Contra Recibo' THEN 1
        WHEN "estado_c_r_" = 'Pagado' THEN 2
        WHEN "estado_c_r_" IS NULL THEN 99
        ELSE 50
    END;
