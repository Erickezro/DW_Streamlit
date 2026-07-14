"""Shared SQL helpers for fact-level filters."""

BASE_FROM = """
FROM Fact_Accidentes f
INNER JOIN Dim_Tiempo t
    ON f.id_tiempo = t.id_tiempo
INNER JOIN Dim_Ubicacion u
    ON f.id_ubicacion = u.id_ubicacion
INNER JOIN Dim_Clase c
    ON f.id_clase = c.id_clase
INNER JOIN Dim_Causa ca
    ON f.id_causa = ca.id_causa
"""


def construir_filtros(anio=None, provincias=None, cantones=None, clases=None, causas=None):

    filtros = []
    parametros = []

    if anio not in (None, "Todos"):
        filtros.append("t.anio = ?")
        parametros.append(anio)

    if provincias:
        filtros.append(f"u.provincia IN ({', '.join('?' for _ in provincias)})")
        parametros.extend(provincias)

    if cantones:
        filtros.append(f"u.canton IN ({', '.join('?' for _ in cantones)})")
        parametros.extend(cantones)

    if clases:
        filtros.append(f"c.clase IN ({', '.join('?' for _ in clases)})")
        parametros.extend(clases)

    if causas:
        filtros.append(f"ca.causa IN ({', '.join('?' for _ in causas)})")
        parametros.extend(causas)

    if filtros:
        return "WHERE " + " AND ".join(filtros), parametros

    return "", parametros