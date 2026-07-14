"""Consultas SQL para el dashboard."""

import sql.common_filters as common_filters


def query_kpis(anio=None, provincias=None, cantones=None, clases=None, causas=None):

    where_clause, parametros = common_filters.construir_filtros(anio, provincias, cantones, clases, causas)

    sql = f"""
SELECT
    SUM(f.total_accidentes) AS accidentes,
    SUM(f.num_fallecido) AS fallecidos,
    SUM(f.num_lesionado) AS lesionados,
    SUM(f.total_victimas) AS victimas
{common_filters.BASE_FROM}
{where_clause}
"""

    return sql, parametros


def query_accidentes_por_anio(anio=None, provincias=None, cantones=None, clases=None, causas=None):

    where_clause, parametros = common_filters.construir_filtros(anio, provincias, cantones, clases, causas)

    sql = f"""
SELECT
    t.anio,
    SUM(f.total_accidentes) AS accidentes
{common_filters.BASE_FROM}
{where_clause}
GROUP BY t.anio
ORDER BY t.anio
"""

    return sql, parametros


def query_top_provincias(anio=None, provincias=None, cantones=None, clases=None, causas=None):

    where_clause, parametros = common_filters.construir_filtros(anio, provincias, cantones, clases, causas)

    sql = f"""
SELECT TOP 10
    u.provincia,
    SUM(f.total_accidentes) AS accidentes
{common_filters.BASE_FROM}
{where_clause}
GROUP BY u.provincia
ORDER BY accidentes DESC
"""

    return sql, parametros


def query_top_causas(anio=None, provincias=None, cantones=None, clases=None, causas=None):

    where_clause, parametros = common_filters.construir_filtros(anio, provincias, cantones, clases, causas)

    sql = f"""
SELECT TOP 10
    ca.causa,
    SUM(f.total_accidentes) AS accidentes
{common_filters.BASE_FROM}
{where_clause}
GROUP BY ca.causa
ORDER BY accidentes DESC
"""

    return sql, parametros


def query_accidentes_por_clase(anio=None, provincias=None, cantones=None, clases=None, causas=None):

    where_clause, parametros = common_filters.construir_filtros(anio, provincias, cantones, clases, causas)

    sql = f"""
SELECT
    c.clase,
    SUM(f.total_accidentes) AS accidentes
{common_filters.BASE_FROM}
{where_clause}
GROUP BY c.clase
ORDER BY accidentes DESC
"""

    return sql, parametros


def query_accidentes_por_zona(anio=None, provincias=None, cantones=None, clases=None, causas=None):

    where_clause, parametros = common_filters.construir_filtros(anio, provincias, cantones, clases, causas)

    sql = f"""
SELECT
    u.zona,
    SUM(f.total_accidentes) AS accidentes
{common_filters.BASE_FROM}
{where_clause}
GROUP BY u.zona
ORDER BY accidentes DESC
"""

    return sql, parametros


def query_cantones_disponibles(provincias=None, anio=None):

    where_clause, parametros = common_filters.construir_filtros(anio=anio, provincias=provincias)

    sql = f"""
SELECT DISTINCT u.canton
{common_filters.BASE_FROM}
{where_clause}
ORDER BY u.canton
"""

    return sql, parametros


ANIOS_DISPONIBLES = """
SELECT DISTINCT t.anio
FROM Fact_Accidentes f
INNER JOIN Dim_Tiempo t
    ON f.id_tiempo = t.id_tiempo
ORDER BY t.anio
"""


PROVINCIAS_DISPONIBLES = """
SELECT DISTINCT u.provincia
FROM Fact_Accidentes f
INNER JOIN Dim_Ubicacion u
    ON f.id_ubicacion = u.id_ubicacion
ORDER BY u.provincia
"""


CANTONES_DISPONIBLES = """
SELECT DISTINCT u.canton
FROM Fact_Accidentes f
INNER JOIN Dim_Ubicacion u
    ON f.id_ubicacion = u.id_ubicacion
ORDER BY u.canton
"""


CLASES_DISPONIBLES = """
SELECT DISTINCT c.clase
FROM Fact_Accidentes f
INNER JOIN Dim_Clase c
    ON f.id_clase = c.id_clase
ORDER BY c.clase
"""


CAUSAS_DISPONIBLES = """
SELECT DISTINCT ca.causa
FROM Fact_Accidentes f
INNER JOIN Dim_Causa ca
    ON f.id_causa = ca.id_causa
ORDER BY ca.causa
"""