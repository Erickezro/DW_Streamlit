"""Consultas SQL para el análisis temporal."""

import sql.common_filters as common_filters


ANIOS = """
SELECT DISTINCT
    anio
FROM Dim_Tiempo
ORDER BY anio
"""


def query_accidentes_por_mes(anio=None, provincias=None, cantones=None, clases=None, causas=None):

    where_clause, parametros = common_filters.construir_filtros(anio, provincias, cantones, clases, causas)

    sql = f"""
SELECT
    t.cod_mes,
    t.mes,
    SUM(f.total_accidentes) AS accidentes
{common_filters.BASE_FROM}
{where_clause}
GROUP BY
    t.cod_mes,
    t.mes
ORDER BY t.cod_mes
"""

    return sql, parametros


def query_accidentes_por_dia(anio=None, provincias=None, cantones=None, clases=None, causas=None):

    where_clause, parametros = common_filters.construir_filtros(anio, provincias, cantones, clases, causas)

    sql = f"""
SELECT
    t.cod_dia,
    t.dia,
    SUM(f.total_accidentes) AS accidentes
{common_filters.BASE_FROM}
{where_clause}
GROUP BY
    t.cod_dia,
    t.dia
ORDER BY t.cod_dia
"""

    return sql, parametros


def query_accidentes_por_hora(anio=None, provincias=None, cantones=None, clases=None, causas=None):

    where_clause, parametros = common_filters.construir_filtros(anio, provincias, cantones, clases, causas)

    sql = f"""
SELECT
    t.cod_hora,
    t.hora,
    SUM(f.total_accidentes) AS accidentes
{common_filters.BASE_FROM}
{where_clause}
GROUP BY
    t.cod_hora,
    t.hora
ORDER BY t.cod_hora
"""

    return sql, parametros