"""Consultas SQL para el análisis geográfico."""

import sql.common_filters as common_filters

# ==========================
# Provincias (para dropdown de selección)
# ==========================

PROVINCIAS = """
SELECT DISTINCT
    provincia
FROM Dim_Ubicacion
ORDER BY provincia
"""


def query_accidentes_por_provincia(anio=None, provincias=None, cantones=None, clases=None, causas=None):
    """Consulta para obtener accidentes agrupados por provincia con filtros comunes."""
    where_clause, parametros = common_filters.construir_filtros(
        anio=anio,
        provincias=provincias,
        cantones=cantones,
        clases=clases,
        causas=causas
    )

    sql = f"""
SELECT
    u.provincia,
    SUM(f.total_accidentes) AS accidentes
{common_filters.BASE_FROM}
{where_clause}
GROUP BY u.provincia
ORDER BY accidentes DESC
"""
    return sql, parametros


def query_resumen_provincia(provincia, anio=None, cantones=None, clases=None, causas=None):
    """Consulta para obtener el resumen de KPIs de una provincia específica con filtros comunes."""
    where_clause, parametros = common_filters.construir_filtros(
        anio=anio,
        provincias=[provincia],
        cantones=cantones,
        clases=clases,
        causas=causas
    )

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


def query_accidentes_por_canton(provincia, anio=None, cantones=None, clases=None, causas=None):
    """Consulta para obtener accidentes agrupados por cantón de una provincia específica con filtros comunes."""
    where_clause, parametros = common_filters.construir_filtros(
        anio=anio,
        provincias=[provincia],
        cantones=cantones,
        clases=clases,
        causas=causas
    )

    sql = f"""
SELECT
    u.canton,
    SUM(f.total_accidentes) AS accidentes
{common_filters.BASE_FROM}
{where_clause}
GROUP BY u.canton
ORDER BY accidentes DESC
"""
    return sql, parametros


def query_accidentes_por_zona(provincia, anio=None, cantones=None, clases=None, causas=None):
    """Consulta para obtener accidentes agrupados por zona de una provincia específica con filtros comunes."""
    where_clause, parametros = common_filters.construir_filtros(
        anio=anio,
        provincias=[provincia],
        cantones=cantones,
        clases=clases,
        causas=causas
    )

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
