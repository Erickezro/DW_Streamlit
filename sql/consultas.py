"""
Consultas dinámicas OLAP
"""

CONSULTA_OLAP = """

SELECT

{dimension} AS categoria,

SUM(f.{metrica}) AS valor

{base_from}

{where_clause}

GROUP BY {dimension}

ORDER BY valor DESC

"""